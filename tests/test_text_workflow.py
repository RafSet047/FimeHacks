#!/usr/bin/env python3
"""
Text Workflow Tests
pytest-compatible test suite for text workflow functionality.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.services.workflows.text_workflow import TextWorkflow
from src.services.workflow_base import WorkflowInput, WorkflowOutput


class MockFileMetadata:
    """Mock file metadata for testing"""
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


@pytest.fixture
def text_workflow():
    """Create TextWorkflow instance"""
    return TextWorkflow()


@pytest.fixture
def mock_file_metadata():
    """Create mock file metadata"""
    return MockFileMetadata()


@pytest.fixture
def sample_text_content():
    """Sample text content for testing"""
    return """
This is a sample document for testing the text workflow system.
It contains multiple sentences and paragraphs for comprehensive testing.

Healthcare terms: patient, diagnosis, treatment, medication, doctor, hospital.
Academic terms: research, analysis, publication, methodology, hypothesis.

Key findings:
- The system processes text files successfully
- Embeddings are generated for semantic search
- Keywords are extracted automatically
- Content is structured for database storage

This document demonstrates the capabilities of the multimodal AI system
designed for healthcare and university environments.

Additional content to test chunking functionality and ensure that the
embedding generation works correctly with longer text content.
"""


@pytest.fixture
def workflow_input(mock_file_metadata):
    """Create WorkflowInput with temporary file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
