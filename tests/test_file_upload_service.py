#!/usr/bin/env python3
"""
File Upload Service Tests for Step 2.1
pytest-compatible test suite for file upload service functionality.
"""

import os
import sys
import asyncio
import tempfile
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.services.file_upload import FileValidator, FileStorage, FileUploadService
from src.database.connection import get_db, init_db
from src.config.settings import settings
from src.database.crud import file_crud
from src.models.metadata import FileMetadata, DocumentType, ContentCategory, EmployeeRole, PriorityLevel, AccessLevel


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize database for all tests"""
    init_db()


@pytest.fixture
def validator():
    """Create FileValidator instance"""
    return FileValidator()


@pytest.fixture
def storage():
    """Create FileStorage instance"""
    return FileStorage()


@pytest.fixture
def upload_service():
    """Create FileUploadService instance"""
    return FileUploadService()


@pytest.fixture
def test_content():
    """Test file content"""
    return b"Hello, World! This is a test file."


@pytest.fixture
def test_metadata():
    """Test file metadata"""
    return FileMetadata(
        department="test_department",
        uploaded_by="test_user",
        employee_role=EmployeeRole.STAFF,
        document_type=DocumentType.REPORT,
        content_category=ContentCategory.ADMINISTRATIVE,
        priority_level=PriorityLevel.MEDIUM,
        access_level=AccessLevel.INTERNAL,
        project_name="test_project",
        tags=["test", "validation", "automated"],
        description="Test file for validation"
    )


@pytest.fixture
def db_session():
    """Database session for tests"""
    db = next(get_db())
    yield db
    db.close()


class TestFileValidator:
    """Test FileValidator functionality"""
    
    def test_validate_file_extension_valid(self, validator):
        """Test valid file extension"""
        assert validator.validate_file_extension("test.txt") is True
    
    def test_validate_file_extension_invalid(self, validator):
        """Test invalid file extension"""
        assert validator.validate_file_extension("test.exe") is False
    
    def test_validate_file_size_valid(self, validator):
        """Test valid file size"""
        assert validator.validate_file_size(1024) is True
    
    def test_validate_file_size_invalid(self, validator):
        """Test invalid file size"""
        assert validator.validate_file_size(settings.max_file_size + 1) is False
    
    def test_detect_file_type(self, validator, test_content):
        """Test file type detection"""
        type_info = validator.detect_file_type(test_content, "test.txt")
        assert type_info['mime_type'] == "text/plain"
        assert type_info['extension'] == "txt"
    
    def test_comprehensive_validation_valid(self, validator, test_content):
        """Test comprehensive file validation with valid file"""
        result = validator.validate_file("test.txt", 1024, test_content)
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_comprehensive_validation_invalid_extension(self, validator, test_content):
        """Test comprehensive file validation with invalid extension"""
        result = validator.validate_file("test.exe", 1024, test_content)
        assert result['valid'] is False
        assert len(result['errors']) > 0


class TestFileStorage:
    """Test FileStorage functionality"""
    
    def test_generate_file_id(self, storage):
        """Test file ID generation"""
        file_id = storage.generate_file_id()
        assert isinstance(file_id, str)
        assert len(file_id) > 0
    
    def test_generate_file_path(self, storage):
        """Test file path generation"""
        file_id = storage.generate_file_id()
        file_path = storage.generate_file_path(file_id, "test.txt")
        assert isinstance(file_path, Path)
        assert str(file_path).endswith(f"{file_id}.txt")
    
    def test_calculate_file_hash(self, storage, test_content):
        """Test file hash calculation"""
        file_hash = storage.calculate_file_hash(test_content)
        assert isinstance(file_hash, str)
        assert len(file_hash) == 64  # SHA-256 hash length
    
    @pytest.mark.asyncio
    async def test_save_and_delete_file(self, storage, test_content):
        """Test file saving and deletion"""
        file_id = storage.generate_file_id()
        
        # Test file saving
        save_result = await storage.save_file(file_id, "test.txt", test_content)
        assert save_result['storage_success'] is True
        assert os.path.exists(save_result['file_path'])
        
        # Test file deletion
        delete_result = await storage.delete_file(save_result['file_path'])
        assert delete_result is True
        assert not os.path.exists(save_result['file_path'])


class TestDatabaseIntegration:
    """Test database integration"""
    
    def test_create_and_retrieve_file_record(self, db_session, storage, test_content, test_metadata):
        """Test creating and retrieving file records"""
        file_id = storage.generate_file_id()
        file_path = storage.generate_file_path(file_id, "test.txt")
        
        test_file_data = {
            "file_id": file_id,
            "filename": f"{file_id}.txt",
            "original_filename": "test.txt",
            "file_path": str(file_path),
            "file_size": len(test_content),
            "file_type": "txt",
            "mime_type": "text/plain",
            "status": "uploaded",
            "department": test_metadata.department,
            "project": test_metadata.project_name,
            "tags": ",".join(test_metadata.tags),
            "file_metadata": test_metadata.to_dict()
        }
        
        # Create file record
        db_file = file_crud.create_file(db_session, test_file_data)
        assert db_file.id is not None
        assert db_file.file_id == file_id
        assert db_file.file_metadata is not None
        assert db_file.file_metadata["department"] == test_metadata.department
        
        # Test file retrieval
        retrieved_file = file_crud.get_file_by_id(db_session, file_id)
        assert retrieved_file is not None
        assert retrieved_file.filename == f"{file_id}.txt"
        assert retrieved_file.file_metadata["uploaded_by"] == test_metadata.uploaded_by
        
        # Clean up
        file_crud.delete_file(db_session, file_id)
    
    @pytest.mark.asyncio
    async def test_file_info_service(self, upload_service, db_session, storage, test_content, test_metadata):
        """Test file info service"""
        file_id = storage.generate_file_id()
        file_path = storage.generate_file_path(file_id, "test.txt")
        
        test_file_data = {
            "file_id": file_id,
            "filename": f"{file_id}.txt",
            "original_filename": "test.txt",
            "file_path": str(file_path),
            "file_size": len(test_content),
            "file_type": "txt",
            "mime_type": "text/plain",
            "status": "uploaded",
            "department": test_metadata.department,
            "project": test_metadata.project_name,
            "tags": ",".join(test_metadata.tags),
            "file_metadata": test_metadata.to_dict()
        }
        
        # Create file record
        file_crud.create_file(db_session, test_file_data)
        
        # Test file info service
        file_info = await upload_service.get_file_info(file_id, db_session)
        assert file_info is not None
        assert file_info['original_filename'] == "test.txt"
        assert file_info['file_id'] == file_id
        assert file_info['metadata']['department'] == test_metadata.department
        
        # Clean up
        file_crud.delete_file(db_session, file_id)


class TestCompleteUploadWorkflow:
    """Test complete upload workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_upload_workflow(self, upload_service, db_session, test_content, test_metadata):
        """Test complete file upload workflow"""
        
        # Mock UploadFile
        class MockUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self._content = content
                self._position = 0
            
            async def read(self):
                return self._content
            
            async def seek(self, position):
                self._position = position
        
        mock_file = MockUploadFile("test_upload.txt", test_content)
        
        # Test upload
        result = await upload_service.upload_file(
            file=mock_file,
            db=db_session,
            file_metadata=test_metadata
        )
        
        assert result['success'] is True
        assert 'file_id' in result
        assert result['filename'] == "test_upload.txt"
        assert result['file_type'] == "txt"
        assert result['department'] == test_metadata.department
        assert result['uploaded_by'] == test_metadata.uploaded_by
        assert result['employee_role'] == test_metadata.employee_role
        assert result['document_type'] == test_metadata.document_type
        assert result['content_category'] == test_metadata.content_category
        assert result['priority_level'] == test_metadata.priority_level
        assert result['access_level'] == test_metadata.access_level
        assert result['tags'] == test_metadata.tags
        assert result['file_metadata'] == test_metadata.to_dict()
        
        # Verify file exists in storage
        file_info = await upload_service.get_file_info(result['file_id'], db_session)
        assert file_info is not None
        assert file_info['metadata']['uploaded_by'] == test_metadata.uploaded_by
        
        # Clean up
        success = await upload_service.delete_file(result['file_id'], db_session)
        assert success is True
    
    @pytest.mark.asyncio
    async def test_healthcare_metadata_workflow(self, upload_service, db_session, test_content):
        """Test healthcare-specific metadata workflow"""
        from src.models.metadata import HealthcareMetadata
        
        healthcare_metadata = HealthcareMetadata(
            specialty="cardiology",
            patient_id="P12345",
            physician_id="DOC001",
            hospital_unit="ICU"
        )
        
        file_metadata = FileMetadata(
            department="cardiology",
            uploaded_by="Dr. Smith",
            employee_role=EmployeeRole.DOCTOR,
            document_type=DocumentType.PATIENT_RECORD,
            content_category=ContentCategory.CLINICAL,
            priority_level=PriorityLevel.HIGH,
            access_level=AccessLevel.RESTRICTED,
            domain_type="healthcare",
            healthcare_metadata=healthcare_metadata,
            tags=["cardiac", "emergency"]
        )
        
        class MockUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self._content = content
            
            async def read(self):
                return self._content
            
            async def seek(self, position):
                pass
        
        mock_file = MockUploadFile("patient_record.txt", test_content)
        
        # Test upload
        result = await upload_service.upload_file(
            file=mock_file,
            db=db_session,
            file_metadata=file_metadata
        )
        
        assert result['success'] is True
        assert result['file_metadata']['domain_type'] == "healthcare"
        assert result['file_metadata']['healthcare_metadata']['specialty'] == "cardiology"
        assert result['file_metadata']['healthcare_metadata']['patient_id'] == "P12345"
        
        # Clean up
        await upload_service.delete_file(result['file_id'], db_session)
    
    @pytest.mark.asyncio
    async def test_university_metadata_workflow(self, upload_service, db_session, test_content):
        """Test university-specific metadata workflow"""
        from src.models.metadata import UniversityMetadata
        
        university_metadata = UniversityMetadata(
            course_code="CS101",
            semester="Fall 2024",
            academic_year="2024-2025",
            faculty_id="PROF001"
        )
        
        file_metadata = FileMetadata(
            department="computer_science",
            uploaded_by="Prof. Johnson",
            employee_role=EmployeeRole.FACULTY,
            document_type=DocumentType.LECTURE,
            content_category=ContentCategory.ACADEMIC,
            priority_level=PriorityLevel.MEDIUM,
            access_level=AccessLevel.INTERNAL,
            domain_type="university",
            university_metadata=university_metadata,
            tags=["programming", "lecture"]
        )
        
        class MockUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self._content = content
            
            async def read(self):
                return self._content
            
            async def seek(self, position):
                pass
        
        mock_file = MockUploadFile("lecture_notes.txt", test_content)
        
        # Test upload
        result = await upload_service.upload_file(
            file=mock_file,
            db=db_session,
            file_metadata=file_metadata
        )
        
        assert result['success'] is True
        assert result['file_metadata']['domain_type'] == "university"
        assert result['file_metadata']['university_metadata']['course_code'] == "CS101"
        assert result['file_metadata']['university_metadata']['semester'] == "Fall 2024"
        
        # Clean up
        await upload_service.delete_file(result['file_id'], db_session)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 