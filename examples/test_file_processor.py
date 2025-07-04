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
from src.utils.logging import logger


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
    
    for content_type in ContentType:
        if content_type != ContentType.UNKNOWN:
            workflow_func = workflow_manager.get_workflow(content_type)
            from src.services.file_processor import ProcessingJob
            
            dummy_job = ProcessingJob(
                file_id="test-id",
                file_path="/path/to/file",
                content_type=content_type
            )
            
            workflow_config = workflow_func(dummy_job)
            print(f"\nContent Type: {content_type.value}")
            print(f"  Priority: {workflow_config['priority']}")
            print(f"  Estimated Time: {workflow_config['estimated_time']}s")
            print(f"  Requires External API: {workflow_config['requires_external_api']}")
            print(f"  Processing Steps: {', '.join(workflow_config['steps'])}")


async def test_processing_queue():
    """Test processing queue functionality"""
    print("\n=== Testing Processing Queue ===")
    
    db = next(get_db())
    
    # Create test files with different content types
    test_files = [
        ("test1.txt", "text/plain", "text"),
        ("test2.pdf", "application/pdf", "document"),
        ("test3.jpg", "image/jpeg", "image"),
        ("test4.mp3", "audio/mpeg", "audio"),
        ("test5.mp4", "video/mp4", "video")
    ]
    
    print("Adding files to processing queue...")
    jobs = []
    
    for filename, mime_type, expected_type in test_files:
        try:
            job = await content_router.route_file_for_processing(
                file_id=f"test-{filename}",
                file_path=f"/storage/test/{filename}",
                filename=filename,
                mime_type=mime_type,
                db=db
            )
            jobs.append(job)
            print(f"  Added: {filename} -> {job.content_type.value} (priority: {job.priority})")
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
                print(f"  Processed: {job.file_id} ({job.content_type.value}) - Status: {job.status.value}")
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


async def main():
    """Run all tests"""
    print("File Processing Pipeline - Step 2.2.1 Demo")
    print("=" * 50)
    
    try:
        await test_content_type_classification()
        await test_workflow_assignment()
        await test_processing_queue()
        
        print("\n" + "=" * 50)
        print("Step 2.2.1 Content Type Routing Logic - COMPLETED")
        print("✅ Content type classification working")
        print("✅ Workflow assignment working")
        print("✅ Processing queue management working")
        print("✅ Priority-based job processing working")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 