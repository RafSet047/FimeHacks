#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.services.text_chunking import TextChunker, ChunkingStrategy, ChunkingConfig
from src.services.document_extractor import PlainTextExtractor

def create_sample_document():
    """Create a sample document with structured content for testing."""
    content = """Healthcare Quality Improvement Protocol

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
- Document and share best practices"""
    
    temp_file = Path("test_document.txt")
    temp_file.write_text(content)
    return temp_file

def test_chunking():
    """Test the text chunking functionality."""
    print("\nText Chunking Test")
    print("=" * 80)
    
    # Create sample document
    doc_path = create_sample_document()
    print(f"Created test document: {doc_path}")
    
    try:
        # Extract text
        extractor = PlainTextExtractor()
        text = extractor.extract_text(str(doc_path))
        print(f"\nExtracted text length: {len(text)} characters")
        
        # Initialize chunking service with specific config
        chunker = TextChunker()
        
        # Test different configurations
        configs = [
            ChunkingConfig(chunk_size=100, chunk_overlap=20),
            ChunkingConfig(chunk_size=200, chunk_overlap=30),
            ChunkingConfig(chunk_size=500, chunk_overlap=50)
        ]
        
        for config in configs:
            print(f"\nTesting with chunk_size={config.chunk_size}, overlap={config.chunk_overlap}")
            print("-" * 80)
            
            chunks = chunker.chunk_text(
                text=text,
                strategy=ChunkingStrategy.RECURSIVE,
                config=config
            )
            
            print(f"Number of chunks created: {len(chunks)}")
            
            for i, chunk in enumerate(chunks, 1):
                print(f"\nChunk {i}:")
                print(f"Length: {len(chunk.page_content)} characters")
                print(f"Content:\n{chunk.page_content}")
                print(f"Metadata: {chunk.metadata}")
                print("-" * 40)
    
    finally:
        # Cleanup
        doc_path.unlink()
        print("\nTest document cleaned up")

if __name__ == "__main__":
    test_chunking() 