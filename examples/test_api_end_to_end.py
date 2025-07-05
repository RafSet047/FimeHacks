#!/usr/bin/env python3

import sys
import os
import json
import asyncio
import requests
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from examples.demo_end_to_end_workflow import EndToEndWorkflow

async def upload_file(file_path: str) -> dict:
    """Upload file using the API endpoint"""
    
    # Prepare metadata
    metadata = {
        "department": "test",
        "uploaded_by": "test_user",
        "employee_role": "staff",
        "document_type": "other",
        "content_category": "other",
        "priority_level": "low",
        "access_level": "public",
        "tags": ["test", "chunking", "api"]
    }
    
    # Create multipart form data
    files = {
        'file': ('test.txt', open(file_path, 'rb'), 'text/plain'),
        'metadata': (None, json.dumps(metadata))
    }
    
    # Upload file
    response = requests.post(
        'http://localhost:8000/api/files/upload',
        files=files
    )
    
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.json()['detail']}")
    
    return response.json()

async def main():
    # Create test file
    test_file = "test_document.txt"
    with open(test_file, "w") as f:
        f.write("""Healthcare Quality Improvement Protocol

This document outlines the standard procedures for implementing quality improvement 
initiatives in healthcare settings. Quality improvement is essential for enhancing 
patient care and operational efficiency.

Key Components:
1. Assessment of current practices
2. Identification of improvement opportunities
3. Implementation of evidence-based solutions
4. Monitoring and evaluation of results

Implementation Guidelines:
- Establish clear objectives and metrics
- Engage all stakeholders in the process
- Provide adequate training and resources
- Monitor progress against established benchmarks
- Document and share best practices""")

    try:
        print("\nAPI and End-to-End Processing Test")
        print("=" * 80)
        
        # Step 1: Upload via API
        print("\n1. Uploading file via API...")
        upload_result = await upload_file(test_file)
        print(f"Upload successful! File ID: {upload_result['file_id']}")
        print(json.dumps(upload_result, indent=2))
        
        # Step 2: Initialize workflow
        print("\n2. Initializing end-to-end workflow...")
        workflow = EndToEndWorkflow()
        
        # Step 3: Process the uploaded file
        print("\n3. Processing file through workflow...")
        stored_path = f"storage/2025/07/05/{upload_result['file_id']}.txt"
        workflow_result = await workflow.process_file_end_to_end(
            file_path=stored_path,
            collection_name="test_chunking"
        )
        
        # Step 4: Test similarity search
        print("\n4. Testing similarity search...")
        search_results = await workflow.search_similar_content(
            query_text="quality improvement in healthcare",
            collection_name="test_chunking",
            limit=3
        )
        
        # Step 5: Show stored documents
        print("\n5. Reading stored documents...")
        stored_docs = workflow.read_stored_documents(
            collection_name="test_chunking",
            limit=5
        )
        
        print("\nTest completed successfully!")
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)
            print(f"\nCleaned up test file: {test_file}")

if __name__ == "__main__":
    asyncio.run(main()) 