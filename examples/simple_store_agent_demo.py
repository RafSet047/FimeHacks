#!/usr/bin/env python3
"""
Simple demonstration of StoreAgent storing text and tags in Milvus DB
"""

import sys
import os

from src.agents.store_agent import StoreAgent
from src.database.milvus_db import MilvusVectorDatabase

def main():
    """Simple demo of StoreAgent functionality"""
    
    print("Simple StoreAgent Demo")
    print("=" * 50)
    
    # Initialize Milvus DB
    print("Connecting to Milvus DB...")
    milvus_db = MilvusVectorDatabase()
    
    if not milvus_db.connect():
        print("❌ Failed to connect to Milvus DB")
        return
    
    print("✅ Connected to Milvus DB")
    
    # Create collection
    collection_name = "demo_collection"
    print(f"Creating collection: {collection_name}")
    milvus_db.create_collection(collection_name)
    
    # Initialize StoreAgent
    print("Initializing StoreAgent...")
    store_agent = StoreAgent(
        postgres_db=None,  # Not using PostgreSQL for this demo
        milvus_db=milvus_db,
        config={'vector_dim': 384}  # Smaller dimension for demo
    )
    
    # Test with a simple query
    with open("dummy_file.txt", "r") as file:
        test_text = file.read()
    
    print(f"\nStoring text: '{test_text}'")
    
    # Store the text
    result = store_agent.classify_and_store_query(test_text, collection_name)
    
    if result['success']:
        print("✅ Successfully stored document!")
        print(f"   Document ID: {result['document_id']}")
        print(f"   Tags: {result['tags']}")
        print(f"   Content Length: {result['content_length']} characters")
        print(f"   Embedding Dimension: {result['embedding_dim']}")
    else:
        print(f"❌ Failed to store document: {result['error']}")
        return
    
    # Retrieve and display stored documents
    print(f"\nRetrieving stored documents from '{collection_name}':")
    stored_docs = milvus_db.get_stored_documents(collection_name)
    
    for i, doc in enumerate(stored_docs, 1):
        print(f"\n--- Document {i} ---")
        print(f"ID: {doc['id']}")
        print(f"Content: {doc['content']}")
        print(f"Tags: {doc['tags']}")
        print(f"Content Type: {doc['content_type']}")
        print(f"Department: {doc['department']}")
        print(f"Agent: {doc.get('agent_name', 'Unknown')}")
        print(f"Timestamp: {doc.get('timestamp', 'Unknown')}")
    
    # Test tag search
    if stored_docs and stored_docs[0]['tags']:
        first_tag = stored_docs[0]['tags'][0]
        print(f"\nSearching for documents with tag: '{first_tag}'")
        
        matching_docs = milvus_db.search_by_tags(collection_name, [first_tag])
        print(f"Found {len(matching_docs)} matching documents")
        
        for doc in matching_docs:
            print(f"  - {doc['content'][:50]}...")
    
    # Cleanup
    milvus_db.disconnect()
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    main() 