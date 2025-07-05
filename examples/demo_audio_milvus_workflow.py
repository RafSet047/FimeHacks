#!/usr/bin/env python3
import argparse
import logging
from typing import Optional, List, Dict, Any
import sys
import os
import hashlib
import subprocess
import tempfile

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

class AudioMilvusDemo:
    def __init__(self, google_api_key: Optional[str] = None, reset_collection: bool = False):
        # Initialize services
        self.google_service = get_google_service(api_key=google_api_key)
        self.milvus_db = MilvusVectorDatabase()
        
        # Supported audio formats
        self.supported_formats = ['.wav', '.mp3']
        
        # Connect to Milvus
        if not self.milvus_db.connect():
            raise RuntimeError("Failed to connect to Milvus database")
        
        # Create audio transcripts collection config
        self.collection_name = "audio_transcripts"
        audio_config = CollectionConfig(
            name=self.collection_name,
            description="Audio transcripts with text embeddings",
            vector_dim=1536,  # Match Google's text embedding dimension
            content_types=[ContentTypeEnum.AUDIO],
            organization_types=[OrganizationTypeEnum.UNIVERSITY],
            agentic_description=AgenticDescription(
                purpose="Stores audio transcripts with text embeddings",
                best_for="Audio content search by transcript meaning",
                typical_queries=[
                    "Find audio about X topic",
                    "Search for mentions of Y in recordings",
                    "Audio content similar to Z"
                ],
                search_hints=["Use for semantic audio search"],
                combine_with=["audio_recordings"],
                authority_level="medium"
            ),
            index_config={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
        )
        
        # Add collection config
        self.milvus_db.config.collections[self.collection_name] = audio_config
            
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
    
    def _process_embeddings(self, embeddings: List[List[float]], target_dim: int = 768) -> List[float]:
        """Process embeddings to match target dimension"""
        if not embeddings or not embeddings[0]:
            raise ValueError("Empty embeddings")
            
        embedding = embeddings[0]  # Take first embedding
        current_dim = len(embedding)
        
        if current_dim == target_dim:
            return embedding
        elif current_dim > target_dim:
            # Truncate to target dimension
            return embedding[:target_dim]
        else:
            # Pad with zeros to target dimension
            return embedding + [0.0] * (target_dim - current_dim)
    
    def _convert_to_wav(self, audio_file_path: str) -> str:
        """Convert audio file to WAV format if needed"""
        file_ext = os.path.splitext(audio_file_path)[1].lower()
        
        # If already WAV, return original path
        if file_ext == '.wav':
            return audio_file_path
            
        # Check if format is supported
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {file_ext}")
        
        try:
            # Create temporary WAV file
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav_path = temp_wav.name
            temp_wav.close()
            
            # Convert to WAV using ffmpeg
            command = [
                'ffmpeg',
                '-i', audio_file_path,  # Input file
                '-acodec', 'pcm_s16le',  # Output codec (16-bit PCM)
                '-ar', '16000',          # Sample rate 16kHz
                '-ac', '1',              # Mono channel
                '-y',                    # Overwrite output file
                temp_wav_path            # Output file
            ]
            
            # Run ffmpeg
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")
            
            logger.info(f"Successfully converted {file_ext} to WAV")
            return temp_wav_path
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
            raise

    def process_audio(self, audio_file_path: str) -> str:
        """Process audio file: transcribe, generate embeddings, and store in Milvus"""
        temp_wav_path = None
        try:
            # Verify file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            # Convert to WAV if needed
            temp_wav_path = self._convert_to_wav(audio_file_path)
            
            # Step 1: Transcribe audio
            logger.info("Transcribing audio file...")
            transcription_result = self.google_service.transcribe_audio(temp_wav_path)
            
            if not transcription_result or not transcription_result.get("transcript"):
                raise ValueError("Failed to transcribe audio file")
            
            transcript = transcription_result["transcript"]
            confidence = transcription_result.get("confidence", 0.0)
            word_count = transcription_result.get("word_count", 0)
            speakers = transcription_result.get("speakers", [])
            
            logger.info(f"Transcript: {transcript}")
            
            # Step 2: Generate embeddings from transcript
            logger.info("Generating embeddings from transcript...")
            embeddings = self.google_service.generate_text_embeddings(transcript)
            if not embeddings:
                raise ValueError("Failed to generate embeddings")
            
            # Calculate file hash and size
            file_hash = self._calculate_file_hash(audio_file_path)
            file_size = os.path.getsize(audio_file_path)
            
            # Create metadata
            metadata = DocumentMetadata(
                content=ContentMetadata(
                    title=os.path.basename(audio_file_path),
                    author="User",
                    content_type=ContentTypeEnum.AUDIO,
                    format=os.path.splitext(audio_file_path)[1].lstrip('.'),
                    tags=["audio", "transcription"],
                    keywords=["audio", "speech"],
                    description=transcript[:200] + "..." if len(transcript) > 200 else transcript
                ),
                organizational=OrganizationalMetadata(
                    department="Demo",
                    role="user",
                    organization_type=OrganizationTypeEnum.UNIVERSITY,
                    security_level=SecurityLevelEnum.PUBLIC
                ),
                processing=ProcessingMetadata(
                    api_used="google_speech_to_text,google_embeddings",
                    confidence_score=confidence
                ),
                domain_specific=DomainSpecificMetadata(
                    custom_fields={
                        "full_transcript": transcript,
                        "word_count": word_count,
                        "speakers": speakers,
                        "audio_file": audio_file_path,
                        "original_format": os.path.splitext(audio_file_path)[1].lstrip('.')
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
            logger.error(f"Failed to process audio: {e}")
            raise
        finally:
            # Clean up temporary WAV file if created
            if temp_wav_path and temp_wav_path != audio_file_path:
                try:
                    os.remove(temp_wav_path)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_wav_path}: {e}")
    
    def search_similar(self, query_text: str, limit: int = 5) -> List[dict]:
        """Search for similar audio transcripts using text query"""
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
        print("3. Enable the Speech-to-Text and Generative Language APIs")
        print("4. Create credentials (API key)")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Demo for Google Speech-to-Text and embeddings with Milvus integration")
    parser.add_argument("--api-key", help="Google API key (optional, can use env var GOOGLE_API_KEY)")
    parser.add_argument("--reset", action="store_true", help="Reset the collection before operation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add audio command
    add_parser = subparsers.add_parser("add", help="Add audio file to the database")
    add_parser.add_argument("audio_file", help="Path to audio file to process")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for similar audio content")
    search_parser.add_argument("query", help="Text query to search for")
    search_parser.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")
    
    args = parser.parse_args()
    
    # Check Google credentials if not provided via command line
    if not args.api_key and not check_google_credentials():
        sys.exit(1)
    
    try:
        demo = AudioMilvusDemo(google_api_key=args.api_key, reset_collection=args.reset)
        
        if args.command == "add":
            doc_id = demo.process_audio(args.audio_file)
            if doc_id:
                print(f"Successfully added audio file with ID: {doc_id}")
            else:
                print("Failed to add audio file to database")
                sys.exit(1)
            
        elif args.command == "search":
            results = demo.search_similar(args.query, limit=args.limit)
            if not results:
                print("\nNo similar audio content found")
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
                
                # Extract relevant information
                audio_file = domain_specific.get('custom_fields', {}).get('audio_file', 'N/A')
                transcript = domain_specific.get('custom_fields', {}).get('full_transcript', 'N/A')
                word_count = domain_specific.get('custom_fields', {}).get('word_count', 0)
                speakers = domain_specific.get('custom_fields', {}).get('speakers', [])
                description = content.get('description', 'N/A')
                
                print(f"Audio File: {audio_file}")
                print(f"Word Count: {word_count}")
                if speakers:
                    print(f"Speakers: {', '.join(speakers)}")
                print(f"\nPreview: {description}")
                print(f"\nFull Transcript: {transcript}")
                print("-" * 80)  # Separator line
                
    except Exception as e:
        logger.error(f"Error: {e}")
        if "credentials" in str(e).lower():
            print("\nCredential Error: Please check your Google API key")
        sys.exit(1)

if __name__ == "__main__":
    main() 