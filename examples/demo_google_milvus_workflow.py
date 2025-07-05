#!/usr/bin/env python3
import argparse
import logging
from typing import Optional, List
import sys
import os

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.external_apis.google_service import get_google_service
from src.database.milvus_db import MilvusVectorDatabase
from src.database.config import (
    DocumentMetadata, ContentMetadata, OrganizationalMetadata,
    ContentTypeEnum, OrganizationTypeEnum, SecurityLevelEnum,
    ProcessingMetadata, DomainSpecificMetadata, ComplianceMetadata
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMilvusDemo:
    def __init__(self, google_api_key: Optional[str] = None, reset_collection: bool = False):
        # Initialize services
        self.google_service = get_google_service(api_key=google_api_key)
        self.milvus_db = MilvusVectorDatabase()
        
        # Connect to Milvus
        if not self.milvus_db.connect():
            raise RuntimeError("Failed to connect to Milvus database")
            
        # Create collections first
        if not self.milvus_db.create_all_collections():
            raise RuntimeError("Failed to create collections")
        
        # Only reset collection if explicitly requested
        if reset_collection:
            self._reset_collection("text_embeddings")
    
    def _reset_collection(self, collection_name: str):
        """Reset a collection to start fresh"""
        try:
            from pymilvus import utility
            
            # Drop and recreate the collection
            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
                logger.info(f"Dropped existing collection: {collection_name}")
            
            # Create new collection
            self.milvus_db.create_collection(collection_name)
            logger.info(f"Created fresh collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to reset collection {collection_name}: {e}")
    
    def process_text(self, text: str, collection_name: str = "text_embeddings") -> str:
        """Process text and store embeddings in Milvus"""
        try:
            # Generate embeddings
            embeddings = self.google_service.generate_text_embeddings(text)
            if not embeddings:
                raise ValueError("Failed to generate embeddings")
            
            # Debug: print embedding dimensions
            logger.info(f"Generated embedding dimensions: {len(embeddings[0])}")
            
            # Create metadata
            metadata = DocumentMetadata(
                content=ContentMetadata(
                    title="Stored Text",
                    author="User",
                    content_type=ContentTypeEnum.DOCUMENT,
                    format="txt",
                    tags=["text"],
                    keywords=["text"],
                    description=text[:200] + "..." if len(text) > 200 else text  # Store preview in description
                ),
                organizational=OrganizationalMetadata(
                    department="Demo",
                    role="user",
                    organization_type=OrganizationTypeEnum.UNIVERSITY,
                    security_level=SecurityLevelEnum.PUBLIC
                ),
                processing=ProcessingMetadata(
                    api_used="google_embeddings",
                    confidence_score=1.0
                ),
                domain_specific=DomainSpecificMetadata(
                    custom_fields={"full_text": text}  # Store full text in custom fields
                ),
                compliance=ComplianceMetadata()
            )
            
            # Store in Milvus
            doc_id = self.milvus_db.insert_document(
                collection_name=collection_name,
                vector=embeddings[0],  # Using first embedding for simplicity
                metadata=metadata,
                file_size=len(text.encode()),
                content_hash="demo_hash"
            )
            
            if not doc_id:
                raise ValueError("Failed to insert document into Milvus")
                
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to process text: {e}")
            raise
    
    def search_similar(self, query_text: str, collection_name: str = "text_embeddings", limit: int = 5) -> List[dict]:
        """Search for similar texts using embeddings"""
        try:
            # Get collection stats before search
            collection = self.milvus_db.collections.get(collection_name)
            if collection:
                collection.load()
                total_entities = collection.num_entities
                logger.info(f"Collection '{collection_name}' contains {total_entities} documents")
            
            # Generate query embeddings
            query_embeddings = self.google_service.generate_text_embeddings(query_text)
            if not query_embeddings:
                raise ValueError("Failed to generate query embeddings")
            
            # Search in Milvus
            results = self.milvus_db.vector_search(
                collection_name=collection_name,
                query_vector=query_embeddings[0],  # Using first embedding
                limit=limit
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            raise

def check_google_credentials():
    """Check and validate Google API credentials"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: Google API key not found!")
        print("Please set your Google API key using one of these methods:")
        print("1. Export as environment variable:")
        print("   export GOOGLE_API_KEY='your-api-key'")
        print("2. Pass as command line argument:")
        print("   --api-key 'your-api-key'")
        print("\nTo get an API key:")
        print("1. Go to Google Cloud Console")
        print("2. Create a project or select existing one")
        print("3. Enable the Generative Language API")
        print("4. Create credentials (API key)")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Demo for Google embeddings with Milvus integration")
    parser.add_argument("--api-key", help="Google API key (optional, can use env var GOOGLE_API_KEY)")
    parser.add_argument("--reset", action="store_true", help="Reset the collection before operation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add text command
    add_parser = subparsers.add_parser("add", help="Add text to the database")
    add_parser.add_argument("text", help="Text to process")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for similar texts")
    search_parser.add_argument("query", help="Query text to search for")
    search_parser.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")
    
    args = parser.parse_args()
    
    # Check Google credentials if not provided via command line
    if not args.api_key and not check_google_credentials():
        sys.exit(1)
    
    try:
        demo = GoogleMilvusDemo(google_api_key=args.api_key, reset_collection=args.reset)
        
        if args.command == "add":
            doc_id = demo.process_text(args.text)
            if doc_id:
                print(f"Successfully added text with ID: {doc_id}")
            else:
                print("Failed to add text to database")
                sys.exit(1)
            
        elif args.command == "search":
            results = demo.search_similar(args.query, limit=args.limit)
            if not results:
                print("\nNo similar texts found")
                sys.exit(0)
                
            print("\nSearch Results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Similarity Score: {result['score']:.4f}")
                
                # Parse metadata from JSON string if needed
                metadata = result.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}
                
                # Get text from domain_specific custom fields
                domain_specific = metadata.get('domain_specific', {})
                if isinstance(domain_specific, str):
                    try:
                        domain_specific = json.loads(domain_specific)
                    except json.JSONDecodeError:
                        domain_specific = {}
                
                content = metadata.get('content', {})
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        content = {}
                
                full_text = domain_specific.get('custom_fields', {}).get('full_text', 'N/A')
                description = content.get('description', 'N/A')
                
                print(f"Preview: {description}")
                print(f"\nFull Text: {full_text}")
                print("-" * 80)  # Separator line
                
    except Exception as e:
        logger.error(f"Error: {e}")
        if "credentials" in str(e).lower():
            print("\nCredential Error: Please check your Google API key")
        sys.exit(1)

if __name__ == "__main__":
    main() 