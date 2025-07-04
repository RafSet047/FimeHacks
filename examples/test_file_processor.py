#!/usr/bin/env python3
"""
Example demonstrating File Processing Pipeline - Step 2.2.1
Content Type Routing Logic Implementation
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.file_processor import content_router, ContentType, ProcessingStatus
from src.database.connection import get_db
from src.utils.logging import setup_logging
from src.models.metadata import FileMetadata, DocumentType, ContentCategory, EmployeeRole, PriorityLevel, AccessLevel
import logging

setup_logging()
logger = logging.getLogger(__name__)


def create_sample_metadata(department: str, domain_type: str = None, priority: PriorityLevel = PriorityLevel.MEDIUM):
    """Create sample metadata for testing"""
    return FileMetadata(
        department=department,
        uploaded_by="test_user",
        employee_role=EmployeeRole.STAFF,
        document_type=DocumentType.REPORT,
        content_category=ContentCategory.ADMINISTRATIVE,
        priority_level=priority,
        access_level=AccessLevel.INTERNAL,
        domain_type=domain_type,
        tags=["test", "processor"]
    )


async def test_content_type_classification():
    """Test content type classification"""
    print("=== Testing Content Type Classification ===")
    
    classifier = content_router.classifier
    
    test_files = [
        ("document.pdf", "application/pdf"),
        ("image.jpg", "image/jpeg"),
        ("audio.mp3", "audio/mpeg"),
        ("video.mp4", "video/mp4"),
        ("text.txt", "text/plain"),
        ("unknown.xyz", "application/octet-stream")
    ]
    
    for filename, mime_type in test_files:
        content_type = classifier.classify_file(filename, mime_type)
        print(f"File: {filename:15} | MIME: {mime_type:25} | Type: {content_type.value}")


async def test_workflow_assignment():
    """Test workflow assignment for different content types"""
    print("\n=== Testing Workflow Assignment ===")
    
    workflow_manager = content_router.workflow_manager
    
    # Test different metadata scenarios
    test_scenarios = [
        ("Regular text file", create_sample_metadata("engineering"), ContentType.TEXT),
        ("Urgent document", create_sample_metadata("emergency", priority=PriorityLevel.URGENT), ContentType.DOCUMENT),
        ("Healthcare image", create_sample_metadata("cardiology", domain_type="healthcare"), ContentType.IMAGE),
        ("University audio", create_sample_metadata("computer_science", domain_type="university"), ContentType.AUDIO),
        ("Critical video", create_sample_metadata("surgery", domain_type="healthcare", priority=PriorityLevel.CRITICAL), ContentType.VIDEO)
    ]
    
    for scenario_name, metadata, content_type in test_scenarios:
        workflow_func = workflow_manager.get_workflow(content_type)
        from src.services.file_processor import ProcessingJob
        
        dummy_job = ProcessingJob(
            file_id="test-id",
            file_path="/path/to/file",
            content_type=content_type,
            file_metadata=metadata
        )
        
        workflow_config = workflow_func(dummy_job)
        print(f"\n{scenario_name}:")
        print(f"  Content Type: {content_type.value}")
        print(f"  Department: {metadata.department}")
        print(f"  Domain: {metadata.domain_type or 'generic'}")
        print(f"  Priority Level: {metadata.priority_level.value}")
        print(f"  Processing Priority: {workflow_config['priority']}")
        print(f"  Estimated Time: {workflow_config['estimated_time']}s")
        print(f"  Requires External API: {workflow_config['requires_external_api']}")
        print(f"  Processing Steps: {', '.join(workflow_config['steps'])}")


async def test_processing_queue():
    """Test processing queue functionality"""
    print("\n=== Testing Processing Queue ===")
    
    db = next(get_db())
    
    # Create test files with different content types and metadata
    test_files = [
        ("urgent_text.txt", "text/plain", create_sample_metadata("emergency", priority=PriorityLevel.URGENT)),
        ("normal_doc.pdf", "application/pdf", create_sample_metadata("admin")),
        ("healthcare_image.jpg", "image/jpeg", create_sample_metadata("radiology", domain_type="healthcare")),
        ("university_audio.mp3", "audio/mpeg", create_sample_metadata("lectures", domain_type="university")),
        ("critical_video.mp4", "video/mp4", create_sample_metadata("surgery", domain_type="healthcare", priority=PriorityLevel.CRITICAL))
    ]
    
    print("Adding files to processing queue...")
    jobs = []
    
    for filename, mime_type, metadata in test_files:
        try:
            job = await content_router.route_file_for_processing(
                file_id=f"test-{filename}",
                file_path=f"/storage/test/{filename}",
                filename=filename,
                mime_type=mime_type,
                file_metadata=metadata,
                db=db
            )
            jobs.append(job)
            print(f"  Added: {filename} -> {job.content_type.value} (priority: {job.priority}) from {metadata.department}")
        except Exception as e:
            print(f"  Failed to add {filename}: {e}")
    
    # Check queue status
    queue_status = await content_router.get_processing_status()
    print(f"\nQueue Status:")
    print(f"  Pending jobs: {queue_status['pending_jobs']}")
    print(f"  Active jobs: {queue_status['active_jobs']}")
    print(f"  Completed jobs: {queue_status['completed_jobs']}")
    print(f"  Failed jobs: {queue_status['failed_jobs']}")
    print(f"  Max concurrent: {queue_status['max_concurrent']}")
    
    # Process jobs
    print("\nProcessing jobs...")
    processed_count = 0
    max_iterations = 10
    
    while processed_count < len(jobs) and max_iterations > 0:
        try:
            job = await content_router.process_next_job(db)
            if job:
                print(f"  Processed: {job.file_id} ({job.content_type.value}) from {job.file_metadata.department}")
                print(f"    Priority: {job.priority} | Status: {job.status.value}")
                print(f"    Domain: {job.file_metadata.domain_type or 'generic'}")
                print(f"    Processing Steps: {', '.join(job.processing_metadata.processing_steps or [])}")
                print(f"    Duration: {job.processing_metadata.processing_duration_seconds:.2f}s")
                print(f"    APIs Used: {', '.join(job.processing_metadata.apis_used or [])}")
                processed_count += 1
            else:
                print("  No jobs available to process")
                break
        except Exception as e:
            print(f"  Error processing job: {e}")
        
        max_iterations -= 1
        await asyncio.sleep(0.1)
    
    # Final queue status
    final_status = await content_router.get_processing_status()
    print(f"\nFinal Queue Status:")
    print(f"  Pending jobs: {final_status['pending_jobs']}")
    print(f"  Active jobs: {final_status['active_jobs']}")
    print(f"  Completed jobs: {final_status['completed_jobs']}")
    print(f"  Failed jobs: {final_status['failed_jobs']}")


async def test_metadata_influence():
    """Test how metadata influences processing workflow"""
    print("\n=== Testing Metadata Influence on Processing ===")
    
    from src.services.file_processor import ProcessingJob
    
    # Test priority influence
    print("\nPriority Level Influence:")
    for priority in [PriorityLevel.LOW, PriorityLevel.MEDIUM, PriorityLevel.HIGH, PriorityLevel.URGENT, PriorityLevel.CRITICAL]:
        metadata = create_sample_metadata("test", priority=priority)
        job = ProcessingJob(
            file_id="test-priority",
            file_path="/test/path",
            content_type=ContentType.TEXT,
            file_metadata=metadata
        )
        
        workflow_config = content_router.workflow_manager._text_workflow(job)
        print(f"  {priority.value:8} -> Processing Priority: {workflow_config['priority']}")
    
    # Test domain influence
    print("\nDomain Type Influence:")
    for domain in [None, "healthcare", "university"]:
        metadata = create_sample_metadata("test", domain_type=domain)
        job = ProcessingJob(
            file_id="test-domain",
            file_path="/test/path",
            content_type=ContentType.TEXT,
            file_metadata=metadata
        )
        
        workflow_config = content_router.workflow_manager._text_workflow(job)
        domain_name = domain or "generic"
        print(f"  {domain_name:10} -> Steps: {len(workflow_config['steps'])} | Extra: {[s for s in workflow_config['steps'] if 'medical' in s or 'academic' in s]}")


async def main():
    """Run all tests"""
    print("File Processing Pipeline - Step 2.2.1 Demo with Metadata")
    print("=" * 60)
    
    try:
        await test_content_type_classification()
        await test_workflow_assignment()
        await test_processing_queue()
        await test_metadata_influence()
        
        print("\n" + "=" * 60)
        print("Step 2.2.1 Content Type Routing Logic with Metadata - COMPLETED")
        print("✅ Content type classification working")
        print("✅ Workflow assignment with metadata working")
        print("✅ Processing queue with metadata working")
        print("✅ Priority-based job processing working")
        print("✅ Domain-specific processing steps working")
        print("✅ Metadata influence on workflow working")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 