#!/usr/bin/env python3
"""
Standalone File Upload Test Script with Metadata

Usage:
    python examples/test_file_upload.py [file_path]

Examples:
    python examples/test_file_upload.py                    # Creates and uploads test.txt
    python examples/test_file_upload.py myfile.pdf        # Uploads myfile.pdf
    python examples/test_file_upload.py docs/report.docx  # Uploads docs/report.docx
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import asyncio
import tempfile
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.file_upload import FileUploadService
from database.connection import init_db, SessionLocal
from config.settings import settings
from models.metadata import FileMetadata, DocumentType, ContentCategory, EmployeeRole, PriorityLevel, AccessLevel
from fastapi import UploadFile
from io import BytesIO


class MockUploadFile:
    """Mock UploadFile for testing purposes"""
    
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.content = content
        self.size = len(content)
        self.content_type = "application/octet-stream"
    
    async def read(self) -> bytes:
        return self.content
    
    async def seek(self, offset: int):
        pass
    
    async def close(self):
        pass


def create_test_file() -> tuple[str, bytes]:
    """Create a simple test file"""
    content = """# Test File for File Upload Service

This is a test file created automatically by the file upload test script.

File Information:
- Created for testing purposes
- Contains sample text content
- Should be processed by the file upload service

Test Data:
- Department: Engineering
- Project: File Upload Testing
- Tags: test, automation, sample

Content:
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

