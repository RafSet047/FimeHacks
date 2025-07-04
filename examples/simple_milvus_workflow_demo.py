#!/usr/bin/env python3
"""
Simple Milvus Workflow Demo

This example demonstrates:
1. Creating sample healthcare and university files
2. Processing them with TextWorkflow to generate embeddings
3. Storing the data in Milvus database
4. Performing vector search, metadata search, and hybrid search
5. Displaying results

Run with: python examples/simple_milvus_workflow_demo.py
"""

import sys
import os
from pathlib import Path
import tempfile
import uuid
from datetime import datetime

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.workflows.text_workflow import TextWorkflow
from src.services.workflow_base import WorkflowInput
from src.database.milvus_db import MilvusVectorDatabase
from src.database.config import (
    DocumentMetadata, OrganizationalMetadata, ContentMetadata, 
    ProcessingMetadata, DomainSpecificMetadata, ComplianceMetadata,
    OrganizationTypeEnum, ContentTypeEnum, SecurityLevelEnum
)
from src.models.metadata import (
    FileMetadata, DocumentType, ContentCategory, PriorityLevel, 
    AccessLevel, EmployeeRole, HealthcareMetadata, UniversityMetadata
)

def create_sample_files():
    """Create sample healthcare and university files"""
    temp_dir = tempfile.mkdtemp()
    
    # Healthcare file content
    healthcare_content = """
EMERGENCY CARDIAC PROTOCOL - St. Mary's Hospital

Patient Assessment Guidelines:
- Check vital signs immediately upon arrival
- Obtain ECG within 10 minutes for chest pain complaints
- Administer oxygen if SpO2 < 94%
- Establish IV access for medication administration

Treatment Protocol:
1. Assess airway, breathing, circulation
2. Administer aspirin 325mg if no contraindications
3. Obtain cardiac enzymes and complete metabolic panel
4. Contact cardiology for STEMI alerts
5. Prepare for potential catheterization

Emergency Contacts:
- Cardiology: ext. 4567
- ICU: ext. 2345
- Pharmacy: ext. 6789

This protocol is approved by Dr. Johnson, Chief of Cardiology.
Last updated: January 2024
HIPAA compliant - confidential medical information.
    """
    
    # University file content
    university_content = """
COMPUTER SCIENCE 101 - Introduction to Programming

Course Syllabus - Spring 2024

Instructor: Prof. Sarah Chen
Office Hours: Tuesday/Thursday 2-4 PM
Email: s.chen@university.edu

Course Objectives:
Students will learn fundamental programming concepts including:
- Variables and data types
- Control structures (loops, conditionals)
- Functions and modular programming
- Basic algorithms and problem solving
- Introduction to object-oriented programming

Assignments:
- Weekly programming exercises (40%)
- Midterm exam (25%)
- Final project (25%)
- Class participation (10%)

Required Textbook:
"Python Programming for Beginners" by Smith & Jones
ISBN: 978-1234567890

Academic Integrity:
All work must be original. Plagiarism will result in course failure.
Collaboration is encouraged on homework but each student must submit individual work.

FERPA compliance: Student records are confidential.
    """
    
    # Write files
    healthcare_file = os.path.join(temp_dir, "healthcare_protocol.txt")
    university_file = os.path.join(temp_dir, "cs101_syllabus.txt")
    
    with open(healthcare_file, 'w') as f:
        f.write(healthcare_content)
    
    with open(university_file, 'w') as f:
        f.write(university_content)
    
    return healthcare_file, university_file, temp_dir

