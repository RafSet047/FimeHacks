#!/usr/bin/env python3
"""
Simple Text Processing Workflow Demo

This script demonstrates the basic workflow:
1. Upload a text file
2. Extract text using document_extractor
3. Chunk the text using text_chunking
4. Display results

Focus on simplicity and basic text file processing.
"""

import os
import sys
import tempfile
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.file_upload import file_upload_service
from src.services.document_extractor import document_extractor
from src.services.text_chunking import TextChunker, ChunkingStrategy, ChunkingConfig
from src.database.connection import get_db
from src.utils.logging import logger
from src.models.metadata import FileMetadata, DocumentType, ContentCategory, EmployeeRole, PriorityLevel, AccessLevel

class SimpleTextWorkflow:
    """Simple workflow for processing text files"""
    
    def __init__(self):
        self.text_chunker = TextChunker()
        self.db_session = None
    
    async def process_text_file(self, file_path: str, filename: str = None):
        """Process a text file through the complete workflow"""
        try:
            # Step 1: Upload file
            logger.info(f"Step 1: Uploading file {file_path}")
            upload_result = await self._upload_file(file_path, filename)
            
            # Step 2: Extract text
            logger.info(f"Step 2: Extracting text from {file_path}")
            extracted_text = self._extract_text(file_path)
            
            # Step 3: Chunk text
            logger.info(f"Step 3: Chunking extracted text")
            chunks = self._chunk_text(extracted_text)
            
            # Step 4: Display results
            self._display_results(upload_result, extracted_text, chunks)
            
            return {
                "upload_result": upload_result,
                "extracted_text": extracted_text,
                "chunks": chunks
            }
            
        except Exception as e:
            logger.error(f"Error in text workflow: {e}")
            raise
    
    async def _upload_file(self, file_path: str, filename: str = None):
        """Upload file using file_upload_service"""
        try:
            # Create a mock UploadFile object for testing
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
                description="Demo text file for workflow testing",
                tags=["demo", "test", "workflow"]
            )
            
            # Get database session
            db = next(get_db())
            
            # Upload file
            result = await file_upload_service.upload_file(
                file=upload_file,
                db=db,
                file_metadata=file_metadata
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise
    
    def _extract_text(self, file_path: str):
        """Extract text using document_extractor"""
        try:
            # Determine MIME type
            mime_type = self._get_mime_type(file_path)
            
            # Extract text
            text = document_extractor.extract_text(file_path, mime_type)
            
            return text
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    def _chunk_text(self, text: str):
        """Chunk text using text_chunking service"""
        try:
            # Create chunking configuration
            config = ChunkingConfig(
                chunk_size=500,
                chunk_overlap=50,
                add_start_index=True
            )
            
            # Chunk the text
            chunks = self.text_chunker.chunk_text(
                text=text,
                strategy=ChunkingStrategy.RECURSIVE,
                config=config,
                metadata={"source": "demo"}
            )
            
            return chunks
            
        except Exception as e:
            logger.error(f"Text chunking failed: {e}")
            raise
    
    def _get_mime_type(self, file_path: str):
        """Get MIME type for file"""
        extension = Path(file_path).suffix.lower()
        
        mime_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.json': 'application/json'
        }
        
        return mime_types.get(extension, 'text/plain')
    
    def _display_results(self, upload_result, extracted_text, chunks):
        """Display workflow results"""
        print("\n" + "="*60)
        print("SIMPLE TEXT WORKFLOW RESULTS")
        print("="*60)
        
        # Upload results
        print(f"\n1. UPLOAD RESULTS:")
        print(f"   Success: {upload_result.get('success', False)}")
        print(f"   File ID: {upload_result.get('file_id', 'N/A')}")
        print(f"   Filename: {upload_result.get('filename', 'N/A')}")
        print(f"   File Size: {upload_result.get('file_size', 0)} bytes")
        
        # Extraction results
        print(f"\n2. TEXT EXTRACTION:")
        print(f"   Extracted Characters: {len(extracted_text)}")
        print(f"   Sample Text (first 200 chars):")
        print(f"   {extracted_text[:200]}...")
        
        # Chunking results
        print(f"\n3. TEXT CHUNKING:")
        print(f"   Total Chunks: {len(chunks)}")
        print(f"   Chunk Details:")
        
        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
            print(f"   Chunk {i+1}:")
            print(f"     Length: {len(chunk.page_content)} characters")
            print(f"     Start Index: {chunk.metadata.get('start_index', 'N/A')}")
            print(f"     End Index: {chunk.metadata.get('end_index', 'N/A')}")
            print(f"     Preview: {chunk.page_content[:100]}...")
            print()
        
        if len(chunks) > 3:
            print(f"   ... and {len(chunks) - 3} more chunks")
        
        print("="*60)


def create_sample_text_file():
    """Create a sample text file for testing"""
    sample_text = """
This is a sample text file for demonstrating the simple text workflow.

The workflow consists of three main steps:
1. Upload the file to the system
2. Extract text content from the file
3. Chunk the text into smaller pieces for processing

This text contains multiple paragraphs and sections to demonstrate how the chunking works.
Each chunk will have a specific size and overlap to ensure no information is lost during processing.

The chunking strategy used is recursive, which means it will try to split on different separators
in order of preference (double newlines, single newlines, spaces, characters).

This approach ensures that the text is split at natural boundaries whenever possible,
making the chunks more coherent and meaningful for downstream processing.

Finally, each chunk includes metadata about its position in the original text,
which can be useful for reconstruction or reference purposes.
    """.strip()
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(sample_text)
    temp_file.close()
    
    return temp_file.name


async def main():
    """Main demo function"""
    print("Simple Text Processing Workflow Demo")
    print("====================================")
    
    # Create sample file
    sample_file = create_sample_text_file()
    print(f"Created sample file: {sample_file}")
    
    try:
        # Initialize workflow
        workflow = SimpleTextWorkflow()
        
        # Process the file
        result = await workflow.process_text_file(sample_file, "demo_sample.txt")
        
        print("\nWorkflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"Error: {e}")
        
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.unlink(sample_file)
            print(f"Cleaned up sample file: {sample_file}")


if __name__ == "__main__":
    asyncio.run(main()) 