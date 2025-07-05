#!/usr/bin/env python3
"""
End-to-End Document Processing Workflow Demo

This script demonstrates the complete workflow:
1. Upload a file using file_upload service
2. Extract text using document_extractor
3. Chunk the text using text_chunking
4. Generate embeddings using Google service
5. Store in Milvus database with proper metadata conversion
6. Search for similar content

This addresses the data structure alignment issues between the services.
"""

import os
import sys
import tempfile
import asyncio
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.file_upload import file_upload_service
from src.services.document_extractor import document_extractor
from src.services.text_chunking import TextChunker, ChunkingStrategy, ChunkingConfig
from src.services.external_apis.google_service import get_google_service
from src.database.milvus_db import MilvusVectorDatabase
from src.database.config import (
    DocumentMetadata, ContentMetadata, OrganizationalMetadata,
    ContentTypeEnum, OrganizationTypeEnum, SecurityLevelEnum,
    ProcessingMetadata, DomainSpecificMetadata, ComplianceMetadata
)
from src.database.connection import get_db
from src.utils.logging import setup_logging
from src.models.metadata import FileMetadata, DocumentType, ContentCategory, EmployeeRole, PriorityLevel, AccessLevel

# Setup logging for this module
setup_logging()
logger = logging.getLogger(__name__)

# LangChain Document import for type hints
try:
    from langchain.schema import Document
except ImportError:
    Document = None

class MetadataConverter:
    """Converts between different metadata formats used in the workflow"""
    
    @staticmethod
    def file_metadata_to_document_metadata(
        file_metadata: FileMetadata,
        chunk_info: Dict[str, Any],
        processing_info: Dict[str, Any]
    ) -> DocumentMetadata:
        """Convert FileMetadata to DocumentMetadata for Milvus storage"""
        
        # Map file metadata to content metadata
        content_metadata = ContentMetadata(
            title=file_metadata.description or "Processed Document",
            author=file_metadata.uploaded_by,
            content_type=ContentTypeEnum.DOCUMENT,
            format=chunk_info.get("file_extension", "txt"),
            tags=file_metadata.tags or [],
            keywords=file_metadata.tags or [],
            description=file_metadata.description or "Processed document chunk"
        )
        
        # Map organizational metadata
        organizational_metadata = OrganizationalMetadata(
            department=file_metadata.department,
            role=file_metadata.employee_role,  # Already a string due to use_enum_values=True
            organization_type=OrganizationTypeEnum.HEALTHCARE,  # Default
            security_level=SecurityLevelEnum.INTERNAL,  # Default
            access_groups=[file_metadata.employee_role]  # Already a string
        )
        
        # Create processing metadata
        processing_metadata = ProcessingMetadata(
            api_used=processing_info.get("api_used", "google_embeddings"),
            confidence_score=processing_info.get("confidence_score", 1.0),
            model_version=processing_info.get("model_version", "text-embedding-004"),
            processing_duration=processing_info.get("processing_duration", 0.0)
        )
        
        # Domain-specific metadata
        domain_specific_metadata = DomainSpecificMetadata(
            priority=file_metadata.priority_level,  # Already a string due to use_enum_values=True
            status="processed",
            custom_fields={
                "chunk_index": chunk_info.get("chunk_index", 0),
                "total_chunks": chunk_info.get("total_chunks", 1),
                "start_index": chunk_info.get("start_index", 0),
                "end_index": chunk_info.get("end_index", 0),
                "chunk_text": chunk_info.get("chunk_text", "")[:500]  # Store preview
            }
        )
        
        # Compliance metadata
        compliance_metadata = ComplianceMetadata(
            anonymized=file_metadata.access_level == "public",  # Compare with string value
            approved_by=file_metadata.uploaded_by
        )
        
        return DocumentMetadata(
            organizational=organizational_metadata,
            content=content_metadata,
            processing=processing_metadata,
            domain_specific=domain_specific_metadata,
            compliance=compliance_metadata
        )

