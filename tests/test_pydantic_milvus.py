#!/usr/bin/env python3

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.milvus_db import MilvusVectorDatabase
from src.database.config import (
    DatabaseConfig, DocumentMetadata, OrganizationalMetadata, 
    ContentMetadata, ProcessingMetadata, DomainSpecificMetadata, 
    ComplianceMetadata, OrganizationTypeEnum, ContentTypeEnum, 
    SecurityLevelEnum, get_default_database_config
)
from datetime import datetime
import json
import random
from typing import List

def generate_dummy_vector(dim: int) -> List[float]:
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

@pytest.fixture
def healthcare_document() -> DocumentMetadata:
    """Create a healthcare document for testing"""
    return DocumentMetadata(
        organizational=OrganizationalMetadata(
            department="emergency_medicine",
            role="attending_physician",
            organization_type=OrganizationTypeEnum.HEALTHCARE,
            project_id="emergency_protocols_2024",
            security_level=SecurityLevelEnum.CONFIDENTIAL,
            access_groups=["doctors", "nurses", "emergency_staff"]
        ),
        content=ContentMetadata(
            title="Test Emergency Protocol",
            author="Dr. Test",
            content_type=ContentTypeEnum.DOCUMENT,
            format="pdf",
            creation_date=datetime.now(),
            version="1.0",
            language="en",
            tags=["emergency", "protocol", "test"],
            keywords=["emergency", "protocol", "testing"]
        ),
        processing=ProcessingMetadata(
            api_used="openai_gpt4",
            confidence_score=0.95,
            model_version="gpt-4-turbo",
            processing_duration=10.0
        ),
        domain_specific=DomainSpecificMetadata(
            specialty="emergency_medicine",
            subject_area="protocols",
            priority="high",
            status="approved",
            related_entities=["test_cases"],
            custom_fields={"test": True}
        ),
        compliance=ComplianceMetadata(
            compliance_frameworks=["HIPAA"],
            retention_date=datetime(2030, 12, 31),
            approved_by="Test Administrator",
            review_date=datetime(2025, 6, 15),
            anonymized=True
        )
    )

@pytest.fixture
def university_document() -> DocumentMetadata:
    """Create a university document for testing"""
    return DocumentMetadata(
        organizational=OrganizationalMetadata(
            department="computer_science",
            role="professor",
            organization_type=OrganizationTypeEnum.UNIVERSITY,
            project_id="ai_research_2024",
            security_level=SecurityLevelEnum.INTERNAL,
            access_groups=["faculty", "students"]
        ),
        content=ContentMetadata(
            title="Test AI Research Paper",
            author="Prof. Test",
            content_type=ContentTypeEnum.DOCUMENT,
            format="pdf",
            creation_date=datetime.now(),
            version="1.0",
            language="en",
            tags=["ai", "research", "test"],
            keywords=["artificial intelligence", "research", "testing"]
        ),
        processing=ProcessingMetadata(
            api_used="openai_embeddings",
            confidence_score=0.92,
            model_version="text-embedding-3-large",
            processing_duration=5.0
        ),
        domain_specific=DomainSpecificMetadata(
            specialty="computer_science",
            subject_area="artificial_intelligence",
            priority="medium",
            status="published",
            related_entities=["research_papers"],
            custom_fields={"test": True}
        ),
        compliance=ComplianceMetadata(
            compliance_frameworks=["FERPA"],
            retention_date=datetime(2030, 12, 31),
            approved_by="Department Head",
            review_date=datetime(2025, 8, 1),
            anonymized=False
        )
    )