def process_with_workflow(file_path: str, file_id: str, domain_type: str):
    """Process file using TextWorkflow"""
    print(f"\n📄 Processing file: {os.path.basename(file_path)}")
    
    # Create appropriate metadata based on domain type
    if domain_type == "healthcare":
        file_metadata = FileMetadata(
            department="emergency_medicine",
            uploaded_by="demo_user",
            employee_role=EmployeeRole.DOCTOR,
            document_type=DocumentType.PROTOCOL,
            content_category=ContentCategory.CLINICAL,
            priority_level=PriorityLevel.HIGH,
            access_level=AccessLevel.CONFIDENTIAL,
            domain_type="healthcare",
            healthcare_metadata=HealthcareMetadata(
                specialty="emergency_medicine",
                hospital_unit="emergency_room"
            ),
            tags=["protocol", "emergency", "cardiac"],
            keywords=["emergency", "protocol", "cardiac", "treatment"]
        )
    else:  # university
        file_metadata = FileMetadata(
            department="computer_science",
            uploaded_by="demo_professor",
            employee_role=EmployeeRole.FACULTY,
            document_type=DocumentType.LECTURE,
            content_category=ContentCategory.ACADEMIC,
            priority_level=PriorityLevel.MEDIUM,
            access_level=AccessLevel.INTERNAL,
            domain_type="university",
            university_metadata=UniversityMetadata(
                course_code="CS101",
                semester="Spring",
                academic_year="2024"
            ),
            tags=["syllabus", "programming", "cs101"],
            keywords=["programming", "computer", "science", "course"]
        )
    
    workflow = TextWorkflow()
    workflow_input = WorkflowInput(
        file_id=file_id,
        file_path=file_path,
        filename=os.path.basename(file_path),
        mime_type="text/plain",
        file_metadata=file_metadata
    )
    
    result = workflow.process(workflow_input)
    
    if result.success:
        print(f"✅ Processing successful in {result.processing_time:.2f}s")
        print(f"   Word count: {result.structured_data['word_count']}")
        print(f"   Keywords: {', '.join(result.structured_data['keywords'][:5])}...")
        print(f"   Embeddings: {len(result.embeddings)} chunks generated")
    else:
        print(f"❌ Processing failed: {result.error_message}")
    
    return result

def create_document_metadata(workflow_result, org_type: OrganizationTypeEnum, 
                           department: str, specialty: str, compliance_frameworks: list):
    """Convert workflow result to DocumentMetadata for Milvus"""
    
    return DocumentMetadata(
        organizational=OrganizationalMetadata(
            department=department,
            role="system_user",
            organization_type=org_type,
            project_id=f"demo_project_{org_type.value}",
            security_level=SecurityLevelEnum.INTERNAL,
            access_groups=["demo_users"]
        ),
        content=ContentMetadata(
            title=f"Demo {org_type.value.title()} Document",
            author="Demo System",
            content_type=ContentTypeEnum.DOCUMENT,
            format="txt",
            creation_date=datetime.now(),
            version="1.0",
            language="en",
            tags=workflow_result.structured_data['keywords'][:5],
            keywords=workflow_result.structured_data['keywords']
        ),
        processing=ProcessingMetadata(
            api_used="text_workflow",
            confidence_score=0.95,
            model_version="demo_v1.0",
            processing_duration=workflow_result.processing_time
        ),
        domain_specific=DomainSpecificMetadata(
            specialty=specialty,
            subject_area=department,
            priority="medium",
            status="processed",
            related_entities=["demo"],
            custom_fields={"demo": True, "workflow_version": "1.0"}
        ),
        compliance=ComplianceMetadata(
            compliance_frameworks=compliance_frameworks,
            retention_date=datetime(2025, 12, 31),
            approved_by="Demo Administrator",
            review_date=datetime(2025, 6, 1),
            anonymized=False
        )
    )

def perform_searches(db: MilvusVectorDatabase, query_vector: list):
    """Perform all types of searches and display results"""
    
    print("\n🔍 PERFORMING SEARCHES")
    print("=" * 50)
    
    # 1. Vector Search
    print("\n1. 🎯 Vector Similarity Search:")
    vector_results = db.vector_search("documents", query_vector, limit=3)
    
    if vector_results:
        for i, result in enumerate(vector_results, 1):
            org_type = result.get('organization_type', 'unknown')
            dept = result.get('department', 'unknown')
            score = result.get('score', 0)
            print(f"   Result {i}: {org_type} - {dept} (similarity: {score:.3f})")
    else:
        print("   No results found")
    
    # 2. Metadata Search - Healthcare
    print("\n2. 🏥 Metadata Search - Healthcare Documents:")
    healthcare_results = db.metadata_search(
        "documents", 
        'organization_type == "healthcare"', 
        limit=5
    )
    
    if healthcare_results:
        for i, result in enumerate(healthcare_results, 1):
            title = "Unknown"
            if isinstance(result.get('metadata'), dict):
                title = result['metadata'].get('content', {}).get('title', 'Unknown')
            print(f"   Result {i}: {title}")
    else:
        print("   No healthcare documents found")
    
    # 3. Metadata Search - University
    print("\n3. 🎓 Metadata Search - University Documents:")
    university_results = db.metadata_search(
        "documents", 
        'organization_type == "university"', 
        limit=5
    )
    
    if university_results:
        for i, result in enumerate(university_results, 1):
            title = "Unknown"
            if isinstance(result.get('metadata'), dict):
                title = result['metadata'].get('content', {}).get('title', 'Unknown')
            print(f"   Result {i}: {title}")
    else:
        print("   No university documents found")
    
    # 4. Hybrid Search
    print("\n4. 🔗 Hybrid Search - Vector + Metadata Filter:")
    hybrid_results = db.hybrid_search(
        "documents",
        query_vector,
        metadata_filter='security_level == "internal"',
        limit=3
    )
    
    if hybrid_results:
        for i, result in enumerate(hybrid_results, 1):
            org_type = result.get('organization_type', 'unknown')
            security = result.get('security_level', 'unknown')
            score = result.get('score', 0)
            print(f"   Result {i}: {org_type} - {security} (score: {score:.3f})")
    else:
        print("   No results found")
    
    # 5. Collection Statistics
    print("\n5. 📊 Collection Statistics:")
    stats = db.get_stats("documents")
    if stats:
        print(f"   Total documents: {stats.get('total_entities', 0)}")
        print(f"   Collection: {stats.get('collection_name', 'unknown')}")
        print(f"   Vector dimension: {stats.get('vector_dimension', 'unknown')}")
    else:
        print("   No statistics available")