class EndToEndWorkflow:
    """Complete end-to-end document processing workflow"""
    
    def __init__(self, google_api_key: Optional[str] = None):
        self.text_chunker = TextChunker()
        self.google_service = get_google_service(api_key=google_api_key)
        self.milvus_db = MilvusVectorDatabase()
        self.metadata_converter = MetadataConverter()
        
        # Connect to Milvus
        if not self.milvus_db.connect():
            raise RuntimeError("Failed to connect to Milvus database")
        
        # Create collections
        if not self.milvus_db.create_all_collections():
            raise RuntimeError("Failed to create collections")
    
    async def process_file_end_to_end(
        self, 
        file_path: str, 
        filename: str = None,
        collection_name: str = "text_embeddings"
    ) -> Dict[str, Any]:
        """Process a file through the complete end-to-end workflow"""
        
        results = {
            "file_path": file_path,
            "stages": {},
            "milvus_ids": [],
            "chunks_processed": 0,
            "embeddings_generated": 0,
            "total_processing_time": 0.0
        }
        
        start_time = datetime.now()
        
        try:
            # Stage 1: Upload file
            logger.info(f"Stage 1: Uploading file {file_path}")
            upload_result = await self._upload_file(file_path, filename)
            results["stages"]["upload"] = upload_result
            
            # Stage 2: Extract text
            logger.info(f"Stage 2: Extracting text from {file_path}")
            extracted_text = self._extract_text(file_path)
            results["stages"]["extraction"] = {
                "text_length": len(extracted_text),
                "success": True
            }
            
            # Stage 3: Chunk text
            logger.info(f"Stage 3: Chunking extracted text")
            chunks = self._chunk_text(extracted_text)
            results["stages"]["chunking"] = {
                "chunk_count": len(chunks),
                "success": True
            }
            results["chunks_processed"] = len(chunks)
            
            # Stage 4: Process each chunk through embeddings and storage
            logger.info(f"Stage 4: Processing {len(chunks)} chunks through embeddings and storage")
            chunk_results = await self._process_chunks(
                chunks=chunks,
                file_metadata=upload_result.get("file_metadata"),
                collection_name=collection_name,
                file_path=file_path
            )
            results["stages"]["embedding_and_storage"] = chunk_results
            results["milvus_ids"] = chunk_results.get("milvus_ids", [])
            results["embeddings_generated"] = chunk_results.get("embeddings_generated", 0)
            
            # Calculate total processing time
            end_time = datetime.now()
            results["total_processing_time"] = (end_time - start_time).total_seconds()
            
            # Display results
            self._display_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in end-to-end workflow: {e}")
            results["error"] = str(e)
            raise
    
    async def search_similar_content(
        self, 
        query_text: str, 
        collection_name: str = "text_embeddings",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar content using the processed embeddings"""
        
        try:
            logger.info(f"Searching for similar content to: {query_text[:100]}...")
            
            # Generate query embeddings
            query_embeddings = self.google_service.generate_text_embeddings(query_text)
            if not query_embeddings:
                raise ValueError("Failed to generate query embeddings")
            
            # Search in Milvus
            results = self.milvus_db.vector_search(
                collection_name=collection_name,
                query_vector=query_embeddings[0],
                limit=limit
            )
            
            # Process and display results
            self._display_search_results(query_text, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    def read_stored_documents(
        self, 
        collection_name: str = "text_embeddings",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Read and display stored documents from the collection"""
        
        try:
            logger.info(f"Reading stored documents from collection: {collection_name}")
            
            # Get collection stats first
            stats = self.milvus_db.get_stats(collection_name)
            total_entities = stats.get("total_entities", 0)
            
            if total_entities == 0:
                print(f"\nNo documents found in collection '{collection_name}'")
                return []
            
            # Use metadata search to get all documents
            results = self.milvus_db.metadata_search(
                collection_name=collection_name,
                filter_expr="id != ''",  # Simple filter to get all documents
                limit=limit
            )
            
            # Display results
            self._display_stored_documents(results, collection_name, total_entities)
            
            return results
            
        except Exception as e:
            logger.error(f"Error reading stored documents: {e}")
            print(f"Error reading documents: {e}")
            return []
    
    async def _upload_file(self, file_path: str, filename: str = None) -> Dict[str, Any]:
        """Upload file using file_upload_service"""
        try:
            from fastapi import UploadFile
            from io import BytesIO
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Create upload file object
            upload_file = UploadFile(
                filename=filename or os.path.basename(file_path),
                file=BytesIO(file_content)
            )
            
            # Create file metadata
            file_metadata = FileMetadata(
                department="demo",
                uploaded_by="demo_user",
                employee_role=EmployeeRole.STAFF,
                document_type=DocumentType.OTHER,
                content_category=ContentCategory.OTHER,
                priority_level=PriorityLevel.LOW,
                access_level=AccessLevel.PUBLIC,
                description="Demo file for end-to-end workflow testing",
                tags=["demo", "end-to-end", "workflow"]
            )
            
            # Get database session
            db = next(get_db())
            
            # Upload file
            result = await file_upload_service.upload_file(
                file=upload_file,
                db=db,
                file_metadata=file_metadata
            )
            
            # Add file metadata to result for later use
            result["file_metadata"] = file_metadata
            
            return result
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text using document_extractor"""
        try:
            mime_type = self._get_mime_type(file_path)
            text = document_extractor.extract_text(file_path, mime_type)
            return text
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    def _chunk_text(self, text: str) -> List[Document]:
        """Chunk text using text_chunking service"""
        try:
            config = ChunkingConfig(
                chunk_size=500,
                chunk_overlap=50,
                add_start_index=True
            )
            
            chunks = self.text_chunker.chunk_text(
                text=text,
                strategy=ChunkingStrategy.RECURSIVE,
                config=config,
                metadata={"source": "end_to_end_demo"}
            )
            
            return chunks
        except Exception as e:
            logger.error(f"Text chunking failed: {e}")
            raise
    
    async def _process_chunks(
        self, 
        chunks: List[Document], 
        file_metadata: FileMetadata,
        collection_name: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Process chunks through embeddings and storage"""
        
        results = {
            "embeddings_generated": 0,
            "milvus_ids": [],
            "processing_times": [],
            "errors": []
        }
        
        for i, chunk in enumerate(chunks):
            try:
                chunk_start_time = datetime.now()
                
                # Generate embeddings for this chunk
                chunk_text = chunk.page_content
                embeddings = self.google_service.generate_text_embeddings(chunk_text)
                
                if not embeddings:
                    results["errors"].append(f"Failed to generate embeddings for chunk {i}")
                    continue
                
                results["embeddings_generated"] += 1
                
                # Prepare chunk info for metadata conversion
                chunk_info = {
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "start_index": chunk.metadata.get("start_index", 0),
                    "end_index": chunk.metadata.get("end_index", 0),
                    "chunk_text": chunk_text,
                    "file_extension": Path(file_path).suffix.lstrip('.')
                }
                
                # Processing info
                processing_info = {
                    "api_used": "google_embeddings",
                    "confidence_score": 1.0,
                    "model_version": "text-embedding-004",
                    "processing_duration": (datetime.now() - chunk_start_time).total_seconds()
                }
                
                # Convert metadata
                document_metadata = self.metadata_converter.file_metadata_to_document_metadata(
                    file_metadata=file_metadata,
                    chunk_info=chunk_info,
                    processing_info=processing_info
                )
                
                # Store in Milvus
                file_size = len(chunk_text.encode())
                content_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
                
                doc_id = self.milvus_db.insert_document(
                    collection_name=collection_name,
                    vector=embeddings[0],
                    metadata=document_metadata,
                    file_size=file_size,
                    content_hash=content_hash
                )
                
                if doc_id:
                    results["milvus_ids"].append(doc_id)
                    chunk_end_time = datetime.now()
                    results["processing_times"].append(
                        (chunk_end_time - chunk_start_time).total_seconds()
                    )
                    logger.info(f"Processed chunk {i+1}/{len(chunks)}: {doc_id}")
                else:
                    results["errors"].append(f"Failed to store chunk {i} in Milvus")
                    
            except Exception as e:
                error_msg = f"Error processing chunk {i}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        return results
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for file"""
        extension = Path(file_path).suffix.lower()
        
        mime_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.json': 'application/json',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        return mime_types.get(extension, 'text/plain')
    
    def _display_results(self, results: Dict[str, Any]):
        """Display comprehensive workflow results"""
        print("\n" + "="*80)
        print("END-TO-END DOCUMENT PROCESSING WORKFLOW RESULTS")
        print("="*80)
        
        print(f"\nFile: {results['file_path']}")
        print(f"Total Processing Time: {results['total_processing_time']:.2f} seconds")
        print(f"Chunks Processed: {results['chunks_processed']}")
        print(f"Embeddings Generated: {results['embeddings_generated']}")
        print(f"Milvus Documents Stored: {len(results['milvus_ids'])}")
        
        # Stage-by-stage results
        print(f"\nSTAGE RESULTS:")
        for stage, stage_results in results["stages"].items():
            print(f"  {stage.upper()}:")
            if isinstance(stage_results, dict):
                for key, value in stage_results.items():
                    if key != "file_metadata":  # Skip large metadata object
                        print(f"    {key}: {value}")
            else:
                print(f"    {stage_results}")
        
        # Milvus IDs
        if results["milvus_ids"]:
            print(f"\nMILVUS DOCUMENT IDs:")
            for i, doc_id in enumerate(results["milvus_ids"][:5]):  # Show first 5
                print(f"  Chunk {i+1}: {doc_id}")
            if len(results["milvus_ids"]) > 5:
                print(f"  ... and {len(results['milvus_ids']) - 5} more")
        
        # Errors
        if results["stages"].get("embedding_and_storage", {}).get("errors"):
            print(f"\nERRORS:")
            for error in results["stages"]["embedding_and_storage"]["errors"]:
                print(f"  - {error}")
        
        print("="*80)
    
    def _display_search_results(self, query: str, results: List[Dict[str, Any]]):
        """Display search results"""
        print("\n" + "="*80)
        print("SIMILARITY SEARCH RESULTS")
        print("="*80)
        print(f"Query: {query}")
        print(f"Results Found: {len(results)}")
        
        if not results:
            print("No similar content found.")
        else:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Similarity Score: {result['score']:.4f}")
                print(f"   Document ID: {result['id']}")
                print(f"   Department: {result.get('department', 'N/A')}")
                print(f"   Content Type: {result.get('content_type', 'N/A')}")
                
                # Extract chunk text from metadata
                metadata = result.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}
                
                domain_specific = metadata.get('domain_specific', {})
                if isinstance(domain_specific, str):
                    try:
                        domain_specific = json.loads(domain_specific)
                    except json.JSONDecodeError:
                        domain_specific = {}
                
                chunk_text = domain_specific.get('custom_fields', {}).get('chunk_text', 'N/A')
                chunk_index = domain_specific.get('custom_fields', {}).get('chunk_index', 'N/A')
                
                print(f"   Chunk Index: {chunk_index}")
                print(f"   Preview: {chunk_text[:200]}...")
                print("-" * 60)
        
        print("="*80)
    
    def _display_stored_documents(self, results: List[Dict[str, Any]], collection_name: str, total_entities: int):
        """Display stored documents"""
        print("\n" + "="*80)
        print("STORED DOCUMENTS")
        print("="*80)
        print(f"Collection: {collection_name}")
        print(f"Total Documents in Collection: {total_entities}")
        print(f"Showing: {len(results)} documents")
        
        if not results:
            print("No documents retrieved.")
        else:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Document ID: {result['id']}")
                print(f"   Department: {result.get('department', 'N/A')}")
                print(f"   Content Type: {result.get('content_type', 'N/A')}")
                print(f"   Role: {result.get('role', 'N/A')}")
                print(f"   Security Level: {result.get('security_level', 'N/A')}")
                
                # Extract metadata information
                metadata = result.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}
                
                # Get content metadata
                content = metadata.get('content', {})
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        content = {}
                
                # Get domain-specific metadata
                domain_specific = metadata.get('domain_specific', {})
                if isinstance(domain_specific, str):
                    try:
                        domain_specific = json.loads(domain_specific)
                    except json.JSONDecodeError:
                        domain_specific = {}
                
                title = content.get('title', 'N/A')
                author = content.get('author', 'N/A')
                tags = content.get('tags', [])
                chunk_index = domain_specific.get('custom_fields', {}).get('chunk_index', 'N/A')
                chunk_text = domain_specific.get('custom_fields', {}).get('chunk_text', 'N/A')
                
                print(f"   Title: {title}")
                print(f"   Author: {author}")
                print(f"   Tags: {', '.join(tags) if tags else 'N/A'}")
                print(f"   Chunk Index: {chunk_index}")
                print(f"   Content Preview: {chunk_text[:150]}...")
                print("-" * 60)
        
        print("="*80)

def create_sample_document():
    """Create a sample document for testing"""
    sample_text = """
    Healthcare Quality Improvement Protocol

    This document outlines the standard procedures for implementing quality improvement 
    initiatives in healthcare settings. Quality improvement is essential for maintaining 
    high standards of patient care and ensuring optimal outcomes.

    Key Components:
    1. Assessment of current practices
    2. Identification of improvement opportunities
    3. Implementation of evidence-based solutions
    4. Monitoring and evaluation of results
    5. Continuous refinement of processes

    The protocol emphasizes the importance of multidisciplinary collaboration, 
    patient-centered care, and data-driven decision making. Regular audits and 
    feedback mechanisms ensure sustained improvement over time.

    Implementation Guidelines:
    - Establish clear objectives and metrics
    - Engage all stakeholders in the process
    - Provide adequate training and resources
    - Monitor progress against established benchmarks
    - Communicate results transparently

    This approach has been successfully implemented in numerous healthcare facilities,
    resulting in improved patient satisfaction, reduced adverse events, and enhanced
    operational efficiency.
    """.strip()
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(sample_text)
    temp_file.close()
    
    return temp_file.name

def check_google_credentials():
    """Check Google API credentials"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: Google API key not found!")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY='your-api-key'")
        return False
    return True

