#!/usr/bin/env python3
"""Demo script for Pydantic-based Milvus Vector Database"""

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

def generate_dummy_vector(dim: int) -> list:
    return [random.random() for _ in range(dim)]

def create_healthcare_document() -> DocumentMetadata:
    """Create a healthcare document with structured metadata"""
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
            title="Advanced Cardiac Life Support Protocol",
            author="Dr. Sarah Johnson",
            content_type=ContentTypeEnum.DOCUMENT,
            format="pdf",
            creation_date=datetime.now(),
            version="2.1",
            language="en",
            tags=["emergency", "cardiac", "protocol", "ACLS"],
            keywords=["cardiac arrest", "CPR", "defibrillation", "emergency response"]
        ),
        processing=ProcessingMetadata(
            api_used="openai_gpt4",
            confidence_score=0.95,
            model_version="gpt-4-turbo",
            processing_duration=12.5
        ),
        domain_specific=DomainSpecificMetadata(
            specialty="emergency_medicine",
            subject_area="cardiac_care",
            priority="critical",
            status="approved",
            related_entities=["cardiac_arrest_cases", "training_simulations"],
            custom_fields={
                "medical_code": "ICD-10-I46.9",
                "procedure_type": "life_saving",
                "training_required": True
            }
        ),
        compliance=ComplianceMetadata(
            compliance_frameworks=["HIPAA", "Joint_Commission"],
            retention_date=datetime(2029, 12, 31),
            approved_by="Chief Medical Officer",
            review_date=datetime(2025, 6, 15),
            anonymized=True
        ),
        relationships={
            "related_protocols": ["basic_life_support", "pediatric_acls"],
            "training_materials": ["acls_video_series", "simulation_scenarios"],
            "reference_cases": ["case_study_001", "case_study_002"]
        }
    )

def create_university_document() -> DocumentMetadata:
    """Create a university document with structured metadata"""
    return DocumentMetadata(
        organizational=OrganizationalMetadata(
            department="computer_science",
            role="professor",
            organization_type=OrganizationTypeEnum.UNIVERSITY,
            project_id="ai_research_2024",
            security_level=SecurityLevelEnum.INTERNAL,
            access_groups=["faculty", "graduate_students", "researchers"]
        ),
        content=ContentMetadata(
            title="Deep Learning Fundamentals Lecture Series",
            author="Prof. Michael Chen",
            content_type=ContentTypeEnum.DOCUMENT,
            format="pdf",
            creation_date=datetime.now(),
            version="1.0",
            language="en",
            tags=["machine_learning", "deep_learning", "neural_networks"],
            keywords=["backpropagation", "gradient_descent", "CNN", "RNN"]
        ),
        processing=ProcessingMetadata(
            api_used="openai_embeddings",
            confidence_score=0.92,
            model_version="text-embedding-3-large",
            processing_duration=8.3
        ),
        domain_specific=DomainSpecificMetadata(
            specialty="computer_science",
            subject_area="artificial_intelligence",
            priority="high",
            status="published",
            related_entities=["research_papers", "student_projects"],
            custom_fields={
                "course_code": "CS-7642",
                "semester": "Fall_2024",
                "citation_count": 0
            }
        ),
        compliance=ComplianceMetadata(
            compliance_frameworks=["FERPA", "University_Policy"],
            retention_date=datetime(2030, 12, 31),
            approved_by="Department Head",
            review_date=datetime(2025, 8, 1),
            anonymized=False
        )
    )

def demo_quick_start():
    """Quick start demo"""
    print("🚀 Quick Start Demo")
    print("=" * 30)
    
    # Create database
    db = MilvusVectorDatabase()
    
    if not db.connect():
        print("❌ Connection failed! Make sure Milvus is running.")
        return False
    
    # Create collections
    if not db.create_all_collections():
        print("❌ Failed to create collections!")
        return False
    
    print("✅ Connected and collections created!")
    
    # Insert healthcare document
    healthcare_doc = create_healthcare_document()
    healthcare_vector = generate_dummy_vector(1536)
    
    doc_id = db.insert_document(
        collection_name="documents",
        vector=healthcare_vector,
        metadata=healthcare_doc,
        file_size=45000,
        content_hash="healthcare_protocol_hash_123"
    )
    
    if doc_id:
        print(f"✅ Healthcare document inserted: {doc_id}")
    
    # Insert university document
    university_doc = create_university_document()
    university_vector = generate_dummy_vector(1536)
    
    doc_id2 = db.insert_document(
        collection_name="documents",
        vector=university_vector,
        metadata=university_doc,
        file_size=32000,
        content_hash="university_lecture_hash_456"
    )
    
    if doc_id2:
        print(f"✅ University document inserted: {doc_id2}")
    
    # Search examples
    print("\n🔍 Search Examples:")
    
    # Search by organization type
    healthcare_results = db.metadata_search(
        "documents",
        'organization_type == "healthcare"',
        limit=5
    )
    
    print(f"Found {len(healthcare_results)} healthcare documents")
    for result in healthcare_results:
        metadata = result.get('metadata', {})
        title = metadata.get('content', {}).get('title', 'Unknown')
        print(f"  - {title}")
    
    # Vector search
    query_vector = generate_dummy_vector(1536)
    vector_results = db.vector_search(
        "documents",
        query_vector,
        limit=3
    )
    
    print(f"\nFound {len(vector_results)} similar documents:")
    for i, result in enumerate(vector_results):
        metadata = result.get('metadata', {})
        title = metadata.get('content', {}).get('title', 'Unknown')
        print(f"  {i+1}. {title} (similarity: {result['score']:.3f})")
    
    # Get stats
    print(f"\n📊 Collection Statistics:")
    for collection_name in db.get_available_collections():
        stats = db.get_stats(collection_name)
        if stats:
            print(f"  {collection_name}: {stats['total_entities']} entities")
    
    db.disconnect()
    return True

def main():
    """Main demo function"""
    print("🎓 Pydantic-based Milvus Vector Database Demo")
    print("=" * 50)
    
    try:
        success = demo_quick_start()
        if success:
            print("\n🎉 Demo completed successfully!")
        else:
            print("\n❌ Demo failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Milvus is running: docker run -p 19530:19530 milvusdb/milvus:latest")

if __name__ == "__main__":
    main() 