#!/usr/bin/env python3
"""
Demo: File Processor (Simplified)
Shows content type classification and basic workflow routing
"""

import sys
import os
import asyncio
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.file_processor import ContentTypeClassifier, content_router, ProcessingJob
from src.services.content_types import ContentType
from src.models.metadata import (
    FileMetadata, DocumentType, ContentCategory, EmployeeRole, 
    PriorityLevel, AccessLevel, HealthcareMetadata, UniversityMetadata
)
from src.database.connection import get_db
from src.utils.logging import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


def create_test_metadata(name: str, domain: str = "generic") -> FileMetadata:
    """Create test metadata for demo files"""
    
    if domain == "healthcare":
        healthcare_data = HealthcareMetadata(
            specialty="cardiology",
            patient_id="P12345",
            physician_id="DOC001"
        )
        
        return FileMetadata(
            department="Cardiology",
            uploaded_by="Dr. Smith",
            employee_role=EmployeeRole.DOCTOR,
            document_type=DocumentType.PATIENT_RECORD,
            content_category=ContentCategory.CLINICAL,
            priority_level=PriorityLevel.URGENT,
            access_level=AccessLevel.RESTRICTED,
            project_name="Patient Care",
            tags=["patient", "cardiology", "urgent"],
            description=f"Medical record: {name}",
            domain_type="healthcare",
            healthcare_metadata=healthcare_data
        )
    
    elif domain == "university":
        university_data = UniversityMetadata(
            course_code="CS101",
            semester="Fall 2024",
            faculty_id="PROF001"
        )
        
        return FileMetadata(
            department="Computer Science",
            uploaded_by="Prof. Johnson",
            employee_role=EmployeeRole.FACULTY,
            document_type=DocumentType.LECTURE,
            content_category=ContentCategory.ACADEMIC,
            priority_level=PriorityLevel.HIGH,
            access_level=AccessLevel.INTERNAL,
            project_name="CS101 Course",
            tags=["lecture", "academic", "cs101"],
            description=f"Course material: {name}",
            domain_type="university",
            university_metadata=university_data
        )
    
    else:  # generic
        return FileMetadata(
            department="IT",
            uploaded_by="staff_user",
            employee_role=EmployeeRole.STAFF,
            document_type=DocumentType.REPORT,
            content_category=ContentCategory.ADMINISTRATIVE,
            priority_level=PriorityLevel.MEDIUM,
            access_level=AccessLevel.INTERNAL,
            project_name="Demo Project",
            tags=["demo", "test"],
            description=f"Demo file: {name}"
        )


