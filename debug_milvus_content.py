#!/usr/bin/env python3

import sys
import os
import json
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.milvus_db import MilvusVectorDatabase

def debug_milvus_content():
    """Debug script to check what content is actually stored in Milvus"""
    
    # Initialize database
    db = MilvusVectorDatabase()
    
    # Connect to database
    if not db.connect():
        print("Failed to connect to Milvus database")
        return
    
    print("Connected to Milvus database")
    
    # List all collections
    collections = db.list_collections()
    print(f"Available collections: {collections}")
    
    # Check each collection
    for collection_name in collections:
        print(f"\n{'='*50}")
        print(f"COLLECTION: {collection_name}")
        print(f"{'='*50}")
        
        try:
            # First, make sure the collection is loaded in the collections dictionary
            if collection_name not in db.collections:
                print(f"Loading collection {collection_name} into collections dictionary...")
                try:
                    from pymilvus import Collection
                    db.collections[collection_name] = Collection(collection_name)
                    print(f"Successfully loaded collection {collection_name}")
                except Exception as load_error:
                    print(f"Failed to load collection {collection_name}: {load_error}")
                    continue
            
            # Get collection stats
            stats = db.get_stats(collection_name)
            print(f"Total entities: {stats.get('total_entities', 0)}")
            
            # Get stored documents
            documents = db.get_stored_documents(collection_name, limit=5)
            
            if not documents:
                print("No documents found in this collection")
                continue
                
            for i, doc in enumerate(documents):
                print(f"\nDocument {i+1}:")
                print(f"  ID: {doc.get('id', 'N/A')}")
                print(f"  Content Type: {doc.get('content_type', 'N/A')}")
                print(f"  Department: {doc.get('department', 'N/A')}")
                print(f"  Tags: {doc.get('tags', [])}")
                
                # Check what's in the raw metadata
                if 'id' in doc:
                    # Query raw metadata for this document
                    try:
                        if collection_name in db.collections:
                            collection = db.collections[collection_name]
                            collection.load()
                            
                            raw_results = collection.query(
                                expr=f"id == '{doc['id']}'",
                                output_fields=["metadata"],
                                limit=1
                            )
                            
                            if raw_results:
                                raw_metadata = raw_results[0].get("metadata")
                                if isinstance(raw_metadata, str):
                                    raw_metadata = json.loads(raw_metadata)
                                
                                print(f"  Raw metadata keys: {list(raw_metadata.keys()) if raw_metadata else 'None'}")
                                
                                # Check if there's any content field
                                if raw_metadata:
                                    for key in raw_metadata.keys():
                                        if 'content' in key.lower() or 'text' in key.lower():
                                            value = raw_metadata[key]
                                            if isinstance(value, str) and len(value) > 0:
                                                print(f"  Found text in '{key}': {value[:200]}...")
                                            else:
                                                print(f"  Found field '{key}' but no text content")
                                
                                # Print first few characters if content exists
                                content = doc.get('content', '')
                                if content:
                                    print(f"  Content preview: {content[:200]}...")
                                else:
                                    print(f"  No content field found")
                                    
                    except Exception as e:
                        print(f"  Error querying raw metadata: {e}")
                        
        except Exception as e:
            print(f"Error processing collection {collection_name}: {e}")
    
    # Disconnect
    db.disconnect()
    print(f"\nDisconnected from database")

if __name__ == "__main__":
    debug_milvus_content() 