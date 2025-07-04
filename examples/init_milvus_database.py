#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.milvus_db import MilvusVectorDatabase
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def initialize_database():
    """Initialize the Milvus database with collections"""
    print("🔧 Initializing Milvus Vector Database...")
    
    # Create database instance
    db = MilvusVectorDatabase()
    
    # Connect to database
    if not db.connect():
        print("❌ Failed to connect to Milvus. Make sure Milvus is running.")
        return None
    
    # Create all collections
    if not db.create_all_collections():
        print("❌ Failed to create collections.")
        return None
    
    print("✅ Database initialized successfully!")
    return db

def show_database_info(db: MilvusVectorDatabase):
    """Display information about the database and collections"""
    print("\n📊 Database Information:")
    print("=" * 50)
    
    # List all collections
    collections = db.list_collections()
    print(f"Total Collections: {len(collections)}")
    
    # Show detailed info for each collection
    for collection_name in db.get_available_collections():
        info = db.get_collection_info(collection_name)
        if info:
            print(f"\n📁 {collection_name.upper()}")
            print(f"   Description: {info['description']}")
            print(f"   Vector Dimensions: {info['vector_dimension']}")
            print(f"   Best for: {info['agentic_description']['best_for']}")
            
            # Get stats
            stats = db.get_stats(collection_name)
            print(f"   Current entities: {stats.get('total_entities', 0)}")

def example_usage():
    """Show example usage of the database"""
    print("\n🚀 Example Usage:")
    print("=" * 50)
    
    # Initialize database
    db = initialize_database()
    if not db:
        return
    
    # Show database info
    show_database_info(db)
    
    # Example: Insert a medical protocol document
    print("\n📝 Example: Inserting a medical protocol...")
    
    protocol_metadata = {
        "organizational": {
            "department": "emergency",
            "role": "physician",
            "security_level": "standard",
            "project_id": "emergency_protocols_2024"
        },
        "content": {
            "title": "Cardiac Arrest Response Protocol",
            "author": "Dr. Emergency",
            "document_type": "protocol",
            "creation_date": "2024-01-15",
            "last_updated": "2024-01-15",
            "version": "1.0"
        },
        "processing": {
            "api_used": "openai_embeddings",
            "processing_timestamp": "2024-01-15T10:30:00Z",
            "confidence": 0.95
        },
        "clinical": {
            "medical_specialty": "emergency_medicine",
            "protocol_type": "life_saving",
            "priority": "critical"
        },
        "compliance": {
            "hipaa_compliant": True,
            "review_date": "2025-01-15",
            "approved_by": "Chief Medical Officer"
        }
    }
    
    # This would be a real embedding in practice
    dummy_vector = [0.1] * 1536  # OpenAI embedding size
    
    doc_id = db.insert_data(
        collection_name="documents",
        vector=dummy_vector,
        metadata=protocol_metadata,
        content_type="medical_protocol",
        department="emergency",
        file_size=25000,
        content_hash="cardiac_protocol_v1_hash"
    )
    
    if doc_id:
        print(f"✅ Successfully inserted protocol with ID: {doc_id}")
    else:
        print("❌ Failed to insert protocol")
    
    # Example: Search for emergency protocols
    print("\n🔍 Example: Searching for emergency protocols...")
    
    # Metadata search
    results = db.metadata_search(
        "documents",
        'department == "emergency"',
        limit=5
    )
    
    print(f"Found {len(results)} emergency protocols:")
    for i, result in enumerate(results):
        metadata = result.get('metadata', {})
        title = metadata.get('content', {}).get('title', 'Unknown')
        print(f"  {i+1}. {title}")
        print(f"      ID: {result['id']}")
        print(f"      Department: {result['department']}")
    
    # Example: Vector search (would use real query embeddings)
    print("\n🎯 Example: Vector similarity search...")
    query_vector = [0.2] * 1536  # This would be a real query embedding
    
    vector_results = db.vector_search(
        "documents",
        query_vector,
        limit=3
    )
    
    print(f"Found {len(vector_results)} similar documents:")
    for i, result in enumerate(vector_results):
        print(f"  {i+1}. Similarity Score: {result['score']:.3f}")
        print(f"      ID: {result['id']}")
        print(f"      Department: {result['department']}")
    
    # Show updated stats
    print("\n📊 Updated Database Statistics:")
    for collection_name in ["documents", "images", "audio_recordings", "video_content"]:
        stats = db.get_stats(collection_name)
        print(f"  {collection_name}: {stats.get('total_entities', 0)} entities")
    
    # Cleanup
    db.disconnect()
    print("\n✅ Example completed successfully!")

def main():
    """Main function"""
    print("🏥 Milvus Vector Database for Healthcare/University")
    print("=" * 55)
    
    try:
        example_usage()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Milvus is running on localhost:19530")
        print("You can start Milvus using Docker:")
        print("  docker run -p 19530:19530 milvusdb/milvus:latest")

if __name__ == "__main__":
    main() 