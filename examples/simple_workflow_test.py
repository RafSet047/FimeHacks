#!/usr/bin/env python3
"""
Simple workflow test without database dependencies
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.workflow_base import WorkflowInput, WorkflowOutput
from services.workflows.text_workflow import TextWorkflow
from services.content_types import ContentType


class SimpleFileMetadata:
    def __init__(self):
        self.domain_type = "healthcare"
        self.department = "cardiology"
        self.project_name = "patient_records"
        self.document_type = "patient_record"
        self.content_category = "clinical"
        self.priority_level = "high"
        self.access_level = "restricted"
        self.tags = ["patient", "cardiology", "clinical"]
        self.employee_role = "doctor"
        self.uploaded_by = "dr_smith"
    
    def to_dict(self):
        return self.__dict__


def main():
    print("=" * 60)
    print("SIMPLE WORKFLOW TEST")
    print("=" * 60)
    
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
    
    # Create simplified file metadata
    file_metadata = SimpleFileMetadata()
    
    # Create workflow input
    workflow_input = WorkflowInput(
        file_id="test_file_001",
        file_path=str(sample_file_path),
        filename="sample_document.txt",
        mime_type="text/plain",
        file_metadata=file_metadata
    )
    
    print(f"Testing file: {sample_file_path}")
    print(f"File metadata: {file_metadata.domain_type} - {file_metadata.department}")
    
    # Test text workflow
    try:
        text_workflow = TextWorkflow()
        result = text_workflow.process(workflow_input)
        
        print(f"\nWorkflow completed: {result.success}")
        print(f"Processing time: {result.processing_time:.2f} seconds")
        
        if result.success:
            print(f"\nExtracted content length: {len(result.extracted_content)} characters")
            print(f"Content preview: {result.extracted_content[:200]}...")
            
            print(f"\nStructured data:")
            for key, value in result.structured_data.items():
                if key == "keywords":
                    print(f"  {key}: {value[:5]}...")  # Show first 5 keywords
                elif key == "summary":
                    print(f"  {key}: {value[:100]}...")  # Show summary preview
                else:
                    print(f"  {key}: {value}")
            
            print(f"\nEmbeddings generated: {len(result.embeddings)} chunks")
            if result.embeddings:
                print(f"Embedding dimension: {len(result.embeddings[0])}")
        else:
            print(f"Workflow failed: {result.error_message}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main() 