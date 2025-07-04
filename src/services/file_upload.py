import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

import logging
from src.config.settings import settings
from src.database.crud import file_crud
from src.utils.logging import setup_logging
# from src.services.file_processor import content_router  # Removed: main.py handles all processing
from src.models.metadata import FileMetadata, ProcessingMetadata

setup_logging()
logger = logging.getLogger(__name__)

# Try to import magic, use fallback if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not available, using fallback file type detection")


class FileValidator:
    """Handles file validation including type, size, and content checks"""
    
    def __init__(self):
        self.allowed_extensions = settings.allowed_file_types_list
        self.max_size = settings.max_file_size
    
    def validate_file_extension(self, filename: str) -> bool:
        """Validate file extension"""
        extension = Path(filename).suffix.lower().lstrip('.')
        return extension in self.allowed_extensions
    
    def validate_file_size(self, file_size: int) -> bool:
        """Validate file size"""
        return file_size <= self.max_size
    
    def detect_file_type(self, file_content: bytes, filename: str = None) -> Dict[str, str]:
        """Detect file type using python-magic or fallback methods"""
        try:
            if MAGIC_AVAILABLE:
                mime_type = magic.from_buffer(file_content, mime=True)
                file_type = magic.from_buffer(file_content)
                extension = self._mime_to_extension(mime_type)
                
                return {
                    "mime_type": mime_type,
                    "file_type": file_type,
                    "extension": extension
                }
            else:
                # Fallback: use file extension and content analysis
                return self._fallback_file_type_detection(file_content, filename)
                
        except Exception as e:
            logger.error(f"Error detecting file type: {e}")
            return self._fallback_file_type_detection(file_content, filename)
    
    def _fallback_file_type_detection(self, file_content: bytes, filename: str = None) -> Dict[str, str]:
        """Fallback file type detection based on content and extension"""
        extension = "bin"
        mime_type = "application/octet-stream"
        file_type = "binary"
        
        # Extract extension from filename if available
        if filename:
            ext = Path(filename).suffix.lower().lstrip('.')
            if ext:
                extension = ext
                mime_type = self._extension_to_mime(ext)
                file_type = f"{ext} file"
        
        # Simple content-based detection
        if file_content.startswith(b'%PDF'):
            mime_type = "application/pdf"
            extension = "pdf"
            file_type = "PDF document"
        elif file_content.startswith(b'\xff\xd8\xff'):
            mime_type = "image/jpeg"
            extension = "jpg"
            file_type = "JPEG image"
        elif file_content.startswith(b'\x89PNG'):
            mime_type = "image/png"
            extension = "png"
            file_type = "PNG image"
        elif file_content.startswith(b'GIF8'):
            mime_type = "image/gif"
            extension = "gif"
            file_type = "GIF image"
        elif all(byte < 128 for byte in file_content[:1000]):  # Likely text
            # Check if it's markdown content
            try:
                content_str = file_content.decode('utf-8', errors='ignore')
                if self._is_markdown_content(content_str):
                    mime_type = "text/markdown"
                    extension = "md"
                    file_type = "Markdown document"
                else:
                    mime_type = "text/plain"
                    extension = "txt"
                    file_type = "text file"
            except:
                mime_type = "text/plain"
                extension = "txt"
                file_type = "text file"
        
        return {
            "mime_type": mime_type,
            "file_type": file_type,
            "extension": extension
        }
    
    def _extension_to_mime(self, extension: str) -> str:
        """Convert file extension to MIME type"""
        ext_mime_map = {
            "txt": "text/plain",
            "md": "text/markdown",
            "markdown": "text/markdown",
            "html": "text/html",
            "htm": "text/html",
            "tex": "text/x-tex",
            "latex": "text/x-tex",
            "py": "text/x-python",
            "js": "text/javascript",
            "css": "text/css",
            "json": "application/json",
            "xml": "application/xml",
            "yaml": "text/yaml",
            "yml": "text/yaml",
            "pdf": "application/pdf",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "mp4": "video/mp4",
            "avi": "video/x-msvideo",
            "mov": "video/quicktime"
        }
        return ext_mime_map.get(extension.lower(), "application/octet-stream")
    
    def _mime_to_extension(self, mime_type: str) -> str:
        """Convert MIME type to file extension"""
        mime_extensions = {
            "text/plain": "txt",
            "text/markdown": "md",
            "text/html": "html",
            "text/x-tex": "tex",
            "text/x-python": "py",
            "text/javascript": "js",
            "text/css": "css",
            "text/yaml": "yaml",
            "application/json": "json",
            "application/xml": "xml",
            "application/pdf": "pdf",
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
            "audio/mpeg": "mp3",
            "audio/wav": "wav",
            "video/mp4": "mp4",
            "video/x-msvideo": "avi",
            "video/quicktime": "mov"
        }
        return mime_extensions.get(mime_type, "bin")
    
    def _is_markdown_content(self, content: str) -> bool:
        """Check if content has markdown characteristics"""
        # Common markdown patterns
        markdown_patterns = [
            r'^#{1,6}\s+.+$',  # Headers
            r'^\*\*.*\*\*$',   # Bold text
            r'^\*.*\*$',       # Italic text
            r'^[-*+]\s+.+$',   # Lists
            r'^\d+\.\s+.+$',   # Numbered lists
            r'^\[.*\]\(.*\)$', # Links
            r'^```.*```$',     # Code blocks
            r'^`.*`$',         # Inline code
            r'^\|.*\|$',       # Tables
            r'^>\s+.+$',       # Blockquotes
        ]
        
        lines = content.split('\n')[:50]  # Check first 50 lines
        markdown_indicators = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check each pattern
            import re
            for pattern in markdown_patterns:
                if re.match(pattern, line, re.MULTILINE):
                    markdown_indicators += 1
                    break
        
        # If more than 10% of lines have markdown indicators, consider it markdown
        return markdown_indicators > len([l for l in lines if l.strip()]) * 0.1
    
    def validate_file(self, filename: str, file_size: int, file_content: bytes) -> Dict[str, Any]:
        """Comprehensive file validation"""
        errors = []
        
        # Check file extension
        if not self.validate_file_extension(filename):
            errors.append(f"File extension not allowed. Allowed: {', '.join(self.allowed_extensions)}")
        
        # Check file size
        if not self.validate_file_size(file_size):
            errors.append(f"File size {file_size} exceeds maximum {self.max_size} bytes")
        
        # Detect file type
        type_info = self.detect_file_type(file_content, filename)
        
        # Validate detected type matches extension
        expected_ext = Path(filename).suffix.lower().lstrip('.')
        if expected_ext != type_info["extension"]:
            logger.warning(f"File extension mismatch: expected {expected_ext}, detected {type_info['extension']}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "type_info": type_info
        }


