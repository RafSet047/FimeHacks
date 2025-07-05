#!/usr/bin/env python3
"""
Create Milvus collection for unstructured raw data.

This script creates a simple collection with the following fields:
- id: Unique identifier
- raw_data: The original text content
- vector_embedding: Vector representation of the data
- tags: List of tags for categorization
- initial_form: Source format (pdf, txt, wav, etc.)
"""

import sys
import os
from typing import List, Optional
import logging

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from src.database.milvus_db import MilvusVectorDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnstructuredDataCollection:
    """Simple collection for unstructured raw data"""
    
    def __init__(self, collection_name: str = "unstructured_data", vector_dim: int = 1536):
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.db = MilvusVectorDatabase()
        
    def create_collection(self) -> bool:
        """Create the unstructured data collection"""
        try:
            # Connect to Milvus
            if not self.db.connect():
                logger.error("Failed to connect to Milvus")
                return False
            
            # Check if collection already exists
            if utility.has_collection(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            
            # Define collection schema
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
                FieldSchema(name="raw_data", dtype=DataType.VARCHAR, max_length=65535),  # Large text field
                FieldSchema(name="vector_embedding", dtype=DataType.FLOAT_VECTOR, dim=self.vector_dim),
                FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=1000),  # JSON string of tags
                FieldSchema(name="initial_form", dtype=DataType.VARCHAR, max_length=50)
            ]
            
            schema = CollectionSchema(
                fields=fields,
                description="Collection for unstructured raw data with vector embeddings"
            )
            
            # Create collection
            collection = Collection(self.collection_name, schema)
            
            # Create index for vector field
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            collection.create_index("vector_embedding", index_params)
            
            logger.info(f"Successfully created collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def insert_data(self, raw_data: str, vector_embedding: List[float], 
                   tags: List[str], initial_form: str, doc_id: Optional[str] = None) -> Optional[str]:
        """Insert data into the collection"""
        try:
            if not self.db.is_connected:
                if not self.db.connect():
                    return None
            
            collection = Collection(self.collection_name)
            
            # Generate ID if not provided
            if doc_id is None:
                import uuid
                doc_id = str(uuid.uuid4())
            
            # Convert tags list to JSON string
            import json
            tags_json = json.dumps(tags)
            
            # Prepare data
            data = [
                [doc_id],                    # id
                [raw_data],                  # raw_data
                [vector_embedding],          # vector_embedding
                [tags_json],                 # tags (as JSON string)
                [initial_form]               # initial_form
            ]
            
            # Insert data
            collection.insert(data)
            collection.flush()
            
            logger.info(f"Inserted data with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            return None
    
    def search(self, query_vector: List[float], limit: int = 10, 
               tag_filter: Optional[str] = None) -> List[dict]:
        """Search for similar vectors"""
        try:
            if not self.db.is_connected:
                if not self.db.connect():
                    return []
            
            collection = Collection(self.collection_name)
            collection.load()
            
            # Search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Perform search
            results = collection.search(
                data=[query_vector],
                anns_field="vector_embedding",
                param=search_params,
                limit=limit,
                expr=tag_filter,
                output_fields=["id", "raw_data", "tags", "initial_form"]
            )
            
            # Process results
            search_results = []
            for hits in results:
                for hit in hits:
                    # Parse tags back to list
                    import json
                    tags = json.loads(hit.entity.get("tags", "[]"))
                    
                    result = {
                        "id": hit.entity.get("id"),
                        "score": hit.score,
                        "raw_data": hit.entity.get("raw_data"),
                        "tags": tags,
                        "initial_form": hit.entity.get("initial_form")
                    }
                    search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        """Get collection information"""
        try:
            if not self.db.is_connected:
                if not self.db.connect():
                    return {}
            
            collection = Collection(self.collection_name)
            collection.load()
            
            return {
                "name": self.collection_name,
                "total_entities": collection.num_entities,
                "vector_dimension": self.vector_dim,
                "description": "Collection for unstructured raw data with vector embeddings"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}

def main():
    """Main function to create the collection"""
    print("Creating unstructured data collection...")
    
    # Create collection instance
    collection = UnstructuredDataCollection()
    
    # Create the collection
    if collection.create_collection():
        print("✅ Collection created successfully!")
        
        # Show collection info
        info = collection.get_collection_info()
        print(f"Collection name: {info.get('name', 'N/A')}")
        print(f"Vector dimension: {info.get('vector_dimension', 'N/A')}")
        print(f"Total entities: {info.get('total_entities', 'N/A')}")
        
    else:
        print("❌ Failed to create collection")
        sys.exit(1)

if __name__ == "__main__":
    main()