def main():
    """Main demonstration function"""
    
    print("🚀 SIMPLE MILVUS WORKFLOW DEMO")
    print("=" * 50)
    
    try:
        # Step 1: Create sample files
        print("\n📁 Creating sample files...")
        healthcare_file, university_file, temp_dir = create_sample_files()
        print(f"✅ Created files in: {temp_dir}")
        
        # Step 2: Initialize Milvus database
        print("\n🗄️  Initializing Milvus database...")
        db = MilvusVectorDatabase()
        
        if not db.connect():
            print("❌ Failed to connect to Milvus")
            return
        
        print("✅ Connected to Milvus Lite")
        
        # Create collections
        if not db.create_all_collections():
            print("❌ Failed to create collections")
            return
        
        print("✅ Collections created")
        
        # Step 3: Process files with TextWorkflow
        print("\n⚙️  Processing files with TextWorkflow...")
        
        # Process healthcare file
        healthcare_id = str(uuid.uuid4())
        healthcare_result = process_with_workflow(healthcare_file, healthcare_id, "healthcare")
        
        # Process university file
        university_id = str(uuid.uuid4())
        university_result = process_with_workflow(university_file, university_id, "university")
        
        if not (healthcare_result.success and university_result.success):
            print("❌ File processing failed")
            return
        
        # Step 4: Convert to Milvus format and insert
        print("\n💾 Storing data in Milvus...")
        
        # Healthcare document
        healthcare_metadata = create_document_metadata(
            healthcare_result,
            OrganizationTypeEnum.HEALTHCARE,
            "emergency_medicine",
            "emergency_protocols",
            ["HIPAA"]
        )
        
        # Use first embedding chunk for simplicity
        healthcare_vector = healthcare_result.embeddings[0] if healthcare_result.embeddings else [0.0] * 384
        # Pad or truncate to 1536 dimensions for documents collection
        healthcare_vector = (healthcare_vector + [0.0] * 1536)[:1536]
        
        healthcare_doc_id = db.insert_document(
            collection_name="documents",
            vector=healthcare_vector,
            metadata=healthcare_metadata,
            file_size=len(healthcare_result.extracted_content),
            content_hash=f"hash_{healthcare_id}"
        )
        
        # University document
        university_metadata = create_document_metadata(
            university_result,
            OrganizationTypeEnum.UNIVERSITY,
            "computer_science",
            "programming_education",
            ["FERPA"]
        )
        
        university_vector = university_result.embeddings[0] if university_result.embeddings else [0.0] * 384
        university_vector = (university_vector + [0.0] * 1536)[:1536]
        
        university_doc_id = db.insert_document(
            collection_name="documents",
            vector=university_vector,
            metadata=university_metadata,
            file_size=len(university_result.extracted_content),
            content_hash=f"hash_{university_id}"
        )
        
        if healthcare_doc_id and university_doc_id:
            print("✅ Documents stored successfully")
            print(f"   Healthcare doc ID: {healthcare_doc_id[:8]}...")
            print(f"   University doc ID: {university_doc_id[:8]}...")
        else:
            print("❌ Failed to store documents")
            return
        
        # Step 5: Perform searches
        query_vector = healthcare_vector  # Use healthcare vector as query
        perform_searches(db, query_vector)
        
        print("\n🎉 Demo completed successfully!")
        
        # Cleanup
        db.disconnect()
        
        # Remove temp files
        import shutil
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up temporary files")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 