class FileStorage:
    """Handles file storage with organized directory structure"""
    
    def __init__(self):
        self.storage_path = Path(settings.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def generate_file_id(self) -> str:
        """Generate unique file identifier"""
        return str(uuid.uuid4())
    
    def generate_file_path(self, file_id: str, original_filename: str) -> Path:
        """Generate organized file path based on date and file type"""
        now = datetime.now()
        
        # Create directory structure: storage/YYYY/MM/DD/
        date_path = self.storage_path / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
        date_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with file_id to avoid conflicts
        extension = Path(original_filename).suffix
        filename = f"{file_id}{extension}"
        
        return date_path / filename
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    async def save_file(self, file_id: str, original_filename: str, file_content: bytes) -> Dict[str, Any]:
        """Save file to storage and return file information"""
        try:
            file_path = self.generate_file_path(file_id, original_filename)
            file_hash = self.calculate_file_hash(file_content)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"File saved: {file_path}")
            
            return {
                "file_path": str(file_path),
                "file_size": len(file_content),
                "file_hash": file_hash,
                "storage_success": True
            }
        except Exception as e:
            logger.error(f"Error saving file {file_id}: {e}")
            return {
                "file_path": None,
                "file_size": len(file_content),
                "file_hash": None,
                "storage_success": False,
                "error": str(e)
            }
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False