class TestPydanticMilvusDatabase:
    """Test class for Pydantic-based Milvus Database functionality"""
    
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
    
    def test_pydantic_document_insertion(self, db_with_collections, healthcare_document):
        """Test inserting a Pydantic document"""
        vector = generate_dummy_vector(1536)
        
        doc_id = db_with_collections.insert_document(
            collection_name="documents",
            vector=vector,
            metadata=healthcare_document,
            file_size=45000,
            content_hash="test_hash_pydantic_insert"
        )
        
        assert doc_id is not None
        assert isinstance(doc_id, str)
        assert len(doc_id) > 0
    
    def test_pydantic_metadata_search(self, db_with_collections, healthcare_document):
        """Test searching with Pydantic metadata"""
        vector = generate_dummy_vector(1536)
        
        # Insert document
        doc_id = db_with_collections.insert_document(
            collection_name="documents",
            vector=vector,
            metadata=healthcare_document,
            file_size=45000,
            content_hash="test_hash_search_pydantic"
        )
        
        assert doc_id is not None
        
        # Search by content hash to ensure we get our specific document
        results = db_with_collections.metadata_search(
            "documents",
            'content_hash == "test_hash_search_pydantic"',
            limit=5
        )
        
        assert isinstance(results, list)
        assert len(results) > 0, "Should find the document we just inserted"
        
        result = results[0]
        assert "metadata" in result
        assert isinstance(result["metadata"], dict), "Metadata should be a dictionary"
        assert "organizational" in result["metadata"], "Should have organizational metadata"
        assert result["metadata"]["organizational"]["organization_type"] == "healthcare"
    
    def test_pydantic_vector_search(self, db_with_collections, university_document):
        """Test vector search with Pydantic document"""
        vector = generate_dummy_vector(1536)
        
        # Insert document
        doc_id = db_with_collections.insert_document(
            collection_name="documents",
            vector=vector,
            metadata=university_document,
            file_size=32000,
            content_hash="test_hash_vector_pydantic"
        )
        
        assert doc_id is not None
        
        # Perform vector search using the same vector for exact match
        results = db_with_collections.vector_search(
            "documents",
            vector,  # Use same vector for higher similarity
            limit=3
        )
        
        assert isinstance(results, list)
        assert len(results) > 0, "Should find at least one result"
        
        # Check the first result for basic structure
        result = results[0]
        assert "id" in result
        assert "score" in result
        assert "metadata" in result
        
        # Check if metadata has the expected structure
        if isinstance(result["metadata"], dict) and "organizational" in result["metadata"]:
            org_type = result["metadata"]["organizational"]["organization_type"]
            assert org_type in ["university", "healthcare"], f"Expected university or healthcare, got {org_type}"
    
    def test_pydantic_hybrid_search(self, db_with_collections, healthcare_document):
        """Test hybrid search with Pydantic document"""
        vector = generate_dummy_vector(1536)
        
        # Insert document
        doc_id = db_with_collections.insert_document(
            collection_name="documents",
            vector=vector,
            metadata=healthcare_document,
            file_size=45000,
            content_hash="test_hash_hybrid_pydantic"
        )
        
        assert doc_id is not None
        
        # Perform hybrid search with organization type filter
        results = db_with_collections.hybrid_search(
            "documents",
            vector,  # Use same vector for higher similarity
            metadata_filter='organization_type == "healthcare"',
            limit=3
        )
        
        assert isinstance(results, list)
        assert len(results) > 0, "Should find healthcare documents"
        
        # Check that we found a healthcare document
        found_healthcare = False
        for result in results:
            if (isinstance(result["metadata"], dict) and 
                "organizational" in result["metadata"] and
                result["metadata"]["organizational"]["organization_type"] == "healthcare"):
                found_healthcare = True
                break
        
        assert found_healthcare, "Should find at least one healthcare document"
    
    def test_config_export_import(self):
        """Test configuration export and import"""
        db = MilvusVectorDatabase()
        
        # Test config export
        config_dict = db.get_config_dict()
        assert isinstance(config_dict, dict)
        assert "host" in config_dict
        assert "port" in config_dict
        assert "collections" in config_dict
        
        # Test creating database from config
        db2 = MilvusVectorDatabase.from_dict(config_dict)
        assert db2.host == db.host
        assert db2.port == db.port
    
    def test_collection_info(self, db_with_collections):
        """Test getting collection information"""
        info = db_with_collections.get_collection_info("documents")
        assert info is not None
        assert info["name"] == "documents"
        assert "description" in info
        assert "vector_dimension" in info
        assert "agentic_description" in info
        assert info["enabled"] is True
    
    def test_stats(self, db_with_collections):
        """Test getting collection statistics"""
        stats = db_with_collections.get_stats("documents")
        
        assert isinstance(stats, dict)
        if stats:
            assert "total_entities" in stats
            assert "collection_name" in stats
            assert stats["collection_name"] == "documents"

def test_pydantic_config_creation():
    """Test creating Pydantic configurations"""
    config = get_default_database_config()
    
    assert isinstance(config, DatabaseConfig)
    assert config.host == "localhost"
    assert config.port == 19530
    assert len(config.collections) == 4
    
    # Test collections
    assert "documents" in config.collections
    assert "images" in config.collections
    assert "audio_recordings" in config.collections
    assert "video_content" in config.collections
    
    # Test collection properties
    documents_config = config.collections["documents"]
    assert documents_config.vector_dim == 1536
    assert documents_config.enabled is True
    assert documents_config.description is not None
    assert documents_config.agentic_description is not None

if __name__ == "__main__":
    pytest.main([__file__]) 