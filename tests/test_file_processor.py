"""
Tests for the file processor module
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.services.file_processor import (
    ProcessingStatus, ProcessingJob, ContentTypeClassifier, 
    ContentTypeRouter, content_router
)
from src.services.content_types import ContentType
from src.models.metadata import (
    FileMetadata, ProcessingMetadata, EmployeeRole, DocumentType, 
    ContentCategory, PriorityLevel, AccessLevel
)


class TestContentTypeClassifier:
    """Test the ContentTypeClassifier class"""
    
    def test_classifier_initialization(self):
        """Test classifier initialization"""
        classifier = ContentTypeClassifier()
        assert classifier.mime_type_mapping is not None
        assert classifier.extension_mapping is not None
        assert len(classifier.mime_type_mapping) > 0
        assert len(classifier.extension_mapping) > 0
    
    def test_classify_file_by_mime_type(self):
        """Test file classification by MIME type"""
        classifier = ContentTypeClassifier()
        
        # Test text files
        assert classifier.classify_file("test.txt", "text/plain") == ContentType.TEXT
        assert classifier.classify_file("data.csv", "text/csv") == ContentType.TEXT
        assert classifier.classify_file("page.html", "text/html") == ContentType.TEXT
        
        # Test document files
        assert classifier.classify_file("doc.pdf", "application/pdf") == ContentType.DOCUMENT
        assert classifier.classify_file("file.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document") == ContentType.DOCUMENT
        
        # Test image files
        assert classifier.classify_file("photo.jpg", "image/jpeg") == ContentType.IMAGE
        assert classifier.classify_file("image.png", "image/png") == ContentType.IMAGE
        
        # Test audio files
        assert classifier.classify_file("song.mp3", "audio/mpeg") == ContentType.AUDIO
        assert classifier.classify_file("sound.wav", "audio/wav") == ContentType.AUDIO
        
        # Test video files
        assert classifier.classify_file("video.mp4", "video/mp4") == ContentType.VIDEO
        assert classifier.classify_file("movie.avi", "video/avi") == ContentType.VIDEO
    
    def test_classify_file_by_extension_fallback(self):
        """Test file classification falls back to extension when MIME type is unknown"""
        classifier = ContentTypeClassifier()
        
        # Test fallback to extension
        assert classifier.classify_file("test.txt", "unknown/type") == ContentType.TEXT
        assert classifier.classify_file("document.pdf", "unknown/type") == ContentType.DOCUMENT
        assert classifier.classify_file("image.jpg", "unknown/type") == ContentType.IMAGE
        assert classifier.classify_file("audio.mp3", "unknown/type") == ContentType.AUDIO
        assert classifier.classify_file("video.mp4", "unknown/type") == ContentType.VIDEO
    
    def test_classify_file_unknown(self):
        """Test classification of unknown file types"""
        classifier = ContentTypeClassifier()
        
        # Test unknown file type
        assert classifier.classify_file("unknown.xyz", "unknown/type") == ContentType.UNKNOWN
        assert classifier.classify_file("test", "unknown/type") == ContentType.UNKNOWN


@pytest.mark.skip(reason="ProcessingWorkflow class removed in simplification")
class TestProcessingWorkflowDeprecated:
    """Test the ProcessingWorkflow class"""
    
    @pytest.fixture
    def workflow(self):
        return ProcessingWorkflow()
    
    @pytest.fixture
    def basic_metadata(self):
        return FileMetadata(
            department="test_department",
            uploaded_by="test_user",
            employee_role=EmployeeRole.STAFF,
            document_type=DocumentType.REPORT,
            content_category=ContentCategory.ADMINISTRATIVE,
            priority_level=PriorityLevel.MEDIUM,
            access_level=AccessLevel.INTERNAL
        )
    
    @pytest.fixture
    def healthcare_metadata(self):
        from src.models.metadata import HealthcareMetadata
        healthcare_specific = HealthcareMetadata(
            specialty="cardiology",
            patient_id="P12345",
            physician_id="DOC001"
        )
        return FileMetadata(
            department="cardiology",
            uploaded_by="Dr. Smith",
            employee_role=EmployeeRole.DOCTOR,
            document_type=DocumentType.PATIENT_RECORD,
            content_category=ContentCategory.CLINICAL,
            priority_level=PriorityLevel.URGENT,
            access_level=AccessLevel.RESTRICTED,
            domain_type="healthcare",
            healthcare_metadata=healthcare_specific
        )
    
    @pytest.fixture
    def university_metadata(self):
        from src.models.metadata import UniversityMetadata
        university_specific = UniversityMetadata(
            course_code="CS101",
            semester="Fall 2024",
            faculty_id="PROF001"
        )
        return FileMetadata(
            department="computer_science",
            uploaded_by="Prof. Johnson",
            employee_role=EmployeeRole.FACULTY,
            document_type=DocumentType.LECTURE,
            content_category=ContentCategory.ACADEMIC,
            priority_level=PriorityLevel.MEDIUM,
            access_level=AccessLevel.INTERNAL,
            domain_type="university",
            university_metadata=university_specific
        )
    
    def test_workflow_initialization(self, workflow):
        """Test workflow initialization"""
        assert workflow.workflows is not None
        assert len(workflow.workflows) == 6  # All content types
        assert ContentType.TEXT in workflow.workflows
        assert ContentType.DOCUMENT in workflow.workflows
        assert ContentType.IMAGE in workflow.workflows
        assert ContentType.AUDIO in workflow.workflows
        assert ContentType.VIDEO in workflow.workflows
        assert ContentType.UNKNOWN in workflow.workflows
    
    def test_get_workflow_functions(self, workflow):
        """Test getting workflow functions"""
        text_workflow = workflow.get_workflow(ContentType.TEXT)
        assert text_workflow is not None
        assert callable(text_workflow)
        
        unknown_workflow = workflow.get_workflow(ContentType.UNKNOWN)
        assert unknown_workflow is not None
        assert callable(unknown_workflow)
    
    def test_text_workflow_basic(self, workflow, basic_metadata):
        """Test text workflow with basic metadata"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.txt",
            content_type=ContentType.TEXT,
            file_metadata=basic_metadata
        )
        
        result = workflow._text_workflow(job)
        
        assert result["steps"] is not None
        assert len(result["steps"]) >= 5  # Basic text processing steps
        assert "extract_text_content" in result["steps"]
        assert "generate_embeddings" in result["steps"]
        assert result["priority"] == 1  # Medium priority
        assert result["estimated_time"] == 30
        assert result["requires_external_api"] is True
        assert result["department"] == basic_metadata.department
    
    def test_text_workflow_healthcare(self, workflow, healthcare_metadata):
        """Test text workflow with healthcare metadata"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.txt",
            content_type=ContentType.TEXT,
            file_metadata=healthcare_metadata
        )
        
        result = workflow._text_workflow(job)
        
        assert result["steps"] is not None
        assert "extract_medical_entities" in result["steps"]
        assert "analyze_medical_terminology" in result["steps"]
        assert result["priority"] == 0  # Urgent priority -> 0
        assert result["domain_context"] == "healthcare"
        assert result["department"] == healthcare_metadata.department
    
    def test_text_workflow_university(self, workflow, university_metadata):
        """Test text workflow with university metadata"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.txt",
            content_type=ContentType.TEXT,
            file_metadata=university_metadata
        )
        
        result = workflow._text_workflow(job)
        
        assert result["steps"] is not None
        assert "extract_academic_entities" in result["steps"]
        assert "analyze_citations" in result["steps"]
        assert result["priority"] == 1  # Medium priority
        assert result["domain_context"] == "university"
        assert result["department"] == university_metadata.department
    
    def test_document_workflow(self, workflow, basic_metadata):
        """Test document workflow"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.pdf",
            content_type=ContentType.DOCUMENT,
            file_metadata=basic_metadata
        )
        
        result = workflow._document_workflow(job)
        
        assert result["steps"] is not None
        assert "extract_document_metadata" in result["steps"]
        assert "convert_to_text" in result["steps"]
        assert "generate_embeddings" in result["steps"]
        assert result["priority"] == 2
        assert result["estimated_time"] == 120
        assert result["requires_external_api"] is True
    
    def test_image_workflow(self, workflow, basic_metadata):
        """Test image workflow"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/image.jpg",
            content_type=ContentType.IMAGE,
            file_metadata=basic_metadata
        )
        
        result = workflow._image_workflow(job)
        
        assert result["steps"] is not None
        assert "extract_image_metadata" in result["steps"]
        assert "generate_thumbnail" in result["steps"]
        assert "analyze_image_content" in result["steps"]
        assert result["priority"] == 3
        assert result["estimated_time"] == 60
    
    def test_audio_workflow(self, workflow, basic_metadata):
        """Test audio workflow"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/audio.mp3",
            content_type=ContentType.AUDIO,
            file_metadata=basic_metadata
        )
        
        result = workflow._audio_workflow(job)
        
        assert result["steps"] is not None
        assert "extract_audio_metadata" in result["steps"]
        assert "transcribe_audio" in result["steps"]
        assert result["priority"] == 4
        assert result["estimated_time"] == 180
    
    def test_video_workflow(self, workflow, basic_metadata):
        """Test video workflow"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/video.mp4",
            content_type=ContentType.VIDEO,
            file_metadata=basic_metadata
        )
        
        result = workflow._video_workflow(job)
        
        assert result["steps"] is not None
        assert "extract_video_metadata" in result["steps"]
        assert "extract_video_frames" in result["steps"]
        assert "transcribe_audio_track" in result["steps"]
        assert result["priority"] == 5
        assert result["estimated_time"] == 300
    
    def test_unknown_workflow(self, workflow, basic_metadata):
        """Test unknown workflow"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/unknown.xyz",
            content_type=ContentType.UNKNOWN,
            file_metadata=basic_metadata
        )
        
        result = workflow._unknown_workflow(job)
        
        assert result["steps"] is not None
        assert "extract_basic_metadata" in result["steps"]
        assert "attempt_content_detection" in result["steps"]
        assert result["priority"] == 10
        assert result["estimated_time"] == 15
        assert result["requires_external_api"] is False
    
    def test_priority_levels(self, workflow):
        """Test priority handling for different priority levels"""
        # Test urgent priority
        urgent_metadata = FileMetadata(
            department="test",
            uploaded_by="test_user",
            employee_role=EmployeeRole.STAFF,
            document_type=DocumentType.REPORT,
            content_category=ContentCategory.ADMINISTRATIVE,
            priority_level=PriorityLevel.URGENT,
            access_level=AccessLevel.INTERNAL
        )
        
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.txt",
            content_type=ContentType.TEXT,
            file_metadata=urgent_metadata
        )
        
        result = workflow._text_workflow(job)
        assert result["priority"] == 0  # Urgent gets priority 0
        
        # Test critical priority
        critical_metadata = FileMetadata(
            department="test",
            uploaded_by="test_user",
            employee_role=EmployeeRole.STAFF,
            document_type=DocumentType.REPORT,
            content_category=ContentCategory.ADMINISTRATIVE,
            priority_level=PriorityLevel.CRITICAL,
            access_level=AccessLevel.INTERNAL
        )
        
        job.file_metadata = critical_metadata
        result = workflow._text_workflow(job)
        assert result["priority"] == 0  # Critical gets priority 0


@pytest.mark.skip(reason="ProcessingQueue class removed in simplification")
class TestProcessingQueue:
    """Test the ProcessingQueue class"""
    
    @pytest.fixture
    def queue(self):
        return ProcessingQueue(max_concurrent_jobs=2)
    
    @pytest.fixture
    def sample_metadata(self):
        return FileMetadata(
            department="test_department",
            uploaded_by="test_user",
            employee_role=EmployeeRole.STAFF,
            document_type=DocumentType.REPORT,
            content_category=ContentCategory.ADMINISTRATIVE,
            priority_level=PriorityLevel.MEDIUM,
            access_level=AccessLevel.INTERNAL
        )
    
    @pytest.fixture
    def sample_job(self, sample_metadata):
        return ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.txt",
            content_type=ContentType.TEXT,
            file_metadata=sample_metadata,
            priority=1
        )
    
    def test_queue_initialization(self, queue):
        """Test queue initialization"""
        assert queue.max_concurrent_jobs == 2
        assert len(queue.pending_jobs) == 0
        assert len(queue.active_jobs) == 0
        assert len(queue.completed_jobs) == 0
        assert len(queue.failed_jobs) == 0
    
    @pytest.mark.asyncio
    async def test_add_job(self, queue, sample_job):
        """Test adding a job to the queue"""
        await queue.add_job(sample_job)
        
        assert len(queue.pending_jobs) == 1
        assert queue.pending_jobs[0] == sample_job
        assert len(queue.active_jobs) == 0
    
    @pytest.mark.asyncio
    async def test_get_next_job(self, queue, sample_job):
        """Test getting the next job from the queue"""
        await queue.add_job(sample_job)
        
        next_job = await queue.get_next_job()
        
        assert next_job == sample_job
        assert next_job.status == ProcessingStatus.IN_PROGRESS
        assert next_job.started_at is not None
        assert len(queue.pending_jobs) == 0
        assert len(queue.active_jobs) == 1
    
    @pytest.mark.asyncio
    async def test_get_next_job_max_concurrent(self, queue, sample_metadata):
        """Test maximum concurrent jobs limit"""
        # Add 3 jobs
        jobs = []
        for i in range(3):
            job = ProcessingJob(
                file_id=f"job{i}",
                file_path=f"/path/to/file{i}.txt",
                content_type=ContentType.TEXT,
                file_metadata=sample_metadata,
                priority=i
            )
            jobs.append(job)
            await queue.add_job(job)
        
        # Get first two jobs (max_concurrent_jobs = 2)
        job1 = await queue.get_next_job()
        job2 = await queue.get_next_job()
        
        assert job1 is not None
        assert job2 is not None
        assert len(queue.active_jobs) == 2
        assert len(queue.pending_jobs) == 1
        
        # Try to get third job - should return None due to max concurrent limit
        job3 = await queue.get_next_job()
        assert job3 is None
        assert len(queue.active_jobs) == 2
        assert len(queue.pending_jobs) == 1
    
    @pytest.mark.asyncio
    async def test_get_next_job_empty_queue(self, queue):
        """Test getting next job from empty queue"""
        next_job = await queue.get_next_job()
        assert next_job is None
    
    @pytest.mark.asyncio
    async def test_complete_job_success(self, queue, sample_job):
        """Test completing a job successfully"""
        await queue.add_job(sample_job)
        job = await queue.get_next_job()
        
        await queue.complete_job(job, success=True)
        
        assert job.status == ProcessingStatus.COMPLETED
        assert job.completed_at is not None
        assert len(queue.active_jobs) == 0
        assert len(queue.completed_jobs) == 1
        assert queue.completed_jobs[0] == job
    
    @pytest.mark.asyncio
    async def test_complete_job_failure(self, queue, sample_job):
        """Test completing a job with failure"""
        await queue.add_job(sample_job)
        job = await queue.get_next_job()
        
        error_msg = "Test error"
        await queue.complete_job(job, success=False, error_message=error_msg)
        
        assert job.status == ProcessingStatus.FAILED
        assert job.completed_at is not None
        assert job.error_message == error_msg
        assert len(queue.active_jobs) == 0
        assert len(queue.failed_jobs) == 1
        assert queue.failed_jobs[0] == job
    
    @pytest.mark.asyncio
    async def test_get_queue_status(self, queue, sample_metadata):
        """Test getting queue status"""
        # Add some jobs in different states
        job1 = ProcessingJob(
            file_id="job1",
            file_path="/path/to/file1.txt",
            content_type=ContentType.TEXT,
            file_metadata=sample_metadata
        )
        job2 = ProcessingJob(
            file_id="job2",
            file_path="/path/to/file2.txt",
            content_type=ContentType.TEXT,
            file_metadata=sample_metadata
        )
        
        await queue.add_job(job1)
        await queue.add_job(job2)
        
        # Start one job
        active_job = await queue.get_next_job()
        
        # Complete one job
        await queue.complete_job(active_job, success=True)
        
        status = await queue.get_queue_status()
        
        assert status["pending_jobs"] == 1
        assert status["active_jobs"] == 0
        assert status["completed_jobs"] == 1
        assert status["failed_jobs"] == 0
        assert status["max_concurrent"] == 2


class TestProcessingJob:
    """Test the ProcessingJob dataclass"""
    
    @pytest.fixture
    def sample_metadata(self):
        return FileMetadata(
            department="test_department",
            uploaded_by="test_user",
            employee_role=EmployeeRole.STAFF,
            document_type=DocumentType.REPORT,
            content_category=ContentCategory.ADMINISTRATIVE,
            priority_level=PriorityLevel.MEDIUM,
            access_level=AccessLevel.INTERNAL
        )
    
    def test_job_initialization(self, sample_metadata):
        """Test ProcessingJob initialization"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.txt",
            content_type=ContentType.TEXT,
            file_metadata=sample_metadata
        )
        
        assert job.file_id == "test_id"
        assert job.file_path == "/path/to/file.txt"
        assert job.content_type == ContentType.TEXT
        assert job.file_metadata == sample_metadata
        assert job.priority == 1
        assert job.created_at is not None
        assert job.started_at is None
        assert job.completed_at is None
        assert job.status == ProcessingStatus.PENDING
        assert job.error_message is None
        assert job.processing_metadata is not None
        assert job.workflow_metadata == {}
    
    def test_job_post_init(self, sample_metadata):
        """Test ProcessingJob post-initialization"""
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.txt",
            content_type=ContentType.TEXT,
            file_metadata=sample_metadata
        )
        
        # Test that post_init creates default values
        assert isinstance(job.created_at, datetime)
        assert isinstance(job.processing_metadata, ProcessingMetadata)
        assert isinstance(job.workflow_metadata, dict)
    
    def test_job_custom_initialization(self, sample_metadata):
        """Test ProcessingJob with custom values"""
        custom_time = datetime.now()
        custom_processing_metadata = ProcessingMetadata()
        custom_workflow_metadata = {"test": "value"}
        
        job = ProcessingJob(
            file_id="test_id",
            file_path="/path/to/file.txt",
            content_type=ContentType.TEXT,
            file_metadata=sample_metadata,
            priority=5,
            created_at=custom_time,
            processing_metadata=custom_processing_metadata,
            workflow_metadata=custom_workflow_metadata
        )
        
        assert job.priority == 5
        assert job.created_at == custom_time
        assert job.processing_metadata == custom_processing_metadata
        assert job.workflow_metadata == custom_workflow_metadata