This is a sample document for testing the text workflow system.
It contains multiple sentences and paragraphs for comprehensive testing.

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
        temp_file_path = f.name
    
    workflow_input = WorkflowInput(
        file_id="test_file_001",
        file_path=temp_file_path,
        filename="test_document.txt",
        mime_type="text/plain",
        file_metadata=mock_file_metadata
    )
    
    yield workflow_input
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestTextWorkflow:
    """Test TextWorkflow main functionality"""
    
    def test_workflow_initialization(self, text_workflow):
        """Test workflow initialization"""
        assert text_workflow.workflow_name == "TextWorkflow"
        assert hasattr(text_workflow, 'logger')
    
    def test_process_success(self, text_workflow, workflow_input):
        """Test successful text processing"""
        result = text_workflow.process(workflow_input)
        
        # Check result structure
        assert isinstance(result, WorkflowOutput)
        assert result.success is True
        assert result.file_id == "test_file_001"
        assert result.error_message is None
        assert result.processing_time >= 0
        
        # Check extracted content
        assert len(result.extracted_content) > 0
        assert "sample document" in result.extracted_content.lower()
        
        # Check structured data
        assert isinstance(result.structured_data, dict)
        assert "word_count" in result.structured_data
        assert "char_count" in result.structured_data
        assert "line_count" in result.structured_data
        assert "keywords" in result.structured_data
        assert "summary" in result.structured_data
        
        # Check embeddings
        assert isinstance(result.embeddings, list)
        assert len(result.embeddings) > 0
        assert isinstance(result.embeddings[0], list)
        assert len(result.embeddings[0]) == 384  # Embedding dimension
    
    def test_process_file_not_found(self, text_workflow, mock_file_metadata):
        """Test processing with non-existent file"""
        workflow_input = WorkflowInput(
            file_id="test_file_002",
            file_path="/non/existent/file.txt",
            filename="nonexistent.txt",
            mime_type="text/plain",
            file_metadata=mock_file_metadata
        )
        
        result = text_workflow.process(workflow_input)
        
        assert result.success is False
        assert result.error_message is not None
        assert result.extracted_content == ""
        assert result.structured_data == {}
        assert result.embeddings == []
    
    def test_process_empty_file(self, text_workflow, mock_file_metadata):
        """Test processing with empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")  # Empty file
            temp_file_path = f.name
        
        try:
            workflow_input = WorkflowInput(
                file_id="test_file_003",
                file_path=temp_file_path,
                filename="empty.txt",
                mime_type="text/plain",
                file_metadata=mock_file_metadata
            )
            
            result = text_workflow.process(workflow_input)
            
            assert result.success is True
            assert result.extracted_content == ""
            assert result.structured_data["word_count"] == 0
            assert result.structured_data["char_count"] == 0
            assert len(result.embeddings) == 0
        finally:
            os.unlink(temp_file_path)


class TestTextWorkflowMethods:
    """Test individual TextWorkflow methods"""
    
    def test_extract_structured_data(self, text_workflow, sample_text_content):
        """Test structured data extraction"""
        structured_data = text_workflow._extract_structured_data(sample_text_content)
        
        assert isinstance(structured_data, dict)
        assert "word_count" in structured_data
        assert "char_count" in structured_data
        assert "line_count" in structured_data
        assert "keywords" in structured_data
        assert "summary" in structured_data
        
        # Verify data types and reasonable values
        assert isinstance(structured_data["word_count"], int)
        assert structured_data["word_count"] > 0
        assert isinstance(structured_data["char_count"], int)
        assert structured_data["char_count"] > 0
        assert isinstance(structured_data["line_count"], int)
        assert structured_data["line_count"] > 0
        assert isinstance(structured_data["keywords"], list)
        assert isinstance(structured_data["summary"], str)
    
    def test_extract_keywords(self, text_workflow):
        """Test keyword extraction"""
        test_content = "patient diagnosis treatment healthcare medical doctor hospital clinic"
        keywords = text_workflow._extract_keywords(test_content)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 10  # Should return top 10
        assert "patient" in keywords
        assert "diagnosis" in keywords
        assert "treatment" in keywords
        
        # Test with empty content
        empty_keywords = text_workflow._extract_keywords("")
        assert isinstance(empty_keywords, list)
        assert len(empty_keywords) == 0
    
    def test_extract_keywords_frequency_ordering(self, text_workflow):
        """Test keyword extraction ordering by frequency"""
        test_content = "test test test example example common common common common word"
        keywords = text_workflow._extract_keywords(test_content)
        
        assert isinstance(keywords, list)
        # "common" appears 4 times, should be first
        # "test" appears 3 times, should be second
        # "example" appears 2 times, should be third
        assert keywords[0] == "common"
        assert keywords[1] == "test"
        assert keywords[2] == "example"
    
    def test_generate_summary(self, text_workflow):
        """Test summary generation"""
        short_content = "Short content"
        short_summary = text_workflow._generate_summary(short_content)
        assert short_summary == short_content
        
        long_content = "a" * 300  # 300 characters
        long_summary = text_workflow._generate_summary(long_content)
        assert len(long_summary) == 203  # 200 + "..."
        assert long_summary.endswith("...")
        
        # Test with exactly 200 characters
        exact_content = "a" * 200
        exact_summary = text_workflow._generate_summary(exact_content)
        assert exact_summary == exact_content
    
    def test_generate_embeddings(self, text_workflow, sample_text_content):
        """Test embedding generation"""
        embeddings = text_workflow._generate_embeddings(sample_text_content)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) > 0
        
        # Check each embedding
        for embedding in embeddings:
            assert isinstance(embedding, list)
            assert len(embedding) == 384  # Standard embedding dimension
            assert all(isinstance(x, float) for x in embedding)
            assert all(0.0 <= x <= 1.0 for x in embedding)  # Values should be normalized
    
    def test_generate_embeddings_chunking(self, text_workflow):
        """Test embedding generation with different content sizes"""
        # Test short content (less than chunk size)
        short_content = "Short text content"
        short_embeddings = text_workflow._generate_embeddings(short_content)
        assert len(short_embeddings) == 1
        
        # Test long content (multiple chunks)
        long_content = "word " * 200  # Creates content longer than 500 characters
        long_embeddings = text_workflow._generate_embeddings(long_content)
        expected_chunks = len(long_content) // 500 + (1 if len(long_content) % 500 > 0 else 0)
        assert len(long_embeddings) == expected_chunks
        
        # Test empty content
        empty_embeddings = text_workflow._generate_embeddings("")
        assert len(empty_embeddings) == 0


class TestTextWorkflowEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_unicode_content(self, text_workflow, mock_file_metadata):
        """Test processing with unicode content"""
        unicode_content = "Unicode test: café, naïve, résumé, 中文, العربية, 🎉"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(unicode_content)
            temp_file_path = f.name
        
        try:
            workflow_input = WorkflowInput(
                file_id="test_unicode",
                file_path=temp_file_path,
                filename="unicode.txt",
                mime_type="text/plain",
                file_metadata=mock_file_metadata
            )
            
            result = text_workflow.process(workflow_input)
            
            assert result.success is True
            assert unicode_content in result.extracted_content
            assert result.structured_data["char_count"] > 0
        finally:
            os.unlink(temp_file_path)
    
    def test_large_content_processing(self, text_workflow, mock_file_metadata):
        """Test processing with large content"""
        large_content = "This is a test sentence. " * 1000  # ~25KB content
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(large_content)
            temp_file_path = f.name
        
        try:
            workflow_input = WorkflowInput(
                file_id="test_large",
                file_path=temp_file_path,
                filename="large.txt",
                mime_type="text/plain",
                file_metadata=mock_file_metadata
            )
            
            result = text_workflow.process(workflow_input)
            
            assert result.success is True
            assert len(result.extracted_content) > 20000
            assert len(result.embeddings) > 1  # Should create multiple chunks
            assert result.structured_data["word_count"] > 1000
        finally:
            os.unlink(temp_file_path)
    
    def test_special_characters_content(self, text_workflow):
        """Test content with special characters"""
        special_content = "Special chars: @#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`"
        
        structured_data = text_workflow._extract_structured_data(special_content)
        keywords = text_workflow._extract_keywords(special_content)
        summary = text_workflow._generate_summary(special_content)
        
        assert structured_data["char_count"] == len(special_content)
        assert isinstance(keywords, list)  # Should handle gracefully
        assert summary == special_content  # Short enough to not truncate


class TestWorkflowInputOutput:
    """Test WorkflowInput and WorkflowOutput structures"""
    
    def test_workflow_input_structure(self, mock_file_metadata):
        """Test WorkflowInput structure"""
        workflow_input = WorkflowInput(
            file_id="test_001",
            file_path="/path/to/file.txt",
            filename="file.txt",
            mime_type="text/plain",
            file_metadata=mock_file_metadata
        )
        
        assert workflow_input.file_id == "test_001"
        assert workflow_input.file_path == "/path/to/file.txt"
        assert workflow_input.filename == "file.txt"
        assert workflow_input.mime_type == "text/plain"
        assert workflow_input.file_metadata == mock_file_metadata
    
    def test_workflow_output_success_structure(self, text_workflow):
        """Test WorkflowOutput success structure"""
        output = text_workflow._create_success_output(
            file_id="test_001",
            content="Test content",
            structured_data={"key": "value"},
            embeddings=[[0.1, 0.2, 0.3]],
            processing_time=0.5
        )
        
        assert isinstance(output, WorkflowOutput)
        assert output.file_id == "test_001"
        assert output.success is True
        assert output.extracted_content == "Test content"
        assert output.structured_data == {"key": "value"}
        assert output.embeddings == [[0.1, 0.2, 0.3]]
        assert output.processing_time == 0.5
        assert output.error_message is None
    
    def test_workflow_output_error_structure(self, text_workflow):
        """Test WorkflowOutput error structure"""
        output = text_workflow._create_error_output(
            file_id="test_001",
            error_message="Test error",
            processing_time=0.1
        )
        
        assert isinstance(output, WorkflowOutput)
        assert output.file_id == "test_001"
        assert output.success is False
        assert output.extracted_content == ""
        assert output.structured_data == {}
        assert output.embeddings == []
        assert output.processing_time == 0.1
        assert output.error_message == "Test error"


if __name__ == "__main__":
    pytest.main([__file__]) 