import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from sqlalchemy.orm import Session

from src.utils.logging import logger
from src.database.crud import file_crud


class ContentType(Enum):
    TEXT = "text"
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    UNKNOWN = "unknown"


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
    priority: int = 1
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


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


class ProcessingWorkflow:
    def __init__(self):
        self.workflows = {
            ContentType.TEXT: self._text_workflow,
            ContentType.DOCUMENT: self._document_workflow,
            ContentType.IMAGE: self._image_workflow,
            ContentType.AUDIO: self._audio_workflow,
            ContentType.VIDEO: self._video_workflow,
            ContentType.UNKNOWN: self._unknown_workflow
        }
    
    def get_workflow(self, content_type: ContentType) -> Callable:
        return self.workflows.get(content_type, self._unknown_workflow)
    
    def _text_workflow(self, job: ProcessingJob) -> Dict[str, Any]:
        return {
            "steps": ["extract_text_content", "generate_text_preview", "analyze_text_structure", "extract_keywords", "generate_embeddings"],
            "priority": 1,
            "estimated_time": 30,
            "requires_external_api": True
        }
    
    def _document_workflow(self, job: ProcessingJob) -> Dict[str, Any]:
        return {
            "steps": ["extract_document_metadata", "convert_to_text", "generate_document_preview", "extract_structure", "generate_embeddings"],
            "priority": 2,
            "estimated_time": 120,
            "requires_external_api": True
        }
    
    def _image_workflow(self, job: ProcessingJob) -> Dict[str, Any]:
        return {
            "steps": ["extract_image_metadata", "generate_thumbnail", "analyze_image_content", "extract_text_from_image", "generate_image_embeddings"],
            "priority": 3,
            "estimated_time": 60,
            "requires_external_api": True
        }
    
    def _audio_workflow(self, job: ProcessingJob) -> Dict[str, Any]:
        return {
            "steps": ["extract_audio_metadata", "transcribe_audio", "analyze_audio_content", "generate_audio_preview", "generate_embeddings"],
            "priority": 4,
            "estimated_time": 180,
            "requires_external_api": True
        }
    
    def _video_workflow(self, job: ProcessingJob) -> Dict[str, Any]:
        return {
            "steps": ["extract_video_metadata", "extract_video_frames", "transcribe_audio_track", "analyze_video_content", "generate_video_preview", "generate_embeddings"],
            "priority": 5,
            "estimated_time": 300,
            "requires_external_api": True
        }
    
    def _unknown_workflow(self, job: ProcessingJob) -> Dict[str, Any]:
        return {
            "steps": ["extract_basic_metadata", "attempt_content_detection", "generate_file_summary"],
            "priority": 10,
            "estimated_time": 15,
            "requires_external_api": False
        }


class ProcessingQueue:
    def __init__(self, max_concurrent_jobs: int = 3):
        self.max_concurrent_jobs = max_concurrent_jobs
        self.pending_jobs: List[ProcessingJob] = []
        self.active_jobs: List[ProcessingJob] = []
        self.completed_jobs: List[ProcessingJob] = []
        self.failed_jobs: List[ProcessingJob] = []
        self._lock = asyncio.Lock()
    
    async def add_job(self, job: ProcessingJob):
        async with self._lock:
            self.pending_jobs.append(job)
            self.pending_jobs.sort(key=lambda x: x.priority)
            logger.info(f"Added job {job.file_id} to processing queue")
    
    async def get_next_job(self) -> Optional[ProcessingJob]:
        async with self._lock:
            if len(self.active_jobs) >= self.max_concurrent_jobs:
                return None
            
            if not self.pending_jobs:
                return None
            
            job = self.pending_jobs.pop(0)
            job.status = ProcessingStatus.IN_PROGRESS
            job.started_at = datetime.now()
            self.active_jobs.append(job)
            
            logger.info(f"Started processing job {job.file_id}")
            return job
    
    async def complete_job(self, job: ProcessingJob, success: bool = True, error_message: str = None):
        async with self._lock:
            if job in self.active_jobs:
                self.active_jobs.remove(job)
            
            job.completed_at = datetime.now()
            
            if success:
                job.status = ProcessingStatus.COMPLETED
                self.completed_jobs.append(job)
                logger.info(f"Completed job {job.file_id}")
            else:
                job.status = ProcessingStatus.FAILED
                job.error_message = error_message
                self.failed_jobs.append(job)
                logger.error(f"Failed job {job.file_id}: {error_message}")
    
    async def get_queue_status(self) -> Dict[str, Any]:
        async with self._lock:
            return {
                "pending_jobs": len(self.pending_jobs),
                "active_jobs": len(self.active_jobs),
                "completed_jobs": len(self.completed_jobs),
                "failed_jobs": len(self.failed_jobs),
                "max_concurrent": self.max_concurrent_jobs
            }


class ContentTypeRouter:
    def __init__(self):
        self.classifier = ContentTypeClassifier()
        self.workflow_manager = ProcessingWorkflow()
        self.processing_queue = ProcessingQueue()
    
    async def route_file_for_processing(
        self, 
        file_id: str, 
        file_path: str, 
        filename: str, 
        mime_type: str,
        db: Session
    ) -> ProcessingJob:
        try:
            content_type = self.classifier.classify_file(filename, mime_type)
            
            workflow_func = self.workflow_manager.get_workflow(content_type)
            
            job = ProcessingJob(
                file_id=file_id,
                file_path=file_path,
                content_type=content_type
            )
            
            workflow_config = workflow_func(job)
            job.metadata.update(workflow_config)
            job.priority = workflow_config.get("priority", 5)
            
            await self.processing_queue.add_job(job)
            
            file_crud.update_file_status(db, file_id, "processing")
            
            logger.info(f"Routed file {file_id} ({content_type.value}) for processing")
            return job
            
        except Exception as e:
            logger.error(f"Error routing file {file_id} for processing: {e}")
            raise
    
    async def process_next_job(self, db: Session) -> Optional[ProcessingJob]:
        job = await self.processing_queue.get_next_job()
        if not job:
            return None
        
        try:
            logger.info(f"Processing job {job.file_id} with workflow steps: {job.metadata.get('steps', [])}")
            
            await asyncio.sleep(1)
            
            await self.processing_queue.complete_job(job, success=True)
            file_crud.update_file_status(db, job.file_id, "processed")
            
            return job
            
        except Exception as e:
            await self.processing_queue.complete_job(job, success=False, error_message=str(e))
            file_crud.update_file_status(db, job.file_id, "failed")
            raise
    
    async def get_processing_status(self) -> Dict[str, Any]:
        return await self.processing_queue.get_queue_status()


content_router = ContentTypeRouter() 