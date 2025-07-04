from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
import logging
import uuid
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.config import (
    DatabaseConfig, CollectionConfig, DocumentMetadata, 
    get_default_database_config, load_config_from_dict
)

logger = logging.getLogger(__name__)

class MilvusVectorDatabase:
    def __init__(self, config: Optional[DatabaseConfig] = None, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialize Milvus Vector Database
        
        Args:
            config: DatabaseConfig object with full configuration
            host: Milvus host (overrides config if provided)
            port: Milvus port (overrides config if provided)
        """
        # Use provided config or default
        self.config = config or get_default_database_config()
        
        # Override host/port if provided
        if host:
            self.config.host = host
        if port:
            self.config.port = port
            
        self.host = self.config.host
        self.port = self.config.port
        self.connection_name = "default"
        self.collections: Dict[str, Collection] = {}
        self.is_connected = False
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MilvusVectorDatabase':
        """Create database instance from dictionary configuration (for UI integration)"""
        config = load_config_from_dict(config_dict)
        return cls(config=config)
    
    def update_config(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary (for UI integration)"""
        self.config = load_config_from_dict(config_dict)
        
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary (for UI integration)"""
        return self.config.model_dump()
        
    def connect(self) -> bool:
        try:
            # Try Milvus Lite first (local embedded database)
            connections.connect(
                alias=self.connection_name,
                uri="./milvus_lite.db"
            )
            self.is_connected = True
            logger.info("Connected to Milvus Lite (embedded database)")
            return True
        except Exception as e:
            # Fallback to remote server if Milvus Lite fails
            try:
                connections.connect(
                    alias=self.connection_name,
                    host=self.host,
                    port=self.port
                )
                self.is_connected = True
                logger.info(f"Connected to Milvus at {self.host}:{self.port}")
                return True
            except Exception as e2:
                logger.error(f"Failed to connect to Milvus: {e2}")
                return False
    
    def disconnect(self):
        if self.is_connected:
            connections.disconnect(self.connection_name)
            self.is_connected = False
            logger.info("Disconnected from Milvus")
    
    def health_check(self) -> bool:
        try:
            # For Milvus Lite, just check if we can list collections
            utility.list_collections()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        try:
            return utility.list_collections()
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def _create_collection_schema(self, collection_config: CollectionConfig) -> CollectionSchema:
        """Create collection schema from Pydantic configuration"""
        vector_dim = collection_config.vector_dim
        
        # Common fields for all collections
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dim),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="content_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="department", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="role", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="organization_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="security_level", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="timestamp", dtype=DataType.INT64),
            FieldSchema(name="file_size", dtype=DataType.INT64),
            FieldSchema(name="content_hash", dtype=DataType.VARCHAR, max_length=64)
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description=collection_config.description,
            enable_dynamic_field=True
        )
        
        return schema
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a collection based on configuration"""
        if collection_name not in self.config.collections:
            logger.error(f"Collection {collection_name} not found in configuration")
            return False
            
        collection_config = self.config.collections[collection_name]
        
        # Skip if collection is disabled
        if not collection_config.enabled:
            logger.info(f"Collection {collection_name} is disabled, skipping")
            return True
            
        try:
            # Check if collection already exists
            if utility.has_collection(collection_name):
                logger.info(f"Collection {collection_name} already exists")
                self.collections[collection_name] = Collection(collection_name)
                return True
            
            # Create new collection
            schema = self._create_collection_schema(collection_config)
            collection = Collection(collection_name, schema)
            self.collections[collection_name] = collection
            
            logger.info(f"Created collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False
    
    def create_all_collections(self) -> bool:
        """Create all enabled collections"""
        success = True
        for collection_name, collection_config in self.config.collections.items():
            if collection_config.enabled:
                if not self.create_collection(collection_name):
                    success = False
        return success
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get collection information"""
        if collection_name not in self.config.collections:
            return None
            
        collection_config = self.config.collections[collection_name]
        return {
            "name": collection_name,
            "description": collection_config.description,
            "vector_dimension": collection_config.vector_dim,
            "content_types": [ct.value for ct in collection_config.content_types],
            "organization_types": [ot.value for ot in collection_config.organization_types],
            "agentic_description": collection_config.agentic_description.model_dump(),
            "enabled": collection_config.enabled
        }
    
    def insert_document(self, collection_name: str, vector: List[float], 
                       metadata: DocumentMetadata, file_size: int, content_hash: str) -> Optional[str]:
        """Insert document with structured metadata"""
        try:
            if collection_name not in self.collections:
                if not self.create_collection(collection_name):
                    return None
            
            collection = self.collections[collection_name]
            
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            
            # Prepare data as lists for batch insertion
            data = [
                [doc_id],                                           # id field
                [vector],                                           # vector field
                [metadata.model_dump_json()],                      # metadata field as JSON string
                [metadata.content.content_type.value],             # content_type field
                [metadata.organizational.department],               # department field
                [metadata.organizational.role],                    # role field
                [metadata.organizational.organization_type.value], # organization_type field
                [metadata.organizational.security_level.value],    # security_level field
                [int(time.time() * 1000)],                        # timestamp field
                [file_size],                                       # file_size field
                [content_hash]                                     # content_hash field
            ]
            
            # Insert data
            collection.insert(data)
            collection.flush()
            
            logger.info(f"Inserted document into {collection_name} with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to insert document into {collection_name}: {e}")
            return None
    
    def insert_data(self, collection_name: str, vector: List[float], metadata: Dict[str, Any], 
                   content_type: str, department: str, file_size: int, content_hash: str) -> Optional[str]:
        """Legacy insert method for backward compatibility"""
        try:
            if collection_name not in self.collections:
                if not self.create_collection(collection_name):
                    return None
            
            collection = self.collections[collection_name]
            
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            
            # Extract values from metadata for backward compatibility
            org_meta = metadata.get("organizational", {})
            role = org_meta.get("role", "unknown")
            org_type = org_meta.get("organization_type", "healthcare")
            security_level = org_meta.get("security_level", "internal")
            
            # Prepare data as lists for batch insertion
            data = [
                [doc_id],                    # id field
                [vector],                    # vector field
                [json.dumps(metadata)],      # metadata field as JSON string
                [content_type],              # content_type field
                [department],                # department field
                [role],                      # role field
                [org_type],                  # organization_type field
                [security_level],            # security_level field
                [int(time.time() * 1000)],   # timestamp field
                [file_size],                 # file_size field
                [content_hash]               # content_hash field
            ]
            
            # Insert data
            collection.insert(data)
            collection.flush()
            
            logger.info(f"Inserted data into {collection_name} with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to insert data into {collection_name}: {e}")
            return None
    
    def vector_search(self, collection_name: str, query_vector: List[float], 
                     limit: int = 10, metadata_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        try:
            if collection_name not in self.collections:
                logger.error(f"Collection {collection_name} not found")
                return []
            
            collection = self.collections[collection_name]
            collection_config = self.config.collections[collection_name]
            
            # Create index if not exists  
            try:
                # Try to describe the index first
                collection.describe_index("vector")
            except Exception:
                # Create index if it doesn't exist
                try:
                    collection.create_index("vector", collection_config.index_config)
                except Exception as e:
                    # If index creation fails, it might already exist
                    logger.warning(f"Index creation failed or already exists: {e}")
                    pass
            
            # Load collection
            collection.load()
            
            search_params = {
                "metric_type": collection_config.index_config.get("metric_type", "COSINE"),
                "params": collection_config.index_config.get("params", {"nprobe": 10})
            }
            
            # Perform search
            results = collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=limit,
                expr=metadata_filter,
                output_fields=["id", "metadata", "content_type", "department", "role", 
                             "organization_type", "security_level", "timestamp", "content_hash"]
            )
            
            # Process results
            search_results = []
            for hits in results:
                for hit in hits:
                    metadata = hit.entity.get("metadata")
                    if isinstance(metadata, str):
                        metadata = json.loads(metadata)
                    
                    result = {
                        "id": hit.entity.get("id"),
                        "score": hit.score,
                        "metadata": metadata,
                        "content_type": hit.entity.get("content_type"),
                        "department": hit.entity.get("department"),
                        "role": hit.entity.get("role"),
                        "organization_type": hit.entity.get("organization_type"),
                        "security_level": hit.entity.get("security_level"),
                        "timestamp": hit.entity.get("timestamp")
                    }
                    search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Vector search failed in {collection_name}: {e}")
            return []
    
    def metadata_search(self, collection_name: str, filter_expr: str, 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """Search based on metadata filters only"""
        try:
            if collection_name not in self.collections:
                logger.error(f"Collection {collection_name} not found")
                return []
            
            collection = self.collections[collection_name]
            collection.load()
            
            results = collection.query(
                expr=filter_expr,
                output_fields=["id", "metadata", "content_type", "department", "role", 
                             "organization_type", "security_level", "timestamp"],
                limit=limit
            )
            
            # Parse JSON metadata back to dictionary
            for result in results:
                metadata = result.get("metadata")
                if isinstance(metadata, str):
                    result["metadata"] = json.loads(metadata)
            
            return results
            
        except Exception as e:
            logger.error(f"Metadata search failed in {collection_name}: {e}")
            return []
    
    def hybrid_search(self, collection_name: str, query_vector: List[float], 
                     metadata_filter: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Combine vector search with metadata filtering"""
        return self.vector_search(collection_name, query_vector, limit, metadata_filter)
    
    def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            if collection_name not in self.collections:
                return {}
            
            collection = self.collections[collection_name]
            collection.load()
            
            collection_config = self.config.collections[collection_name]
            
            return {
                "total_entities": collection.num_entities,
                "collection_name": collection_name,
                "description": collection_config.description,
                "enabled": collection_config.enabled,
                "vector_dimension": collection_config.vector_dim,
                "content_types": [ct.value for ct in collection_config.content_types]
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for {collection_name}: {e}")
            return {}
    
    def get_available_collections(self) -> List[str]:
        """Get list of available collection names"""
        return list(self.config.collections.keys())
    
    def get_organization_info(self) -> Dict[str, Any]:
        """Get organization-level information"""
        return {
            "organization_type": self.config.organization_type.value,
            "default_security_level": self.config.default_security_level.value,
            "audit_logging_enabled": self.config.enable_audit_logging,
            "total_collections": len(self.config.collections),
            "enabled_collections": len([c for c in self.config.collections.values() if c.enabled])
        } 