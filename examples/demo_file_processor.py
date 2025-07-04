#!/usr/bin/env python3
"""
Simple demo of File Processing Pipeline - Step 2.2.1
Run this to see the content type routing logic in action
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.file_processor import content_router, ContentType
from src.utils.logging import setup_logging
from src.models.metadata import FileMetadata, DocumentType, ContentCategory, EmployeeRole, PriorityLevel, AccessLevel
import logging

setup_logging()
logger = logging.getLogger(__name__)


def create_sample_metadata(department: str, domain_type: str = None, priority: PriorityLevel = PriorityLevel.MEDIUM):
    """Create sample metadata for testing"""
    return FileMetadata(
        department=department,
        uploaded_by="demo_user",
        employee_role=EmployeeRole.STAFF,
        document_type=DocumentType.REPORT,
        content_category=ContentCategory.ADMINISTRATIVE,
        priority_level=priority,
        access_level=AccessLevel.INTERNAL,
        domain_type=domain_type,
        tags=["demo", "test"]
    )


def demo_content_classification():
    """Demo content type classification"""
    print("\n🔍 CONTENT TYPE CLASSIFICATION DEMO")
    print("=" * 50)
    
    # Sample files to classify
    test_files = [
        ("research_paper.pdf", "application/pdf"),
        ("profile_photo.jpg", "image/jpeg"),
        ("meeting_recording.mp3", "audio/mpeg"),
        ("training_video.mp4", "video/mp4"),
        ("notes.txt", "text/plain"),
        ("data.csv", "text/csv"),
        ("presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
        ("mystery_file.xyz", "application/octet-stream")
    ]
    
    classifier = content_router.classifier
    
    for filename, mime_type in test_files:
        content_type = classifier.classify_file(filename, mime_type)
        print(f"📄 {filename:<20} → {content_type.value.upper()}")


def demo_workflow_assignment():
    """Demo workflow assignment for different content types"""
    print("\n⚙️  WORKFLOW ASSIGNMENT DEMO")
    print("=" * 50)
    
    from src.services.file_processor import ProcessingJob
    
    workflow_manager = content_router.workflow_manager
    
    # Test scenarios with different metadata
    test_scenarios = [
        ("Regular Text", ContentType.TEXT, create_sample_metadata("engineering")),
        ("Urgent Document", ContentType.DOCUMENT, create_sample_metadata("emergency", priority=PriorityLevel.URGENT)),
        ("Healthcare Image", ContentType.IMAGE, create_sample_metadata("radiology", domain_type="healthcare")),
        ("University Audio", ContentType.AUDIO, create_sample_metadata("lectures", domain_type="university")),
        ("Critical Video", ContentType.VIDEO, create_sample_metadata("surgery", domain_type="healthcare", priority=PriorityLevel.CRITICAL)),
    ]
    
    for scenario_name, content_type, metadata in test_scenarios:
        print(f"\n📋 {scenario_name.upper()} WORKFLOW:")
        
        # Create job with metadata
        dummy_job = ProcessingJob(
            file_id=f"demo-{content_type.value}",
            file_path=f"/path/to/{content_type.value}_file",
            content_type=content_type,
            file_metadata=metadata
        )
        
        # Get workflow
        workflow_func = workflow_manager.get_workflow(content_type)
        workflow_config = workflow_func(dummy_job)
        
        print(f"   Department: {metadata.department}")
        print(f"   Domain: {metadata.domain_type or 'generic'}")
        print(f"   Priority Level: {metadata.priority_level.value}")
        print(f"   Processing Priority: {workflow_config['priority']}")
        print(f"   Est. Time: {workflow_config['estimated_time']}s")
        print(f"   External API: {workflow_config['requires_external_api']}")
        print(f"   Steps: {' → '.join(workflow_config['steps'])}")


async def demo_processing_queue():
    """Demo processing queue functionality"""
    print("\n🔄 PROCESSING QUEUE DEMO")
    print("=" * 50)
    
    # Create mock files to process with different metadata
    mock_files = [
        ("urgent_text.txt", "text/plain", create_sample_metadata("emergency", priority=PriorityLevel.URGENT)),
        ("large_video.mp4", "video/mp4", create_sample_metadata("media", priority=PriorityLevel.LOW)),
        ("important_doc.pdf", "application/pdf", create_sample_metadata("legal", priority=PriorityLevel.HIGH)),
        ("healthcare_image.jpg", "image/jpeg", create_sample_metadata("radiology", domain_type="healthcare")),
        ("university_audio.mp3", "audio/mpeg", create_sample_metadata("lectures", domain_type="university"))
    ]
    
    print("📥 Adding files to processing queue...")
    
    # Add files to queue (without database operations for demo)
    jobs = []
    for filename, mime_type, metadata in mock_files:
        content_type = content_router.classifier.classify_file(filename, mime_type)
        
        from src.services.file_processor import ProcessingJob
        job = ProcessingJob(
            file_id=f"demo-{filename}",
            file_path=f"/mock/path/{filename}",
            content_type=content_type,
            file_metadata=metadata
        )
        
        # Get workflow config
        workflow_func = content_router.workflow_manager.get_workflow(content_type)
        workflow_config = workflow_func(job)
        job.workflow_metadata = workflow_config
        job.priority = workflow_config.get("priority", 5)
        
        await content_router.processing_queue.add_job(job)
        jobs.append(job)
        
        print(f"   ✅ {filename} → {content_type.value} (priority: {job.priority}) from {metadata.department}")
    
    # Show queue status
    status = await content_router.get_processing_status()
    print(f"\n📊 Queue Status: {status['pending_jobs']} pending, {status['active_jobs']} active")
    
    # Process some jobs
    print("\n🚀 Processing jobs...")
    processed = 0
    max_process = 3
    
    while processed < max_process:
        job = await content_router.processing_queue.get_next_job()
        if not job:
            break
            
        print(f"   🔄 Processing: {job.file_id} ({job.content_type.value}) from {job.file_metadata.department}")
        print(f"      Domain: {job.file_metadata.domain_type or 'generic'}")
        print(f"      Priority Level: {job.file_metadata.priority_level.value}")
        
        # Simulate processing
        await asyncio.sleep(0.5)
        
        # Complete job
        await content_router.processing_queue.complete_job(job, success=True)
        print(f"   ✅ Completed: {job.file_id}")
        
        processed += 1
    
    # Final status
    final_status = await content_router.get_processing_status()
    print(f"\n📊 Final Status: {final_status['completed_jobs']} completed, {final_status['pending_jobs']} pending")


def demo_metadata_influence():
    """Demo how metadata influences processing"""
    print("\n🎯 METADATA INFLUENCE DEMO")
    print("=" * 50)
    
    from src.services.file_processor import ProcessingJob
    
    print("Priority Level Impact:")
    for priority in [PriorityLevel.LOW, PriorityLevel.MEDIUM, PriorityLevel.HIGH, PriorityLevel.URGENT, PriorityLevel.CRITICAL]:
        metadata = create_sample_metadata("test", priority=priority)
        job = ProcessingJob(
            file_id="test",
            file_path="/test",
            content_type=ContentType.TEXT,
            file_metadata=metadata
        )
        
        workflow_config = content_router.workflow_manager._text_workflow(job)
        print(f"   {priority.value:8} → Processing Priority: {workflow_config['priority']}")
    
    print("\nDomain-Specific Processing:")
    domains = [
        (None, "Generic"),
        ("healthcare", "Healthcare"),
        ("university", "University")
    ]
    
    for domain_type, domain_name in domains:
        metadata = create_sample_metadata("test", domain_type=domain_type)
        job = ProcessingJob(
            file_id="test",
            file_path="/test",
            content_type=ContentType.TEXT,
            file_metadata=metadata
        )
        
        workflow_config = content_router.workflow_manager._text_workflow(job)
        extra_steps = [s for s in workflow_config['steps'] if 'medical' in s or 'academic' in s]
        print(f"   {domain_name:10} → Steps: {len(workflow_config['steps'])} | Extra: {extra_steps}")


async def main():
    """Main demo function"""
    print("🚀 FILE PROCESSOR DEMO - Step 2.2.1 with Metadata")
    print("Content Type Routing Logic")
    print("=" * 70)
    
    try:
        # Run demos
        demo_content_classification()
        demo_workflow_assignment()
        await demo_processing_queue()
        demo_metadata_influence()
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("📝 Key Observations:")
        print("   • Different file types get different processing workflows")
        print("   • Priority level affects processing order (urgent = priority 0)")
        print("   • Domain type adds specialized processing steps")
        print("   • Healthcare files get medical entity extraction")
        print("   • University files get academic content analysis")
        print("   • Metadata flows through entire processing pipeline")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")


if __name__ == "__main__":
    print("Starting File Processor Demo with Metadata...")
    asyncio.run(main()) 