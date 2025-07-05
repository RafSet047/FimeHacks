#!/usr/bin/env python3

import requests
import json
import os
import tempfile
from pathlib import Path
import time

# API Configuration
API_BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
PROCESS_ENDPOINT = f"{API_BASE_URL}/process"
SEARCH_ENDPOINT = f"{API_BASE_URL}/search"

def print_separator(title):
    """Print a nice separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_health():
    """Test the health endpoint"""
    print_separator("TESTING HEALTH ENDPOINT")
    
    try:
        print(f"Making request to: {HEALTH_ENDPOINT}")
        response = requests.get(HEALTH_ENDPOINT)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful!")
            print(f"Overall Status: {data.get('status')}")
            print("Service Status:")
            services = data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {service}: {status}")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed with error: {e}")
        return False

def create_test_document():
    """Create a test document"""
    test_content = """
    Healthcare Quality Improvement Protocol

    This document outlines the standard procedures for implementing quality improvement 
    initiatives in healthcare settings. Quality improvement is essential for maintaining 
    high standards of patient care and ensuring optimal outcomes.

    Key Components:
    1. Assessment of current practices and baseline metrics
    2. Identification of improvement opportunities through data analysis
    3. Implementation of evidence-based solutions and best practices
    4. Monitoring and evaluation of results against established benchmarks
    5. Continuous refinement of processes based on feedback

    Implementation Guidelines:
    - Establish clear objectives and measurable metrics
    - Engage all stakeholders including patients, staff, and management
    - Provide adequate training and resources for successful implementation
    - Monitor progress against established benchmarks regularly
    - Communicate results transparently to all stakeholders
    - Document lessons learned and best practices for future reference

    The protocol emphasizes the importance of multidisciplinary collaboration, 
    patient-centered care, and data-driven decision making. Regular audits and 
    feedback mechanisms ensure sustained improvement over time.

    This approach has been successfully implemented in numerous healthcare facilities,
    resulting in improved patient satisfaction scores, reduced adverse events, 
    enhanced operational efficiency, and better clinical outcomes.
    """.strip()
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(test_content)
    temp_file.close()
    
    return temp_file.name

def test_process_document():
    """Test the document processing endpoint"""
    print_separator("TESTING DOCUMENT PROCESSING")
    
    # Create test document
    test_file_path = create_test_document()
    
    try:
        print(f"Created test document: {test_file_path}")
        print(f"Making request to: {PROCESS_ENDPOINT}")
        
        # Prepare files and metadata
        files = {
            'file': ('test_document.txt', open(test_file_path, 'rb'), 'text/plain')
        }
        
        metadata = {
            "department": "demo",
            "description": "Healthcare quality improvement protocol for testing",
            "tags": ["healthcare", "quality", "improvement"]
        }
        
        data = {
            'metadata': json.dumps(metadata)
        }
        
        # Make request
        response = requests.post(PROCESS_ENDPOINT, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document processing successful!")
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Chunks Processed: {result.get('chunks_processed')}")
            print(f"Embeddings Generated: {result.get('embeddings_generated')}")
            print(f"Documents Stored: {len(result.get('document_ids', []))}")
            
            # Show first few document IDs
            doc_ids = result.get('document_ids', [])
            if doc_ids:
                print("Document IDs:")
                for i, doc_id in enumerate(doc_ids[:3]):  # Show first 3
                    print(f"  {i+1}. {doc_id}")
                if len(doc_ids) > 3:
                    print(f"  ... and {len(doc_ids) - 3} more")
            
            return True, doc_ids
        else:
            print(f"❌ Document processing failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, []
            
    except Exception as e:
        print(f"❌ Document processing failed with error: {e}")
        return False, []
    
    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
            print(f"Cleaned up test file: {test_file_path}")

def test_search(query_text="healthcare quality improvement"):
    """Test the search endpoint"""
    print_separator("TESTING VECTOR SEARCH")
    
    try:
        print(f"Making request to: {SEARCH_ENDPOINT}")
        print(f"Query: {query_text}")
        
        # Prepare search request
        search_data = {
            "query": query_text,
            "limit": 5,
            "collection_name": "text_embeddings"
        }
        
        # Make request
        response = requests.post(
            SEARCH_ENDPOINT,
            headers={"Content-Type": "application/json"},
            data=json.dumps(search_data)
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Vector search successful!")
            print(f"Query: {result.get('query')}")
            print(f"Total Results: {result.get('total_results')}")
            
            results = result.get('results', [])
            if results:
                print("\nSearch Results:")
                for i, res in enumerate(results, 1):
                    print(f"\n{i}. Similarity Score: {res.get('score', 0):.4f}")
                    print(f"   Document ID: {res.get('id')}")
                    print(f"   Department: {res.get('department')}")
                    print(f"   Content Type: {res.get('content_type')}")
                    
                    # Show metadata if available
                    metadata = res.get('metadata', {})
                    if isinstance(metadata, dict):
                        chunk_text = metadata.get('chunk_text', '')
                        if chunk_text:
                            print(f"   Preview: {chunk_text[:100]}...")
                    
                    print("-" * 40)
            else:
                print("No results found.")
            
            return True
        else:
            print(f"❌ Vector search failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Vector search failed with error: {e}")
        return False

def main():
    """Main test function"""
    print_separator("VECTOR STORE API TEST CLIENT")
    print("This will test all API endpoints of the Vector Store API")
    print("Make sure the API server is running on localhost:8000")
    
    # Wait a moment for user to see the message
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)
    
    # Test 1: Health Check
    health_ok = test_health()
    
    if not health_ok:
        print("\n❌ Health check failed. Make sure the server is running and services are initialized.")
        print("Try running: python src/main.py")
        return
    
    # Test 2: Document Processing
    print("\nWaiting 2 seconds before next test...")
    time.sleep(2)
    
    process_ok, doc_ids = test_process_document()
    
    if not process_ok:
        print("\n❌ Document processing failed. Check server logs for details.")
        return
    
    # Test 3: Vector Search
    print("\nWaiting 2 seconds before next test...")
    time.sleep(2)
    
    search_ok = test_search()
    
    # Summary
    print_separator("TEST SUMMARY")
    print(f"✅ Health Check: {'PASSED' if health_ok else 'FAILED'}")
    print(f"✅ Document Processing: {'PASSED' if process_ok else 'FAILED'}")
    print(f"✅ Vector Search: {'PASSED' if search_ok else 'FAILED'}")
    
    if health_ok and process_ok and search_ok:
        print("\n🎉 All tests passed! Your Vector Store API is working correctly.")
        
        # Additional test queries
        print("\n" + "-"*40)
        print("Testing additional search queries...")
        
        test_queries = [
            "patient care quality",
            "healthcare improvement",
            "clinical outcomes"
        ]
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            test_search(query)
            time.sleep(1)
    else:
        print("\n❌ Some tests failed. Check the server logs and fix the issues.")

if __name__ == "__main__":
    main() 