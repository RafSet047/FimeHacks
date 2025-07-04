import sys
from pathlib import Path
# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from sqlalchemy.orm import Session

import logging
from src.utils.logging import setup_logging
from src.database.crud import file_crud
from src.models.metadata import FileMetadata, ProcessingMetadata
from src.services.content_types import ContentType
from src.services.workflow_manager import workflow_manager
from src.services.workflows import TextWorkflow

setup_logging()
logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ProcessingJob:
    file_id: str
    file_path: str
    content_type: ContentType
    file_metadata: FileMetadata
    priority: int = 1
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    processing_metadata: ProcessingMetadata = None
    workflow_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.processing_metadata is None:
            self.processing_metadata = ProcessingMetadata()
        if self.workflow_metadata is None:
            self.workflow_metadata = {}


class ContentTypeClassifier:
    def __init__(self):
        self.mime_type_mapping = {
            "text/plain": ContentType.TEXT,
            "text/csv": ContentType.TEXT,
            "text/markdown": ContentType.TEXT,
            "text/html": ContentType.TEXT,
            "application/json": ContentType.TEXT,
            "application/pdf": ContentType.DOCUMENT,
            "application/msword": ContentType.DOCUMENT,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ContentType.DOCUMENT,
            "image/jpeg": ContentType.IMAGE,
            "image/png": ContentType.IMAGE,
            "image/gif": ContentType.IMAGE,
            "audio/mpeg": ContentType.AUDIO,
            "audio/wav": ContentType.AUDIO,
            "video/mp4": ContentType.VIDEO,
            "video/avi": ContentType.VIDEO,
        }
        
        self.extension_mapping = {
            ".txt": ContentType.TEXT,
            ".csv": ContentType.TEXT,
            ".md": ContentType.TEXT,
            ".html": ContentType.TEXT,
            ".json": ContentType.TEXT,
            ".pdf": ContentType.DOCUMENT,
            ".doc": ContentType.DOCUMENT,
            ".docx": ContentType.DOCUMENT,
            ".jpg": ContentType.IMAGE,
            ".jpeg": ContentType.IMAGE,
            ".png": ContentType.IMAGE,
            ".gif": ContentType.IMAGE,
            ".mp3": ContentType.AUDIO,
            ".wav": ContentType.AUDIO,
            ".mp4": ContentType.VIDEO,
            ".avi": ContentType.VIDEO,
        }
    
    def classify_file(self, filename: str, mime_type: str) -> ContentType:
        mime_classification = self.mime_type_mapping.get(mime_type.lower(), ContentType.UNKNOWN)
        if mime_classification != ContentType.UNKNOWN:
            return mime_classification
        
        extension = Path(filename).suffix.lower()
        extension_classification = self.extension_mapping.get(extension, ContentType.UNKNOWN)
        if extension_classification != ContentType.UNKNOWN:
            return extension_classification
        
        logger.warning(f"Could not classify file: {filename} with MIME type: {mime_type}")
        return ContentType.UNKNOWN


class ContentTypeRouter:
    def __init__(self):
        self.classifier = ContentTypeClassifier()
        self._setup_workflows()
    
    def _setup_workflows(self):
        # Register workflows
        workflow_manager.register_workflow(ContentType.TEXT, TextWorkflow)
        logger.info("Registered text workflow")
    
    async def route_file_for_processing(
        self, 
        file_id: str, 
        file_path: str, 
        filename: str, 
        mime_type: str,
        file_metadata: FileMetadata,
        db: Session
    ) -> ProcessingJob:
        try:
            content_type = self.classifier.classify_file(filename, mime_type)
            
            # Create processing job
            job = ProcessingJob(
                file_id=file_id,
                file_path=file_path,
                content_type=content_type,
                file_metadata=file_metadata
            )
            
            # Set priority based on file metadata
            if file_metadata.priority_level in ["urgent", "critical"]:
                job.priority = 1
            elif file_metadata.priority_level == "high":
                job.priority = 2
            else:
                job.priority = 3
            
            # Set workflow metadata (simplified)
            job.workflow_metadata = {
                "content_type": content_type.value,
                "domain": file_metadata.domain_type,
                "department": file_metadata.department,
                "estimated_time": 30  # simplified estimate
            }
            
            logger.info(f"Routed file {file_id} from {file_metadata.department} ({content_type.value}) for processing")
            return job
            
        except Exception as e:
            logger.error(f"Error routing file {file_id} for processing: {e}")
            raise
    
    async def process_job(self, job: ProcessingJob, db: Session) -> ProcessingJob:
        job.status = ProcessingStatus.IN_PROGRESS
        job.started_at = datetime.now()
        
        try:
            # Execute workflow
            workflow_output = workflow_manager.execute_workflow(
                content_type=job.content_type,
                file_id=job.file_id,
                file_path=job.file_path,
                filename=Path(job.file_path).name,
                mime_type="",  # We don't need mime type for simplified version
                file_metadata=job.file_metadata,
                db=db
            )
            
            # Update job with results
            job.completed_at = datetime.now()
            
            if workflow_output.success:
                job.status = ProcessingStatus.COMPLETED
                job.processing_metadata.content_extracted = True
                job.processing_metadata.processing_completed_at = job.completed_at
                job.processing_metadata.processing_duration_seconds = workflow_output.processing_time
                
                # Update file status in database
                file_crud.update_file_status(db, job.file_id, "processed")
                
                logger.info(f"Successfully processed file {job.file_id}")
            else:
                job.status = ProcessingStatus.FAILED
                job.error_message = workflow_output.error_message
                job.processing_metadata.error_occurred = True
                job.processing_metadata.error_message = workflow_output.error_message
                
                # Update file status in database
                file_crud.update_file_status(db, job.file_id, "failed")
                
                logger.error(f"Failed to process file {job.file_id}: {workflow_output.error_message}")
            
            return job
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            job.processing_metadata.error_occurred = True
            job.processing_metadata.error_message = str(e)
            
            file_crud.update_file_status(db, job.file_id, "failed")
            
            logger.error(f"Error processing job {job.file_id}: {str(e)}")
            return job


content_router = ContentTypeRouter() 