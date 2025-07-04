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
    
    def test_create_and_retrieve_file_record(self, db_session, storage, test_content):
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
            "department": "test_dept",
            "project": "test_project",
            "tags": "test,validation"
        }
        
        # Create file record
        db_file = file_crud.create_file(db_session, test_file_data)
        assert db_file.id is not None
        assert db_file.file_id == file_id
        
        # Test file retrieval
        retrieved_file = file_crud.get_file_by_id(db_session, file_id)
        assert retrieved_file is not None
        assert retrieved_file.filename == f"{file_id}.txt"
        
        # Clean up
        file_crud.delete_file(db_session, file_id)
    
    @pytest.mark.asyncio
    async def test_file_info_service(self, upload_service, db_session, storage, test_content):
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
            "status": "uploaded"
        }
        
        # Create file record
        file_crud.create_file(db_session, test_file_data)
        
        # Test file info service
        file_info = await upload_service.get_file_info(file_id, db_session)
        assert file_info is not None
        assert file_info['original_filename'] == "test.txt"
        assert file_info['file_id'] == file_id
        
        # Clean up
        file_crud.delete_file(db_session, file_id)


class TestCompleteUploadWorkflow:
    """Test complete upload workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_upload_workflow(self, upload_service, db_session, test_content):
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
            department="test_department",
            project="test_project",
            tags=["test", "upload", "validation"]
        )
        
        assert result['success'] is True
        assert 'file_id' in result
        assert result['filename'] == "test_upload.txt"
        assert result['file_type'] == "txt"
        
        # Verify file exists in storage
        file_info = await upload_service.get_file_info(result['file_id'], db_session)
        assert file_info is not None
        
        # Clean up
        success = await upload_service.delete_file(result['file_id'], db_session)
        assert success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 