#!/usr/bin/env python3
"""
CLI Usage Example for Pydantic-based Milvus Vector Database

This script demonstrates how to use the Milvus Vector Database system
with command-line interface examples.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
import argparse

def generate_dummy_vector(dim: int) -> list:
    """Generate random vector for testing"""
    return [random.random() for _ in range(dim)]

def create_sample_documents():
    """Create sample documents for different scenarios"""
    
    # Healthcare document
    healthcare_doc = DocumentMetadata(
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
            keywords=["cardiac arrest", "CPR", "defibrillation"]
        ),
        processing=ProcessingMetadata(
            api_used="openai_gpt4",
            confidence_score=0.95,
            model_version="gpt-4-turbo"
        ),
        domain_specific=DomainSpecificMetadata(
            specialty="emergency_medicine",
            subject_area="cardiac_care",
            priority="critical",
            status="approved",
            custom_fields={"medical_code": "ICD-10-I46.9"}
        ),
        compliance=ComplianceMetadata(
            compliance_frameworks=["HIPAA", "Joint_Commission"],
            approved_by="Chief Medical Officer",
            anonymized=True
        )
    )
    
    # University document  
    university_doc = DocumentMetadata(
        organizational=OrganizationalMetadata(
            department="computer_science",
            role="professor",
            organization_type=OrganizationTypeEnum.UNIVERSITY,
            project_id="ai_research_2024",
            security_level=SecurityLevelEnum.INTERNAL,
            access_groups=["faculty", "graduate_students"]
        ),
        content=ContentMetadata(
            title="Deep Learning Fundamentals Lecture",
            author="Prof. Michael Chen",
            content_type=ContentTypeEnum.DOCUMENT,
            format="pdf",
            creation_date=datetime.now(),
            version="1.0",
            language="en",
            tags=["machine_learning", "deep_learning"],
            keywords=["neural networks", "backpropagation"]
        ),
        processing=ProcessingMetadata(
            api_used="openai_embeddings",
            confidence_score=0.92,
            model_version="text-embedding-3-large"
        ),
        domain_specific=DomainSpecificMetadata(
            specialty="computer_science",
            subject_area="artificial_intelligence",
            priority="high",
            status="published",
            custom_fields={"course_code": "CS-7642"}
        ),
        compliance=ComplianceMetadata(
            compliance_frameworks=["FERPA", "University_Policy"],
            approved_by="Department Head",
            anonymized=False
        )
    )
    
    return healthcare_doc, university_doc

def setup_database():
    """Setup database connection and collections"""
    print("🔧 Setting up Milvus Vector Database...")
    
    db = MilvusVectorDatabase()
    
    if not db.connect():
        print("❌ Failed to connect to Milvus!")
        print("Make sure Milvus is running: docker run -p 19530:19530 milvusdb/milvus:latest")
        return None
    
    if not db.create_all_collections():
        print("❌ Failed to create collections!")
        return None
    
    print("✅ Database setup completed!")
    return db

def insert_sample_data(db):
    """Insert sample data into the database"""
    print("\n📝 Inserting sample data...")
    
    healthcare_doc, university_doc = create_sample_documents()
    
    # Insert healthcare document
    healthcare_vector = generate_dummy_vector(1536)
    doc_id1 = db.insert_document(
        collection_name="documents",
        vector=healthcare_vector,
        metadata=healthcare_doc,
        file_size=45000,
        content_hash="healthcare_hash_123"
    )
    
    if doc_id1:
        print(f"✅ Healthcare document inserted: {doc_id1[:8]}...")
    
    # Insert university document
    university_vector = generate_dummy_vector(1536)
    doc_id2 = db.insert_document(
        collection_name="documents",
        vector=university_vector,
        metadata=university_doc,
        file_size=32000,
        content_hash="university_hash_456"
    )
    
    if doc_id2:
        print(f"✅ University document inserted: {doc_id2[:8]}...")
    
    return doc_id1, doc_id2

def search_examples(db):
    """Demonstrate various search capabilities"""
    print("\n🔍 Search Examples:")
    
    # 1. Search by organization type
    print("\n1. Search by organization type (healthcare):")
    results = db.metadata_search(
        "documents",
        'organization_type == "healthcare"',
        limit=5
    )
    
    print(f"   Found {len(results)} healthcare documents:")
    for result in results:
        metadata = result.get('metadata', {})
        title = metadata.get('content', {}).get('title', 'Unknown')
        print(f"   - {title}")
    
    # 2. Search by security level
    print("\n2. Search by security level (confidential):")
    results = db.metadata_search(
        "documents",
        'security_level == "confidential"',
        limit=5
    )
    
    print(f"   Found {len(results)} confidential documents:")
    for result in results:
        metadata = result.get('metadata', {})
        title = metadata.get('content', {}).get('title', 'Unknown')
        print(f"   - {title}")
    
    # 3. Search by department and role
    print("\n3. Search by department and role:")
    results = db.metadata_search(
        "documents",
        'department == "emergency_medicine" and role == "attending_physician"',
        limit=5
    )
    
    print(f"   Found {len(results)} emergency medicine documents by attending physicians:")
    for result in results:
        metadata = result.get('metadata', {})
        title = metadata.get('content', {}).get('title', 'Unknown')
        print(f"   - {title}")
    
    # 4. Vector similarity search
    print("\n4. Vector similarity search:")
    query_vector = generate_dummy_vector(1536)
    results = db.vector_search(
        "documents",
        query_vector,
        limit=3
    )
    
    print(f"   Found {len(results)} similar documents:")
    for i, result in enumerate(results):
        metadata = result.get('metadata', {})
        title = metadata.get('content', {}).get('title', 'Unknown')
        print(f"   {i+1}. {title} (similarity: {result['score']:.3f})")
    
    # 5. Hybrid search (vector + metadata filter)
    print("\n5. Hybrid search (vector + metadata filter):")
    results = db.hybrid_search(
        "documents",
        query_vector,
        metadata_filter='organization_type == "healthcare"',
        limit=3
    )
    
    print(f"   Found {len(results)} similar healthcare documents:")
    for i, result in enumerate(results):
        metadata = result.get('metadata', {})
        title = metadata.get('content', {}).get('title', 'Unknown')
        print(f"   {i+1}. {title} (similarity: {result['score']:.3f})")

def show_statistics(db):
    """Show database statistics"""
    print("\n📊 Database Statistics:")
    
    # Organization info
    org_info = db.get_organization_info()
    print(f"   Organization Type: {org_info['organization_type']}")
    print(f"   Default Security Level: {org_info['default_security_level']}")
    print(f"   Audit Logging: {org_info['audit_logging_enabled']}")
    print(f"   Total Collections: {org_info['total_collections']}")
    print(f"   Enabled Collections: {org_info['enabled_collections']}")
    
    # Collection stats
    print("\n   Collection Statistics:")
    for collection_name in db.get_available_collections():
        stats = db.get_stats(collection_name)
        if stats:
            print(f"     {collection_name}: {stats['total_entities']} entities")
            print(f"       - Enabled: {stats['enabled']}")
            print(f"       - Vector Dimensions: {stats['vector_dimension']}")
            print(f"       - Content Types: {stats['content_types']}")

def configuration_example():
    """Show configuration examples"""
    print("\n⚙️  Configuration Examples:")
    
    # 1. Default configuration
    print("\n1. Default Configuration:")
    config = get_default_database_config()
    print(f"   Organization Type: {config.organization_type}")
    print(f"   Default Security Level: {config.default_security_level}")
    print(f"   Collections: {list(config.collections.keys())}")
    
    # 2. Custom configuration for university
    print("\n2. Custom Configuration for University:")
    config.organization_type = OrganizationTypeEnum.UNIVERSITY
    config.default_security_level = SecurityLevelEnum.INTERNAL
    config.collections["images"].enabled = False
    config.collections["audio_recordings"].enabled = False
    
    print(f"   Organization Type: {config.organization_type}")
    print(f"   Default Security Level: {config.default_security_level}")
    enabled_collections = [name for name, cfg in config.collections.items() if cfg.enabled]
    print(f"   Enabled Collections: {enabled_collections}")
    
    # 3. Export configuration (for UI integration)
    print("\n3. Configuration Export (for UI integration):")
    config_dict = config.model_dump()
    print(f"   Configuration exported with {len(config_dict)} keys")
    print(f"   Keys: {list(config_dict.keys())}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Milvus Vector Database CLI Example")
    parser.add_argument("--setup", action="store_true", help="Setup database and collections")
    parser.add_argument("--insert", action="store_true", help="Insert sample data")
    parser.add_argument("--search", action="store_true", help="Run search examples")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--config", action="store_true", help="Show configuration examples")
    parser.add_argument("--all", action="store_true", help="Run all examples")
    
    args = parser.parse_args()
    
    print("🎓 Milvus Vector Database CLI Usage Examples")
    print("=" * 60)
    
    if args.all or not any([args.setup, args.insert, args.search, args.stats, args.config]):
        # Run all examples if no specific flag is provided
        try:
            # Setup database
            db = setup_database()
            if not db:
                return
            
            # Insert sample data
            insert_sample_data(db)
            
            # Run search examples
            search_examples(db)
            
            # Show statistics
            show_statistics(db)
            
            # Show configuration examples
            configuration_example()
            
            # Cleanup
            db.disconnect()
            
            print("\n🎉 All examples completed successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Make sure Milvus is running: docker run -p 19530:19530 milvusdb/milvus:latest")
    
    else:
        # Run specific examples based on flags
        db = None
        
        if args.setup:
            db = setup_database()
        
        if args.insert and db:
            insert_sample_data(db)
        
        if args.search and db:
            search_examples(db)
        
        if args.stats and db:
            show_statistics(db)
        
        if args.config:
            configuration_example()
        
        if db:
            db.disconnect()

if __name__ == "__main__":
    main() 