#!/usr/bin/env python3
import argparse
import logging
from typing import Optional, List, Dict, Any
import sys
import os
import hashlib
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.external_apis.google_service import get_google_service
from src.database.milvus_db import MilvusVectorDatabase
from src.database.config import (
    DocumentMetadata, ContentMetadata, OrganizationalMetadata,
    ContentTypeEnum, OrganizationTypeEnum, SecurityLevelEnum,
    ProcessingMetadata, DomainSpecificMetadata, ComplianceMetadata,
    CollectionConfig, AgenticDescription
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageMilvusDemo:
    def __init__(self, google_api_key: Optional[str] = None, reset_collection: bool = False):
        # Initialize services
        self.google_service = get_google_service(api_key=google_api_key)
        self.milvus_db = MilvusVectorDatabase()
        
        # Supported image formats
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        # Connect to Milvus
        if not self.milvus_db.connect():
            raise RuntimeError("Failed to connect to Milvus database")
        
        # Create image descriptions collection config
        self.collection_name = "image_descriptions"
        image_config = CollectionConfig(
            name=self.collection_name,
            description="Image descriptions with text embeddings",
            vector_dim=1536,  # Match Google's text embedding dimension
            content_types=[ContentTypeEnum.IMAGE],
            organization_types=[OrganizationTypeEnum.UNIVERSITY],
            agentic_description=AgenticDescription(
                purpose="Stores image descriptions with text embeddings",
                best_for="Image content search by description meaning",
                typical_queries=[
                    "Find images containing X",
                    "Search for images with Y objects",
                    "Images similar to Z description"
                ],
                search_hints=["Use for semantic image search"],
                combine_with=["images"],
                authority_level="medium"
            ),
            index_config={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
        )
        
        # Add collection config
        self.milvus_db.config.collections[self.collection_name] = image_config
            
        # Create collections
        if not self.milvus_db.create_all_collections():
            raise RuntimeError("Failed to create collections")
        
        # Only reset collection if explicitly requested
        if reset_collection:
            self._reset_collection(self.collection_name)
    
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
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _validate_image_file(self, image_file_path: str) -> bool:
        """Validate if the file is a supported image format"""
        file_ext = Path(image_file_path).suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported image format: {file_ext}. Supported formats: {', '.join(self.supported_formats)}")
        
        # Check if file exists and is readable
        if not os.path.exists(image_file_path):
            raise FileNotFoundError(f"Image file not found: {image_file_path}")
        
        if not os.access(image_file_path, os.R_OK):
            raise PermissionError(f"Cannot read image file: {image_file_path}")
        
        return True

    def process_image(self, image_file_path: str, analysis_type: str = "caption") -> str:
        """Process image file: analyze, generate embeddings, and store in Milvus"""
        try:
            # Validate image file
            self._validate_image_file(image_file_path)
            
            # Step 1: Analyze image based on type
            logger.info(f"Analyzing image file: {image_file_path}")
            
            if analysis_type == "caption":
                description = self.google_service.generate_image_caption(image_file_path)
                analysis_method = "image_caption"
            elif analysis_type == "ocr":
                description = self.google_service.extract_text_from_image(image_file_path)
                analysis_method = "ocr_text_extraction"
            elif analysis_type == "detailed":
                description = self.google_service.analyze_image(
                    image_file_path, 
                    "Provide a detailed description of this image including objects, people, activities, colors, composition, and any text visible. Give me only one option."
                )
                analysis_method = "detailed_analysis"
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
            
            if not description or description.strip() == "":
                raise ValueError("Failed to generate image description")
            
            logger.info(f"Generated description ({analysis_type}): {description}")
            
            # Step 2: Generate embeddings from description
            logger.info("Generating embeddings from image description...")
            embeddings = self.google_service.generate_text_embeddings(description)
            if not embeddings:
                raise ValueError("Failed to generate embeddings")
            
            # Calculate file hash and size
            file_hash = self._calculate_file_hash(image_file_path)
            file_size = os.path.getsize(image_file_path)
            
            # Get image dimensions if possible
            try:
                from PIL import Image
                with Image.open(image_file_path) as img:
                    width, height = img.size
                    image_mode = img.mode
                    image_format = img.format
            except Exception as e:
                logger.warning(f"Could not get image dimensions: {e}")
                width, height = 0, 0
                image_mode = "unknown"
                image_format = "unknown"
            
            # Create metadata
            metadata = DocumentMetadata(
                content=ContentMetadata(
                    title=os.path.basename(image_file_path),
                    author="User",
                    content_type=ContentTypeEnum.IMAGE,
                    format=Path(image_file_path).suffix.lstrip('.').lower(),
                    tags=["image", analysis_type, "vision"],
                    keywords=["image", "visual", "description"],
                    description=description[:200] + "..." if len(description) > 200 else description
                ),
                organizational=OrganizationalMetadata(
                    department="Demo",
                    role="user",
                    organization_type=OrganizationTypeEnum.UNIVERSITY,
                    security_level=SecurityLevelEnum.PUBLIC
                ),
                processing=ProcessingMetadata(
                    api_used=f"google_vision_{analysis_method},google_embeddings",
                    confidence_score=0.95  # Assume high confidence for successful analysis
                ),
                domain_specific=DomainSpecificMetadata(
                    custom_fields={
                        "full_description": description,
                        "analysis_type": analysis_type,
                        "image_file": image_file_path,
                        "image_width": width,
                        "image_height": height,
                        "image_mode": image_mode,
                        "image_format": image_format,
                        "original_format": Path(image_file_path).suffix.lstrip('.').lower(),
                        "word_count": len(description.split())
                    }
                ),
                compliance=ComplianceMetadata()
            )
            
            # Store in Milvus
            doc_id = self.milvus_db.insert_document(
                collection_name=self.collection_name,
                vector=embeddings[0],  # Using first embedding
                metadata=metadata,
                file_size=file_size,
                content_hash=file_hash
            )
            
            if not doc_id:
                raise ValueError("Failed to insert document into Milvus")
                
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to process image: {e}")
            raise
    
    def search_similar(self, query_text: str, limit: int = 5) -> List[dict]:
        """Search for similar image descriptions using text query"""
        try:
            # Get collection stats before search
            collection = self.milvus_db.collections.get(self.collection_name)
            if collection:
                collection.load()
                total_entities = collection.num_entities
                logger.info(f"Collection '{self.collection_name}' contains {total_entities} documents")
            
            # Generate query embeddings
            query_embeddings = self.google_service.generate_text_embeddings(query_text)
            if not query_embeddings:
                raise ValueError("Failed to generate query embeddings")
            
            # Search in Milvus
            results = self.milvus_db.vector_search(
                collection_name=self.collection_name,
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
    parser = argparse.ArgumentParser(description="Demo for Google Vision API and embeddings with Milvus integration")
    parser.add_argument("--api-key", help="Google API key (optional, can use env var GOOGLE_API_KEY)")
    parser.add_argument("--reset", action="store_true", help="Reset the collection before operation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add image command
    add_parser = subparsers.add_parser("add", help="Add image file to the database")
    add_parser.add_argument("image_file", help="Path to image file to process")
    add_parser.add_argument("--type", choices=["caption", "ocr", "detailed"], default="caption",
                           help="Type of image analysis: caption (default), ocr, or detailed")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for similar image content")
    search_parser.add_argument("query", help="Text query to search for")
    search_parser.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all processed images")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of images to list (default: 10)")
    
    args = parser.parse_args()
    
    # Check Google credentials if not provided via command line
    if not args.api_key and not check_google_credentials():
        sys.exit(1)
    
    try:
        demo = ImageMilvusDemo(google_api_key=args.api_key, reset_collection=args.reset)
        
        if args.command == "add":
            doc_id = demo.process_image(args.image_file, analysis_type=args.type)
            if doc_id:
                print(f"Successfully added image file with ID: {doc_id}")
                print(f"Analysis type: {args.type}")
            else:
                print("Failed to add image file to database")
                sys.exit(1)
            
        elif args.command == "search":
            results = demo.search_similar(args.query, limit=args.limit)
            if not results:
                print("\nNo similar image content found")
                sys.exit(0)
                
            print(f"\nSearch Results for: '{args.query}'")
            print("=" * 80)
            
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
                
                # Extract relevant information
                custom_fields = domain_specific.get('custom_fields', {})
                image_file = custom_fields.get('image_file', 'N/A')
                full_description = custom_fields.get('full_description', 'N/A')
                analysis_type = custom_fields.get('analysis_type', 'N/A')
                image_width = custom_fields.get('image_width', 0)
                image_height = custom_fields.get('image_height', 0)
                image_format = custom_fields.get('image_format', 'N/A')
                word_count = custom_fields.get('word_count', 0)
                
                description = content.get('description', 'N/A')
                
                print(f"Image File: {image_file}")
                print(f"Analysis Type: {analysis_type}")
                print(f"Dimensions: {image_width}x{image_height}")
                print(f"Format: {image_format}")
                print(f"Description Length: {word_count} words")
                print(f"\nPreview: {description}")
                print(f"\nFull Description: {full_description}")
                print("-" * 80)
                
        elif args.command == "list":
            # For listing, we'll search with a very generic query to get recent entries
            results = demo.search_similar("image", limit=args.limit)
            if not results:
                print("\nNo images found in database")
                sys.exit(0)
                
            print(f"\nRecent Images in Database (showing up to {args.limit}):")
            print("=" * 80)
            
            for i, result in enumerate(results, 1):
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
                
                content = metadata.get('content', {})
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        content = {}
                
                custom_fields = domain_specific.get('custom_fields', {})
                image_file = custom_fields.get('image_file', 'N/A')
                analysis_type = custom_fields.get('analysis_type', 'N/A')
                description = content.get('description', 'N/A')
                
                print(f"{i}. {os.path.basename(image_file)} ({analysis_type})")
                print(f"   {description}")
                print()
                
    except Exception as e:
        logger.error(f"Error: {e}")
        if "credentials" in str(e).lower():
            print("\nCredential Error: Please check your Google API key")
        elif "PIL" in str(e) or "image" in str(e).lower():
            print("\nImage Processing Error: Please ensure PIL is installed (pip install Pillow)")
        sys.exit(1)

if __name__ == "__main__":
    main() 