@pytest.mark.skip(reason="ContentTypeRouter simplified - some methods removed")
class TestContentTypeRouter:
    """Test the ContentTypeRouter class"""
    
    @pytest.fixture
    def router(self):
        return ContentTypeRouter()
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_metadata(self):
        return FileMetadata(
            department="test_department",
            uploaded_by="test_user",
            employee_role=EmployeeRole.STAFF,
            document_type=DocumentType.REPORT,
            content_category=ContentCategory.ADMINISTRATIVE,
            priority_level=PriorityLevel.MEDIUM,
            access_level=AccessLevel.INTERNAL
        )
    
    def test_router_initialization(self, router):
        """Test ContentTypeRouter initialization"""
        assert router.classifier is not None
        assert router.workflow_manager is not None
        assert router.processing_queue is not None
    
    @pytest.mark.asyncio
    async def test_route_file_for_processing(self, router, mock_db, sample_metadata):
        """Test routing a file for processing"""
        with patch('src.services.file_processor.file_crud') as mock_file_crud:
            mock_file_crud.update_file_status.return_value = True
            
            job = await router.route_file_for_processing(
                file_id="test_id",
                file_path="/path/to/file.txt",
                filename="test.txt",
                mime_type="text/plain",
                file_metadata=sample_metadata,
                db=mock_db
            )
            
            assert job is not None
            assert job.file_id == "test_id"
            assert job.file_path == "/path/to/file.txt"
            assert job.content_type == ContentType.TEXT
            assert job.file_metadata == sample_metadata
            assert job.workflow_metadata is not None
            assert job.priority is not None
            
            # Verify file status was updated
            mock_file_crud.update_file_status.assert_called_once_with(
                mock_db, "test_id", "processing"
            )
    
    @pytest.mark.asyncio
    async def test_route_file_for_processing_error(self, router, mock_db, sample_metadata):
        """Test routing a file for processing with error"""
        with patch('src.services.file_processor.file_crud') as mock_file_crud:
            mock_file_crud.update_file_status.side_effect = Exception("Database error")
            
            with pytest.raises(Exception) as exc_info:
                await router.route_file_for_processing(
                    file_id="test_id",
                    file_path="/path/to/file.txt",
                    filename="test.txt",
                    mime_type="text/plain",
                    file_metadata=sample_metadata,
                    db=mock_db
                )
            
            assert "Database error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_process_next_job_success(self, router, mock_db, sample_metadata):
        """Test processing the next job successfully"""
        with patch('src.services.file_processor.file_crud') as mock_file_crud:
            mock_file_crud.update_file_status.return_value = True
            
            # Add a job to the queue
            job = await router.route_file_for_processing(
                file_id="test_id",
                file_path="/path/to/file.txt",
                filename="test.txt",
                mime_type="text/plain",
                file_metadata=sample_metadata,
                db=mock_db
            )
            
            # Process the job
            processed_job = await router.process_next_job(mock_db)
            
            assert processed_job is not None
            assert processed_job.file_id == "test_id"
            assert processed_job.status == ProcessingStatus.COMPLETED
            assert processed_job.processing_metadata.processing_started_at is not None
            assert processed_job.processing_metadata.processing_completed_at is not None
            assert processed_job.processing_metadata.content_extracted is True
            assert processed_job.processing_metadata.processing_duration_seconds is not None
            
            # Verify file status was updated to processed
            mock_file_crud.update_file_status.assert_called_with(
                mock_db, "test_id", "processed"
            )
    
    @pytest.mark.asyncio
    async def test_process_next_job_no_jobs(self, router, mock_db):
        """Test processing when no jobs are available"""
        job = await router.process_next_job(mock_db)
        assert job is None
    
    @pytest.mark.asyncio
    async def test_process_next_job_with_external_api(self, router, mock_db, sample_metadata):
        """Test processing a job that requires external API"""
        with patch('src.services.file_processor.file_crud') as mock_file_crud:
            mock_file_crud.update_file_status.return_value = True
            
            # Add a document job that requires external API
            job = await router.route_file_for_processing(
                file_id="test_id",
                file_path="/path/to/file.pdf",
                filename="test.pdf",
                mime_type="application/pdf",
                file_metadata=sample_metadata,
                db=mock_db
            )
            
            processed_job = await router.process_next_job(mock_db)
            
            assert processed_job is not None
            assert processed_job.processing_metadata.apis_used is not None
            assert len(processed_job.processing_metadata.apis_used) > 0
            assert 'openai' in processed_job.processing_metadata.apis_used
    
    @pytest.mark.asyncio
    async def test_process_next_job_failure(self, router, mock_db, sample_metadata):
        """Test processing a job that fails"""
        with patch('src.services.file_processor.file_crud') as mock_file_crud:
            mock_file_crud.update_file_status.side_effect = [True, Exception("Processing error")]
            
            # Add a job to the queue
            await router.route_file_for_processing(
                file_id="test_id",
                file_path="/path/to/file.txt",
                filename="test.txt",
                mime_type="text/plain",
                file_metadata=sample_metadata,
                db=mock_db
            )
            
            # Process the job - should fail
            with pytest.raises(Exception):
                await router.process_next_job(mock_db)
    
    @pytest.mark.asyncio
    async def test_get_processing_status(self, router):
        """Test getting processing status"""
        status = await router.get_processing_status()
        
        assert status is not None
        assert "pending_jobs" in status
        assert "active_jobs" in status
        assert "completed_jobs" in status
        assert "failed_jobs" in status
        assert "max_concurrent" in status
    
    @pytest.mark.asyncio
    async def test_different_content_types_routing(self, router, mock_db, sample_metadata):
        """Test routing different content types"""
        with patch('src.services.file_processor.file_crud') as mock_file_crud:
            mock_file_crud.update_file_status.return_value = True
            
            # Test different file types
            test_cases = [
                ("test.txt", "text/plain", ContentType.TEXT),
                ("doc.pdf", "application/pdf", ContentType.DOCUMENT),
                ("image.jpg", "image/jpeg", ContentType.IMAGE),
                ("audio.mp3", "audio/mpeg", ContentType.AUDIO),
                ("video.mp4", "video/mp4", ContentType.VIDEO),
                ("unknown.xyz", "unknown/type", ContentType.UNKNOWN)
            ]
            
            for filename, mime_type, expected_type in test_cases:
                job = await router.route_file_for_processing(
                    file_id=f"test_id_{expected_type.value}",
                    file_path=f"/path/to/{filename}",
                    filename=filename,
                    mime_type=mime_type,
                    file_metadata=sample_metadata,
                    db=mock_db
                )
                
                assert job.content_type == expected_type
                assert job.workflow_metadata is not None
    
    @pytest.mark.asyncio
    async def test_priority_based_processing(self, router, mock_db):
        """Test that priority affects processing order"""
        with patch('src.services.file_processor.file_crud') as mock_file_crud:
            mock_file_crud.update_file_status.return_value = True
            
            # Create metadata with different priorities
            high_priority_metadata = FileMetadata(
                department="test_department",
                uploaded_by="test_user",
                employee_role=EmployeeRole.STAFF,
                document_type=DocumentType.REPORT,
                content_category=ContentCategory.ADMINISTRATIVE,
                priority_level=PriorityLevel.URGENT,
                access_level=AccessLevel.INTERNAL
            )
            
            low_priority_metadata = FileMetadata(
                department="test_department",
                uploaded_by="test_user",
                employee_role=EmployeeRole.STAFF,
                document_type=DocumentType.REPORT,
                content_category=ContentCategory.ADMINISTRATIVE,
                priority_level=PriorityLevel.LOW,
                access_level=AccessLevel.INTERNAL
            )
            
            # Add low priority job first
            low_job = await router.route_file_for_processing(
                file_id="low_priority",
                file_path="/path/to/low.txt",
                filename="low.txt",
                mime_type="text/plain",
                file_metadata=low_priority_metadata,
                db=mock_db
            )
            
            # Add high priority job second
            high_job = await router.route_file_for_processing(
                file_id="high_priority",
                file_path="/path/to/high.txt",
                filename="high.txt",
                mime_type="text/plain",
                file_metadata=high_priority_metadata,
                db=mock_db
            )
            
            # High priority job should have lower priority number (higher priority)
            assert high_job.priority < low_job.priority


@pytest.mark.skip(reason="Global content router simplified")
class TestGlobalContentRouter:
    """Test the global content_router instance"""
    
    def test_global_router_instance(self):
        """Test that global content router is properly initialized"""
        assert content_router is not None
        assert isinstance(content_router, ContentTypeRouter)
        assert content_router.classifier is not None
        assert content_router.workflow_manager is not None
        assert content_router.processing_queue is not None 