#!/usr/bin/env python3
"""
Demo script showing the simplified workflow system usage
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.workflow_manager import workflow_manager
from services.workflows import TextWorkflow
from services.content_types import ContentType
from models.metadata import FileMetadata
from utils.logging import setup_logging


async def main():
    # Setup logging
    setup_logging()
    
    # Create a sample text file
    sample_file_path = Path(__file__).parent.parent / "assets" / "sample_document.txt"
    
    if not sample_file_path.exists():
        print(f"Creating sample file at {sample_file_path}")
        sample_file_path.parent.mkdir(exist_ok=True)
        with open(sample_file_path, 'w') as f:
            f.write("""
This is a sample document for testing the workflow system.
It contains multiple sentences and paragraphs.

Healthcare terms: patient, diagnosis, treatment, medication, doctor, hospital.
Academic terms: research, analysis, publication, methodology, hypothesis.

Key findings:
- The system processes text files successfully
- Embeddings are generated for semantic search
- Keywords are extracted automatically
- Content is structured for database storage

This document demonstrates the capabilities of the multimodal AI system
designed for healthcare and university environments.
""")
    
    # Create file metadata
    file_metadata = FileMetadata(
        domain_type="healthcare",
        department="cardiology",
        project_name="patient_records",
        document_type="patient_record",
        content_category="clinical",
        priority_level="high",
        access_level="restricted",
        tags=["patient", "cardiology", "clinical"],
        employee_role="doctor",
        uploaded_by="dr_smith"
    )
    
    print("=" * 60)
    print("SIMPLIFIED WORKFLOW SYSTEM DEMO")
    print("=" * 60)
    
    # Register workflows (this would normally be done at startup)
    workflow_manager.register_workflow(ContentType.TEXT, TextWorkflow)
    
    # Execute workflow
    print(f"\nProcessing file: {sample_file_path}")
    print(f"File metadata: {file_metadata.domain_type} - {file_metadata.department}")
    
    try:
        workflow_output = workflow_manager.execute_workflow(
            content_type=ContentType.TEXT,
            file_id="demo_file_001",
            file_path=str(sample_file_path),
            filename="sample_document.txt",
            mime_type="text/plain",
            file_metadata=file_metadata
        )
        
        print(f"\nWorkflow completed successfully: {workflow_output.success}")
        print(f"Processing time: {workflow_output.processing_time:.2f} seconds")
        
        if workflow_output.success:
            print(f"\nExtracted content preview:")
            print(f"Content length: {len(workflow_output.extracted_content)} characters")
            print(f"Preview: {workflow_output.extracted_content[:200]}...")
            
            print(f"\nStructured data:")
            for key, value in workflow_output.structured_data.items():
                if key == "keywords":
                    print(f"  {key}: {value[:5]}...")  # Show first 5 keywords
                else:
                    print(f"  {key}: {value}")
            
            print(f"\nEmbeddings generated: {len(workflow_output.embeddings)} chunks")
            if workflow_output.embeddings:
                print(f"Embedding dimension: {len(workflow_output.embeddings[0])}")
        else:
            print(f"Workflow failed: {workflow_output.error_message}")
            
    except Exception as e:
        print(f"Error executing workflow: {e}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 