class FileUploadService:
    """Main file upload service that coordinates validation, storage, and database operations"""
    
    def __init__(self):
        self.validator = FileValidator()
        self.storage = FileStorage()
    
    async def upload_file(
        self, 
        file: UploadFile, 
        db: Session,
        file_metadata: FileMetadata
    ) -> Dict[str, Any]:
        """
        Upload and process a file
        
        Args:
            file: FastAPI UploadFile object
            db: Database session
            file_metadata: Complete file metadata structure
            
        Returns:
            Dictionary with upload results
        """
        try:
            # Generate unique file ID
            file_id = self.storage.generate_file_id()
            
            # Read file content
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Validate file
            validation_result = self.validator.validate_file(
                file.filename, 
                len(file_content), 
                file_content
            )
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "file_id": file_id,
                    "errors": validation_result["errors"]
                }
            
            # Save file to storage
            storage_result = await self.storage.save_file(
                file_id, 
                file.filename, 
                file_content
            )
            
            if not storage_result["storage_success"]:
                return {
                    "success": False,
                    "file_id": file_id,
                    "errors": [f"Storage error: {storage_result.get('error', 'Unknown error')}"]
                }
            
            # Prepare database record
            file_data = {
                "file_id": file_id,
                "filename": f"{file_id}{Path(file.filename).suffix}",
                "original_filename": file.filename,
                "file_path": storage_result["file_path"],
                "file_size": storage_result["file_size"],
                "file_type": validation_result["type_info"]["extension"],
                "mime_type": validation_result["type_info"]["mime_type"],
                "status": "uploaded",
                "department": file_metadata.department,
                "project": file_metadata.project_name,
                "tags": ",".join(file_metadata.tags) if file_metadata.tags else None,
                "file_metadata": file_metadata.to_dict()
            }
            
            # Save to database
            db_file = file_crud.create_file(db, file_data)
            
            # Note: File processing is now handled entirely by main.py /process endpoint
            # This ensures correct order: extraction first, then analysis
            processing_info = {
                "processing_completed": True,
                "processing_note": "File ready for processing by main.py endpoint"
            }
            
            logger.info(f"File upload successful: {file_id}")
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": file.filename,
                "original_filename": file.filename,
                "storage_path": storage_result["file_path"],
                "file_size": storage_result["file_size"],
                "file_type": validation_result["type_info"]["extension"],
                "mime_type": validation_result["type_info"]["mime_type"],
                "file_hash": storage_result["file_hash"],
                "database_id": db_file.id,
                "department": file_metadata.department,
                "project": file_metadata.project_name,
                "tags": file_metadata.tags,
                "employee_role": file_metadata.employee_role,
                "uploaded_by": file_metadata.uploaded_by,
                "document_type": file_metadata.document_type,
                "content_category": file_metadata.content_category,
                "priority_level": file_metadata.priority_level,
                "access_level": file_metadata.access_level,
                "file_metadata": file_metadata.to_dict(),
                "message": "File uploaded successfully",
                **processing_info
            }
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {
                "success": False,
                "file_id": file_id if 'file_id' in locals() else None,
                "errors": [f"Upload error: {str(e)}"]
            }
    
    async def get_file_info(self, file_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get file information by file ID"""
        try:
            db_file = file_crud.get_file_by_id(db, file_id)
            if not db_file:
                return None
            
            return {
                "file_id": db_file.file_id,
                "filename": db_file.filename,
                "original_filename": db_file.original_filename,
                "file_size": db_file.file_size,
                "file_type": db_file.file_type,
                "mime_type": db_file.mime_type,
                "status": db_file.status,
                "department": db_file.department,
                "project": db_file.project,
                "tags": db_file.tags.split(",") if db_file.tags else [],
                "metadata": db_file.file_metadata,
                "created_at": db_file.created_at.isoformat(),
                "updated_at": db_file.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting file info {file_id}: {e}")
            return None
    
    async def delete_file(self, file_id: str, db: Session) -> bool:
        """Delete file from storage and database"""
        try:
            # Get file info
            db_file = file_crud.get_file_by_id(db, file_id)
            if not db_file:
                return False
            
            # Delete from storage
            storage_deleted = await self.storage.delete_file(db_file.file_path)
            
            # Delete from database
            db_deleted = file_crud.delete_file(db, file_id)
            
            return storage_deleted and db_deleted
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False


# Global service instance
file_upload_service = FileUploadService() 