async def main():
    """Main function with argparse commands"""
    parser = argparse.ArgumentParser(description="End-to-End Document Processing Workflow")
    parser.add_argument("--api-key", help="Google API key (optional, can use env var GOOGLE_API_KEY)")
    parser.add_argument("--collection", default="text_embeddings", help="Milvus collection name (default: text_embeddings)")
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a document to the collection")
    add_parser.add_argument("file_path", help="Path to the file to process")
    add_parser.add_argument("--filename", help="Custom filename (optional)")
    
    # Read command
    read_parser = subparsers.add_parser("read", help="Read stored documents from the collection")
    read_parser.add_argument("--limit", type=int, default=10, help="Number of documents to retrieve (default: 10)")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Search for similar content")
    query_parser.add_argument("query_text", help="Text to search for")
    query_parser.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run a demo with sample document")
    
    args = parser.parse_args()
    
    # Check credentials if not provided via command line
    if not args.api_key and not check_google_credentials():
        return
    
    try:
        # Initialize workflow
        workflow = EndToEndWorkflow(google_api_key=args.api_key)
        
        if args.command == "add":
            print("End-to-End Document Processing Workflow - ADD")
            print("============================================")
            
            if not os.path.exists(args.file_path):
                print(f"Error: File '{args.file_path}' not found!")
                return
            
            print(f"Processing file: {args.file_path}")
            
            # Process the file end-to-end
            results = await workflow.process_file_end_to_end(
                file_path=args.file_path,
                filename=args.filename,
                collection_name=args.collection
            )
            
            if results.get('milvus_ids'):
                print(f"\nSuccess! Processed {results['chunks_processed']} chunks")
                print(f"Generated {results['embeddings_generated']} embeddings")
                print(f"Stored {len(results['milvus_ids'])} documents in Milvus")
            else:
                print("Failed to store documents in Milvus. Check the error messages above.")
        
        elif args.command == "read":
            print("End-to-End Document Processing Workflow - READ")
            print("==============================================")
            
            # Read stored documents
            results = workflow.read_stored_documents(
                collection_name=args.collection,
                limit=args.limit
            )
            
            if not results:
                print(f"No documents found in collection '{args.collection}'")
        
        elif args.command == "query":
            print("End-to-End Document Processing Workflow - QUERY")
            print("===============================================")
            
            # Search for similar content
            results = await workflow.search_similar_content(
                query_text=args.query_text,
                collection_name=args.collection,
                limit=args.limit
            )
            
            if not results:
                print("No similar content found.")
        
        elif args.command == "demo":
            print("End-to-End Document Processing Workflow - DEMO")
            print("==============================================")
            
            # Create sample document
            sample_file = create_sample_document()
            print(f"Created sample document: {sample_file}")
            
            try:
                # Process the file end-to-end
                print("\n1. Adding sample document...")
                results = await workflow.process_file_end_to_end(
                    file_path=sample_file,
                    filename="healthcare_quality_protocol.txt",
                    collection_name=args.collection
                )
                
                if results.get('milvus_ids'):
                    print(f"Success! Processed {results['chunks_processed']} chunks")
                    print(f"Generated {results['embeddings_generated']} embeddings")
                    print(f"Stored {len(results['milvus_ids'])} documents in Milvus")
                    
                    # Test similarity search
                    print("\n2. Testing similarity search...")
                    search_results = await workflow.search_similar_content(
                        query_text="quality improvement in healthcare",
                        collection_name=args.collection,
                        limit=3
                    )
                    
                    # Show stored documents
                    print("\n3. Reading stored documents...")
                    stored_docs = workflow.read_stored_documents(
                        collection_name=args.collection,
                        limit=5
                    )
                    
                    print("\nDemo completed successfully!")
                else:
                    print("Demo failed - could not store documents in Milvus")
                    
            finally:
                # Clean up sample file
                if os.path.exists(sample_file):
                    os.unlink(sample_file)
                    print(f"\nCleaned up sample file: {sample_file}")
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 