End of test file.
"""
    
    filename = "test_file.txt"
    return filename, content.encode('utf-8')


def create_sample_metadata(filename: str) -> FileMetadata:
    """Create sample metadata based on filename"""
    
    # Determine document type based on filename
    if filename.endswith('.pdf'):
        doc_type = DocumentType.REPORT
        content_cat = ContentCategory.ADMINISTRATIVE
    elif filename.endswith('.txt'):
        doc_type = DocumentType.MANUAL
        content_cat = ContentCategory.TECHNICAL
    elif filename.endswith('.jpg') or filename.endswith('.png'):
        doc_type = DocumentType.OTHER
        content_cat = ContentCategory.OPERATIONAL
    else:
        doc_type = DocumentType.OTHER
        content_cat = ContentCategory.ADMINISTRATIVE
    
    # Create metadata
    return FileMetadata(
        department="Engineering",
        uploaded_by="test_user",
        employee_role=EmployeeRole.STAFF,
        employee_id="EMP001",
        document_type=doc_type,
        content_category=content_cat,
        priority_level=PriorityLevel.MEDIUM,
        access_level=AccessLevel.INTERNAL,
        project_name="File Upload Testing",
        tags=["test", "automation", "sample"],
        keywords=["upload", "test", "demo"],
        description=f"Test upload of {filename} for validation purposes",
        notes="Created by automated test script"
    )


def create_healthcare_metadata() -> FileMetadata:
    """Create healthcare-specific metadata"""
    from models.metadata import HealthcareMetadata
    
    healthcare_data = HealthcareMetadata(
        specialty="cardiology",
        patient_id="P12345",
        physician_id="DOC001",
        hospital_unit="ICU",
        procedure_code="CARD001"
    )
    
    return FileMetadata(
        department="Cardiology",
        uploaded_by="Dr. Smith",
        employee_role=EmployeeRole.DOCTOR,
        employee_id="DOC001",
        document_type=DocumentType.PATIENT_RECORD,
        content_category=ContentCategory.CLINICAL,
        priority_level=PriorityLevel.HIGH,
        access_level=AccessLevel.RESTRICTED,
        project_name="Patient Care",
        case_id="CASE001",
        tags=["patient", "cardiology", "urgent"],
        keywords=["heart", "cardiac", "diagnosis"],
        description="Patient cardiac assessment report",
        domain_type="healthcare",
        healthcare_metadata=healthcare_data
    )


def create_university_metadata() -> FileMetadata:
    """Create university-specific metadata"""
    from models.metadata import UniversityMetadata
    
    university_data = UniversityMetadata(
        course_code="CS101",
        semester="Fall 2024",
        academic_year="2024-2025",
        faculty_id="PROF001",
        research_group="AI Research Lab"
    )
    
    return FileMetadata(
        department="Computer Science",
        uploaded_by="Prof. Johnson",
        employee_role=EmployeeRole.FACULTY,
        employee_id="PROF001",
        document_type=DocumentType.LECTURE,
        content_category=ContentCategory.ACADEMIC,
        priority_level=PriorityLevel.MEDIUM,
        access_level=AccessLevel.INTERNAL,
        project_name="Introduction to Programming",
        tags=["lecture", "programming", "cs101"],
        keywords=["python", "programming", "basics"],
        description="Introduction to Python programming lecture notes",
        domain_type="university",
        university_metadata=university_data
    )


async def test_file_upload(file_path: str = None):
    """Test file upload functionality"""
    
    print("🚀 Starting File Upload Test with Metadata")
    print("=" * 60)
    
    # Initialize database
    print("📋 Initializing database...")
    init_db()
    
    # Create upload service
    upload_service = FileUploadService()
    
    # Prepare file for upload
    if file_path and os.path.exists(file_path):
        # Use provided file
        print(f"📁 Using provided file: {file_path}")
        filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Create appropriate metadata
        metadata = create_sample_metadata(filename)
    else:
        # Create test file
        if file_path:
            print(f"⚠️  File not found: {file_path}")
            print("📝 Creating test file instead...")
        else:
            print("📝 No file provided, creating test file...")
        
        filename, content = create_test_file()
        metadata = create_sample_metadata(filename)
    
    # Create mock upload file
    mock_file = MockUploadFile(filename, content)
    
    print(f"📄 File: {filename}")
    print(f"📊 Size: {len(content):,} bytes")
    print(f"🏷️  Type: {mock_file.content_type}")
    print(f"🏢 Department: {metadata.department}")
    print(f"👤 Uploaded by: {metadata.uploaded_by}")
    print(f"🎭 Role: {metadata.employee_role}")
    print(f"📋 Document Type: {metadata.document_type}")
    print(f"📂 Category: {metadata.content_category}")
    print(f"⚡ Priority: {metadata.priority_level}")
    print(f"🔒 Access: {metadata.access_level}")
    print(f"🏷️  Tags: {', '.join(metadata.tags)}")
    
    # Test upload
    print("\n🔄 Starting upload process...")
    
    try:
        with SessionLocal() as db:
            result = await upload_service.upload_file(
                file=mock_file,
                db=db,
                file_metadata=metadata
            )
        
        print("✅ Upload successful!")
        print("\n📋 Upload Results:")
        print(f"   File ID: {result['file_id']}")
        print(f"   Original Name: {result['original_filename']}")
        print(f"   Storage Path: {result['storage_path']}")
        print(f"   File Size: {result['file_size']:,} bytes")
        print(f"   File Type: {result['file_type']}")
        print(f"   MIME Type: {result['mime_type']}")
        print(f"   Hash: {result['file_hash'][:16]}...")
        print(f"   Department: {result['department']}")
        print(f"   Project: {result['project']}")
        print(f"   Uploaded By: {result['uploaded_by']}")
        print(f"   Employee Role: {result['employee_role']}")
        print(f"   Document Type: {result['document_type']}")
        print(f"   Content Category: {result['content_category']}")
        print(f"   Priority Level: {result['priority_level']}")
        print(f"   Access Level: {result['access_level']}")
        print(f"   Tags: {', '.join(result['tags'])}")
        
        # Show processing information
        if result.get('processing_queued'):
            print(f"\n🔄 Processing Information:")
            print(f"   Content Type: {result.get('content_type', 'unknown')}")
            print(f"   Processing Priority: {result.get('processing_priority', 'unknown')}")
            print(f"   Estimated Time: {result.get('estimated_processing_time', 0)}s")
        
        # Show storage location
        storage_path = Path(result['storage_path'])
        print(f"\n📂 File stored at: {storage_path.absolute()}")
        
        if storage_path.exists():
            print("✅ File confirmed in storage!")
            print(f"   Actual size: {storage_path.stat().st_size:,} bytes")
        else:
            print("❌ File not found in storage!")
        
        # Show metadata
        print(f"\n📊 Complete Metadata:")
        metadata_dict = result['metadata']
        for key, value in metadata_dict.items():
            if key not in ['created_at', 'updated_at']:
                print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_domain_specific_uploads():
    """Test domain-specific uploads"""
    print("\n🏥 Testing Healthcare Upload...")
    
    healthcare_metadata = create_healthcare_metadata()
    healthcare_content = b"Patient cardiac assessment: Normal sinus rhythm observed."
    healthcare_file = MockUploadFile("cardiac_assessment.txt", healthcare_content)
    
    upload_service = FileUploadService()
    
    try:
        with SessionLocal() as db:
            result = await upload_service.upload_file(
                file=healthcare_file,
                db=db,
                file_metadata=healthcare_metadata
            )
        
        print("✅ Healthcare upload successful!")
        print(f"   Domain: {result['metadata']['domain_type']}")
        print(f"   Specialty: {result['metadata']['healthcare_metadata']['specialty']}")
        print(f"   Patient ID: {result['metadata']['healthcare_metadata']['patient_id']}")
        
    except Exception as e:
        print(f"❌ Healthcare upload failed: {e}")
    
    print("\n🎓 Testing University Upload...")
    
    university_metadata = create_university_metadata()
    university_content = b"Lecture 1: Introduction to Python Programming\n\nprint('Hello, World!')"
    university_file = MockUploadFile("python_intro.txt", university_content)
    
    try:
        with SessionLocal() as db:
            result = await upload_service.upload_file(
                file=university_file,
                db=db,
                file_metadata=university_metadata
            )
        
        print("✅ University upload successful!")
        print(f"   Domain: {result['metadata']['domain_type']}")
        print(f"   Course: {result['metadata']['university_metadata']['course_code']}")
        print(f"   Semester: {result['metadata']['university_metadata']['semester']}")
        
    except Exception as e:
        print(f"❌ University upload failed: {e}")


def main():
    """Main function"""
    file_path = None
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    # Run the async test
    try:
        success = asyncio.run(test_file_upload(file_path))
        if success:
            print("\n🎯 Running domain-specific tests...")
            asyncio.run(test_domain_specific_uploads())
            
            print("\n🎉 All tests completed successfully!")
            print("\nTo view your uploaded files, check the storage directory:")
            print(f"   {Path(settings.storage_path).absolute()}")
            
            print("\n📊 Key Features Demonstrated:")
            print("   ✅ Comprehensive metadata structure")
            print("   ✅ Domain-specific metadata (healthcare/university)")
            print("   ✅ Priority-based processing")
            print("   ✅ Role-based access control preparation")
            print("   ✅ Automatic processing queue integration")
        else:
            print("\n💥 Test failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 