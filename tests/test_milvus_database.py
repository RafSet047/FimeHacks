#!/usr/bin/env python3

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.milvus_db import MilvusVectorDatabase
import json
import random

def generate_dummy_vector(dim: int) -> list:
    """Generate random vector for testing"""
    return [random.random() for _ in range(dim)]

@pytest.fixture
def db():
    """Database fixture for tests"""
    database = MilvusVectorDatabase()
    if database.connect():
        yield database
        database.disconnect()
    else:
        pytest.skip("Milvus not available")

@pytest.fixture
def db_with_collections(db):
    """Database fixture with collections created"""
    if db.create_all_collections():
        return db
    else:
        pytest.skip("Failed to create collections")

class TestMilvusDatabase:
    """Test class for Milvus Database functionality"""
    
    def test_connection(self):
        """Test database connection"""
        db = MilvusVectorDatabase()
        success = db.connect()
        
        if success:
            assert db.is_connected
            assert db.health_check()
            db.disconnect()
            assert not db.is_connected
        else:
            pytest.skip("Milvus not available for testing")
    
    def test_collection_creation(self, db):
        """Test collection creation"""
        success = db.create_all_collections()
        assert success
        
        collections = db.list_collections()
        assert len(collections) >= 0
        
        available_collections = db.get_available_collections()
        assert "documents" in available_collections
        assert "images" in available_collections
        assert "audio_recordings" in available_collections
        assert "video_content" in available_collections
    
    def test_collection_info(self, db_with_collections):
        """Test getting collection information"""
        info = db_with_collections.get_collection_info("documents")
        assert info is not None
        assert info["name"] == "documents"
        assert "description" in info
        assert "vector_dimension" in info
        assert "agentic_description" in info
        assert info["enabled"] is True
    
    def test_data_insertion(self, db_with_collections):
        """Test data insertion using legacy method"""
        text_metadata = {
            "organizational": {
                "department": "cardiology",
                "role": "physician",
                "project_id": "heart_study_2024"
            },
            "content": {
                "title": "Cardiac Emergency Protocol",
                "author": "Dr. Smith",
                "document_type": "protocol",
                "creation_date": "2024-01-15"
            },
            "processing": {
                "api_used": "openai",
                "confidence": 0.95
            }
        }
        
        text_vector = generate_dummy_vector(1536)
        doc_id = db_with_collections.insert_data(
            collection_name="documents",
            vector=text_vector,
            metadata=text_metadata,
            content_type="protocol",
            department="cardiology",
            file_size=15000,
            content_hash="abc123"
        )
        
        assert doc_id is not None
        assert isinstance(doc_id, str)
        assert len(doc_id) > 0
    
    def test_vector_search(self, db_with_collections):
        """Test vector similarity search"""
        text_metadata = {
            "organizational": {
                "department": "cardiology",
                "role": "physician"
            },
            "content": {
                "title": "Test Document",
                "author": "Dr. Test"
            }
        }
        
        text_vector = generate_dummy_vector(1536)
        doc_id = db_with_collections.insert_data(
            collection_name="documents",
            vector=text_vector,
            metadata=text_metadata,
            content_type="protocol",
            department="cardiology",
            file_size=15000,
            content_hash="test123"
        )
        
        assert doc_id is not None
        
        query_vector = generate_dummy_vector(1536)
        results = db_with_collections.vector_search(
            "documents", 
            query_vector, 
            limit=5
        )
        
        assert isinstance(results, list)
        if len(results) > 0:
            result = results[0]
            assert "id" in result
            assert "score" in result
            assert "metadata" in result
            assert "content_type" in result
            assert "department" in result
    
    def test_metadata_search(self, db_with_collections):
        """Test metadata-based search"""
        text_metadata = {
            "organizational": {
                "department": "emergency",
                "role": "physician"
            },
            "content": {
                "title": "Emergency Protocol",
                "author": "Dr. Emergency"
            }
        }
        
        text_vector = generate_dummy_vector(1536)
        doc_id = db_with_collections.insert_data(
            collection_name="documents",
            vector=text_vector,
            metadata=text_metadata,
            content_type="protocol",
            department="emergency",
            file_size=15000,
            content_hash="emergency123"
        )
        
        assert doc_id is not None
        
        results = db_with_collections.metadata_search(
            "documents",
            'department == "emergency"',
            limit=5
        )
        
        assert isinstance(results, list)
        if len(results) > 0:
            result = results[0]
            assert result["department"] == "emergency"

def test_database_configuration():
    """Test database configuration without connection"""
    db = MilvusVectorDatabase()
    
    config_dict = db.get_config_dict()
    assert isinstance(config_dict, dict)
    assert "host" in config_dict
    assert "port" in config_dict
    assert "collections" in config_dict

if __name__ == "__main__":
    pytest.main([__file__]) 