async def demo_content_classification():
    """Demo content type classification"""
    print("🔍 CONTENT TYPE CLASSIFICATION DEMO")
    print("=" * 50)
    
    classifier = ContentTypeClassifier()
    
    test_files = [
        ("research_paper.pdf", "application/pdf"),
        ("profile_photo.jpg", "image/jpeg"),
        ("meeting_recording.mp3", "audio/mpeg"),
        ("training_video.mp4", "video/mp4"),
        ("notes.txt", "text/plain"),
        ("data.csv", "text/csv"),
        ("presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
        ("mystery_file.xyz", "application/octet-stream")
    ]
    
    for filename, mime_type in test_files:
        content_type = classifier.classify_file(filename, mime_type)
        print(f"📄 {filename:<20} → {content_type.value.upper()}")


async def demo_workflow_assignment():
    """Demo workflow assignment (simplified)"""
    print("\n⚙️  WORKFLOW ASSIGNMENT DEMO (SIMPLIFIED)")
    print("=" * 50)
    
    print("📋 TEXT files → TextWorkflow (keywords, summary, embeddings)")
    print("📋 DOCUMENT files → TextWorkflow (fallback)")
    print("📋 IMAGE files → Not implemented (hackathon scope)")
    print("📋 AUDIO files → Not implemented (hackathon scope)")
    print("📋 VIDEO files → Not implemented (hackathon scope)")
    print("📋 UNKNOWN files → TextWorkflow (fallback)")


async def demo_processing_examples():
    """Demo processing examples with different metadata"""
    print("\n📊 PROCESSING EXAMPLES (SIMPLIFIED)")
    print("=" * 50)
    
    db = next(get_db())
    
    # Example 1: Generic text file
    print("\n📄 Example 1: Generic Text File")
    print("-" * 30)
    
    generic_metadata = create_test_metadata("meeting_notes.txt", "generic")
    
    try:
        job = await content_router.route_file_for_processing(
            file_id="demo_001",
            file_path="/demo/meeting_notes.txt",
            filename="meeting_notes.txt",
            mime_type="text/plain",
            file_metadata=generic_metadata,
            db=db
        )
        
        print(f"✅ File routed successfully:")
        print(f"   📝 Content Type: {job.content_type.value}")
        print(f"   🏢 Department: {job.file_metadata.department}")
        print(f"   👤 Uploaded by: {job.file_metadata.uploaded_by}")
        print(f"   🎯 Priority: {job.priority}")
        print(f"   ⏱️  Estimated time: {job.workflow_metadata.get('estimated_time', 'unknown')}s")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Healthcare file
    print("\n🏥 Example 2: Healthcare File")
    print("-" * 30)
    
    healthcare_metadata = create_test_metadata("patient_record.txt", "healthcare")
    
    try:
        job = await content_router.route_file_for_processing(
            file_id="demo_002",
            file_path="/demo/patient_record.txt",
            filename="patient_record.txt",
            mime_type="text/plain",
            file_metadata=healthcare_metadata,
            db=db
        )
        
        print(f"✅ File routed successfully:")
        print(f"   📝 Content Type: {job.content_type.value}")
        print(f"   🏥 Department: {job.file_metadata.department}")
        print(f"   👨‍⚕️ Uploaded by: {job.file_metadata.uploaded_by}")
        print(f"   🚨 Priority: {job.priority} (urgent)")
        print(f"   🌐 Domain: {job.file_metadata.domain_type}")
        print(f"   🏥 Specialty: {job.file_metadata.healthcare_metadata.specialty}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: University file
    print("\n🎓 Example 3: University File")
    print("-" * 30)
    
    university_metadata = create_test_metadata("lecture_slides.txt", "university")
    
    try:
        job = await content_router.route_file_for_processing(
            file_id="demo_003",
            file_path="/demo/lecture_slides.txt",
            filename="lecture_slides.txt",
            mime_type="text/plain",
            file_metadata=university_metadata,
            db=db
        )
        
        print(f"✅ File routed successfully:")
        print(f"   📝 Content Type: {job.content_type.value}")
        print(f"   🎓 Department: {job.file_metadata.department}")
        print(f"   👨‍🏫 Uploaded by: {job.file_metadata.uploaded_by}")
        print(f"   ⚡ Priority: {job.priority}")
        print(f"   🌐 Domain: {job.file_metadata.domain_type}")
        print(f"   📚 Course: {job.file_metadata.university_metadata.course_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run the demo"""
    try:
        print("🚀 FILE PROCESSOR DEMO (SIMPLIFIED)")
        print("Content Type Classification and Workflow Routing")
        print("=" * 70)
        
        await demo_content_classification()
        await demo_workflow_assignment()
        await demo_processing_examples()
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETED!")
        print("🎯 Key Features Demonstrated:")
        print("   • Content type classification by file extension and MIME type")
        print("   • Simplified workflow routing (TEXT → TextWorkflow)")
        print("   • Domain-specific metadata handling (healthcare, university)")
        print("   • Priority assignment based on metadata")
        print("   • Ready for hackathon development!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")


if __name__ == "__main__":
    print("Starting File Processor Demo (Simplified)...")
    asyncio.run(main()) 