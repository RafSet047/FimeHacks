#!/usr/bin/env python3
"""
Demo: File Upload + Processing Integration with Metadata
Shows how upload automatically triggers processing with comprehensive metadata
"""

import asyncio
import sys
import os
import tempfile
import argparse
import mimetypes
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.file_upload import file_upload_service
from src.services.file_processor import content_router
from src.database.connection import get_db
from src.utils.logging import setup_logging
from src.models.metadata import FileMetadata, DocumentType, ContentCategory, EmployeeRole, PriorityLevel, AccessLevel, HealthcareMetadata, UniversityMetadata
from fastapi import UploadFile
from io import BytesIO
import logging

setup_logging()
logger = logging.getLogger(__name__)


def create_test_files():
    """Create simple test files for demo"""
    
    # Create a simple text file
    text_content = """
    This is a sample text document for testing the metadata-driven processing system.
    It contains some basic information about our enhanced file processing capabilities.
    
    Key features:
    - Comprehensive metadata structure
    - Domain-specific processing workflows
    - Priority-based processing queue
    - Role-based access control preparation
    - Background processing with detailed tracking
    
    This text should be processed quickly since it has priority 1.
    """
    
    # Create a simple "document" (HTML file treated as document)
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Research Paper with Metadata</title>
    </head>
    <body>
        <h1>Enhanced File Processing System</h1>
        <p>This is a sample research document for testing the document processing pipeline with metadata.</p>
        <p>It should be classified as a document and processed with priority based on metadata.</p>
        <h2>Features</h2>
        <ul>
            <li>Metadata-driven processing</li>
            <li>Domain-specific workflows</li>
            <li>Priority-based queue management</li>
            <li>Comprehensive audit trail</li>
        </ul>
    </body>
    </html>
    """
    
    return [
        ("sample_notes.txt", text_content.encode(), "text/plain"),
        ("research_paper.html", html_content.encode(), "text/html")
    ]


def create_sample_metadata(filename: str, priority: PriorityLevel = PriorityLevel.MEDIUM) -> FileMetadata:
    """Create sample metadata based on filename"""
    
    # Determine document type and category based on filename
    if "notes" in filename.lower():
        doc_type = DocumentType.MANUAL
        content_cat = ContentCategory.TECHNICAL
    elif "research" in filename.lower():
        doc_type = DocumentType.RESEARCH
        content_cat = ContentCategory.ACADEMIC
    else:
        doc_type = DocumentType.REPORT
        content_cat = ContentCategory.ADMINISTRATIVE
    
    return FileMetadata(
        department="Demo Department",
        uploaded_by="demo_user",
        employee_role=EmployeeRole.STAFF,
        employee_id="DEMO001",
        document_type=doc_type,
        content_category=content_cat,
        priority_level=priority,
        access_level=AccessLevel.INTERNAL,
        project_name="Integration Demo",
        tags=["demo", "test", "integration"],
        keywords=["processing", "metadata", "demo"],
        description=f"Demo upload of {filename} to test metadata integration",
        notes="Created by integration demo script"
    )


def create_healthcare_metadata() -> FileMetadata:
    """Create healthcare-specific metadata for demo"""
    healthcare_data = HealthcareMetadata(
        specialty="emergency",
        patient_id="DEMO123",
        physician_id="DR001",
        hospital_unit="ER",
        procedure_code="ER001"
    )
    
    return FileMetadata(
        department="Emergency",
        uploaded_by="Dr. Demo",
        employee_role=EmployeeRole.DOCTOR,
        employee_id="DR001",
        document_type=DocumentType.PATIENT_RECORD,
        content_category=ContentCategory.CLINICAL,
        priority_level=PriorityLevel.URGENT,
        access_level=AccessLevel.RESTRICTED,
        project_name="Patient Care",
        case_id="EMERGENCY001",
        tags=["patient", "emergency", "urgent"],
        keywords=["emergency", "treatment", "urgent"],
        description="Emergency department patient assessment",
        domain_type="healthcare",
        healthcare_metadata=healthcare_data
    )


def create_university_metadata() -> FileMetadata:
    """Create university-specific metadata for demo"""
    university_data = UniversityMetadata(
        course_code="DEMO101",
        semester="Fall 2024",
        academic_year="2024-2025",
        faculty_id="PROF001",
        research_group="Demo Research Lab"
    )
    
    return FileMetadata(
        department="Computer Science",
        uploaded_by="Prof. Demo",
        employee_role=EmployeeRole.FACULTY,
        employee_id="PROF001",
        document_type=DocumentType.LECTURE,
        content_category=ContentCategory.ACADEMIC,
        priority_level=PriorityLevel.HIGH,
        access_level=AccessLevel.INTERNAL,
        project_name="Demo Course",
        tags=["lecture", "demo", "academic"],
        keywords=["teaching", "education", "demo"],
        description="Demo lecture materials for integration testing",
        domain_type="university",
        university_metadata=university_data
    )


async def simulate_file_upload(filename: str, content: bytes, content_type: str):
    """Simulate file upload using UploadFile"""
    
    # Create a mock UploadFile
    file_obj = BytesIO(content)
    
    class MockUploadFile:
        def __init__(self, filename, content, content_type):
            self.filename = filename
            self.content = content
            self.content_type = content_type
            self._file = BytesIO(content)
            
        async def read(self):
            return self.content
            
        async def seek(self, position):
            self._file.seek(position)
    
    return MockUploadFile(filename, content, content_type)


def load_cli_file(file_path: str):
    """Load a file from CLI argument"""
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Guess MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"
        
        return [(file_path.name, content, mime_type)]
        
    except Exception as e:
        print(f"❌ Error loading file {file_path}: {e}")
        return []


async def demo_upload_and_process(cli_file_path: str = None):
    """Main demo function"""
    print("🚀 UPLOAD + PROCESSING INTEGRATION DEMO WITH METADATA")
    print("=" * 70)
    
    # Get database session
    db = next(get_db())
    
    # Prepare files and metadata
    if cli_file_path:
        print(f"📁 Using CLI file: {cli_file_path}")
        test_files = load_cli_file(cli_file_path)
        if not test_files:
            print("❌ Failed to load CLI file. Using default test files instead.")
            test_files = create_test_files()
    else:
        print("📁 Using default test files")
        test_files = create_test_files()
    
    # Create different metadata scenarios
    metadata_scenarios = [
        create_sample_metadata("sample_notes.txt", PriorityLevel.MEDIUM),
        create_sample_metadata("research_paper.html", PriorityLevel.HIGH),
        create_healthcare_metadata(),
        create_university_metadata()
    ]
    
    uploaded_files = []
    
    print("\n📤 UPLOADING FILES WITH METADATA...")
    print("-" * 40)
    
    # Upload files with different metadata
    for i, (filename, content, content_type) in enumerate(test_files):
        try:
            # Create mock upload file
            upload_file = await simulate_file_upload(filename, content, content_type)
            
            # Use appropriate metadata (cycle through scenarios)
            metadata = metadata_scenarios[i % len(metadata_scenarios)]
            
            # Upload the file
            print(f"📁 Uploading: {filename}")
            print(f"   📊 Department: {metadata.department}")
            print(f"   👤 Uploaded by: {metadata.uploaded_by} ({metadata.employee_role.value})")
            print(f"   📋 Type: {metadata.document_type.value}")
            print(f"   ⚡ Priority: {metadata.priority_level.value}")
            print(f"   🔒 Access: {metadata.access_level.value}")
            print(f"   🌐 Domain: {metadata.domain_type or 'generic'}")
            
            result = await file_upload_service.upload_file(
                file=upload_file,
                db=db,
                file_metadata=metadata
            )
            
            if result["success"]:
                uploaded_files.append(result)
                print(f"   ✅ Success: {result['file_id']}")
                print(f"   📦 Size: {result['file_size']} bytes")
                print(f"   🏷️  MIME Type: {result['mime_type']}")
                print(f"   📋 Content Type: {result.get('content_type', 'unknown')}")
                print(f"   ⏰ Processing Priority: {result.get('processing_priority', 'unknown')}")
                print(f"   🔄 Processing Queued: {result.get('processing_queued', False)}")
            else:
                print(f"   ❌ Failed: {result['errors']}")
                
        except Exception as e:
            print(f"   ❌ Error uploading {filename}: {e}")
        
        print()
    
    print(f"📊 PROCESSING QUEUE STATUS")
    print("-" * 40)
    
    # Check queue status
    queue_status = await content_router.get_processing_status()
    print(f"📋 Pending Jobs: {queue_status['pending_jobs']}")
    print(f"🔄 Active Jobs: {queue_status['active_jobs']}")
    print(f"✅ Completed Jobs: {queue_status['completed_jobs']}")
    print(f"❌ Failed Jobs: {queue_status['failed_jobs']}")
    
    print(f"\n🔄 PROCESSING JOBS...")
    print("-" * 40)
    
    # Process the jobs
    processed_count = 0
    max_attempts = 10
    
    while processed_count < len(uploaded_files) and max_attempts > 0:
        try:
            job = await content_router.process_next_job(db)
            
            if job:
                print(f"⚡ Processing: {job.file_id}")
                print(f"   📝 Content Type: {job.content_type.value}")
                print(f"   🏢 Department: {job.file_metadata.department}")
                print(f"   👤 Uploaded by: {job.file_metadata.uploaded_by}")
                print(f"   🎭 Role: {job.file_metadata.employee_role.value}")
                print(f"   🌐 Domain: {job.file_metadata.domain_type or 'generic'}")
                print(f"   🎯 Processing Priority: {job.priority}")
                print(f"   📋 Steps: {' → '.join(job.workflow_metadata.get('steps', []))}")
                print(f"   ⏱️  Duration: {job.processing_metadata.processing_duration_seconds:.2f}s")
                print(f"   🔧 APIs Used: {', '.join(job.processing_metadata.apis_used or [])}")
                print(f"   ✅ Status: {job.status.value}")
                processed_count += 1
            else:
                print("⏸️  No jobs available to process")
                break
                
        except Exception as e:
            print(f"❌ Error processing job: {e}")
            
        max_attempts -= 1
        await asyncio.sleep(0.5)
        print()
    
    print(f"📊 FINAL RESULTS")
    print("-" * 40)
    
    # Final queue status
    final_status = await content_router.get_processing_status()
    print(f"✅ Completed Jobs: {final_status['completed_jobs']}")
    print(f"⏸️  Pending Jobs: {final_status['pending_jobs']}")
    print(f"❌ Failed Jobs: {final_status['failed_jobs']}")
    
    # Show file details
    print(f"\n📁 UPLOADED FILES SUMMARY")
    print("-" * 40)
    
    for result in uploaded_files:
        metadata = result['metadata']
        print(f"📄 {result['original_filename']}")
        print(f"   🆔 ID: {result['file_id']}")
        print(f"   📦 Size: {result['file_size']} bytes")
        print(f"   🏷️  Type: {result['file_type']}")
        print(f"   🏢 Department: {metadata['department']}")
        print(f"   👤 Uploaded by: {metadata['uploaded_by']}")
        print(f"   🎭 Role: {metadata['employee_role']}")
        print(f"   ⚡ Priority: {metadata['priority_level']}")
        print(f"   🌐 Domain: {metadata.get('domain_type', 'generic')}")
        print(f"   🔄 Processing: {result.get('processing_queued', False)}")
        print()


async def main():
    """Run the demo"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Upload + Processing Integration Demo with Metadata")
    parser.add_argument(
        "--file", 
        type=str, 
        help="Path to a file to upload and process (optional)"
    )
    parser.add_argument(
        "-f",
        type=str,
        dest="file",
        help="Short form of --file"
    )
    
    args = parser.parse_args()
    
    try:
        await demo_upload_and_process(args.file)
        
        print("=" * 70)
        print("✅ DEMO COMPLETED!")
        print("🎯 Key Observations:")
        print("   • Files uploaded with comprehensive metadata structure")
        print("   • Processing priority determined by metadata priority level")
        print("   • Domain-specific processing steps added automatically")
        print("   • Healthcare files get medical entity extraction")
        print("   • University files get academic content analysis")
        print("   • Role and department information tracked throughout")
        print("   • Processing metadata captured for audit trail")
        print("   • System ready for search integration with metadata")
        
        if args.file:
            print(f"   • Your file: {args.file} was processed with metadata!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")


if __name__ == "__main__":
    print("Starting Upload + Processing Demo with Metadata...")
    print("💡 Usage:")
    print("   python examples/demo_upload_and_process.py                    # Use default test files")
    print("   python examples/demo_upload_and_process.py --file myfile.txt  # Upload your own file")
    print("   python examples/demo_upload_and_process.py -f myfile.pdf      # Short form")
    print()
    asyncio.run(main()) 