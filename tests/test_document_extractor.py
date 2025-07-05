import pytest
import os
import tempfile
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.document_extractor import (
    DocumentTextExtractor, 
    PDFExtractor, 
    DOCXExtractor, 
    DOCExtractor, 
    PlainTextExtractor,
    document_extractor
)


class TestPDFExtractor:
    """Test PDF text extraction functionality"""
    
    def test_can_handle_pdf_mime_type(self):
        extractor = PDFExtractor()
        assert extractor.can_handle("test.pdf", "application/pdf")
        assert extractor.can_handle("document.PDF", "application/pdf")
        assert not extractor.can_handle("test.txt", "text/plain")
    
    def test_can_handle_pdf_extension(self):
        extractor = PDFExtractor()
        assert extractor.can_handle("test.pdf", "unknown/type")
        assert extractor.can_handle("TEST.PDF", "unknown/type")
        assert not extractor.can_handle("test.docx", "unknown/type")
    
    @patch('src.services.document_extractor.LANGCHAIN_AVAILABLE', True)
    @patch('src.services.document_extractor.PyPDFLoader')
    def test_extract_with_langchain(self, mock_loader):
        """Test PDF extraction using langchain"""
        # Mock langchain loader
        mock_doc1 = Mock()
        mock_doc1.page_content = "Page 1 content"
        mock_doc2 = Mock()
        mock_doc2.page_content = "Page 2 content"
        
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc1, mock_doc2]
        mock_loader.return_value = mock_loader_instance
        
        extractor = PDFExtractor()
        result = extractor.extract_text("test.pdf")
        
        assert result == "Page 1 content\n\nPage 2 content"
        mock_loader.assert_called_once_with("test.pdf")
    
    @patch('src.services.document_extractor.LANGCHAIN_AVAILABLE', False)
    @patch('src.services.document_extractor.PYPDF2_AVAILABLE', True)
    @patch('src.services.document_extractor.PyPDF2')
    def test_extract_with_pypdf2(self, mock_pypdf2):
        """Test PDF extraction using PyPDF2 fallback"""
        # Mock PyPDF2 reader
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 text"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        extractor = PDFExtractor()
        
        with patch('builtins.open', mock_open(read_data=b"fake pdf data")):
            result = extractor.extract_text("test.pdf")
        
        assert result == "Page 1 text\nPage 2 text"
    
    @patch('src.services.document_extractor.LANGCHAIN_AVAILABLE', False)
    @patch('src.services.document_extractor.PYPDF2_AVAILABLE', False)
    def test_extract_no_libraries_available(self):
        """Test error when no PDF libraries are available"""
        extractor = PDFExtractor()
        
        with pytest.raises(RuntimeError, match="No PDF processing library available"):
            extractor.extract_text("test.pdf")


class TestDOCXExtractor:
    """Test DOCX text extraction functionality"""
    
    def test_can_handle_docx_mime_type(self):
        extractor = DOCXExtractor()
        assert extractor.can_handle("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        assert not extractor.can_handle("test.pdf", "application/pdf")
    
    def test_can_handle_docx_extension(self):
        extractor = DOCXExtractor()
        assert extractor.can_handle("test.docx", "unknown/type")
        assert extractor.can_handle("TEST.DOCX", "unknown/type")
        assert not extractor.can_handle("test.doc", "unknown/type")
    
    @patch('src.services.document_extractor.LANGCHAIN_AVAILABLE', True)
    @patch('src.services.document_extractor.UnstructuredWordDocumentLoader')
    def test_extract_with_langchain(self, mock_loader):
        """Test DOCX extraction using langchain"""
        mock_doc = Mock()
        mock_doc.page_content = "Document content from langchain"
        
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        extractor = DOCXExtractor()
        result = extractor.extract_text("test.docx")
        
        assert result == "Document content from langchain"
        mock_loader.assert_called_once_with("test.docx")
    
    @patch('src.services.document_extractor.LANGCHAIN_AVAILABLE', False)
    @patch('src.services.document_extractor.PYTHON_DOCX_AVAILABLE', True)
    @patch('src.services.document_extractor.Document')
    def test_extract_with_python_docx(self, mock_document):
        """Test DOCX extraction using python-docx fallback"""
        # Mock document paragraphs
        mock_paragraph1 = Mock()
        mock_paragraph1.text = "Paragraph 1"
        mock_paragraph2 = Mock()
        mock_paragraph2.text = "Paragraph 2"
        
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_document.return_value = mock_doc
        
        extractor = DOCXExtractor()
        result = extractor.extract_text("test.docx")
        
        assert result == "Paragraph 1\nParagraph 2"
        mock_document.assert_called_once_with("test.docx")


class TestPlainTextExtractor:
    """Test plain text extraction functionality"""
    
    def test_can_handle_text_mime_types(self):
        extractor = PlainTextExtractor()
        assert extractor.can_handle("test.txt", "text/plain")
        assert extractor.can_handle("test.md", "text/markdown")
        assert extractor.can_handle("test.html", "text/html")
        assert not extractor.can_handle("test.pdf", "application/pdf")
    
    def test_can_handle_text_extensions(self):
        extractor = PlainTextExtractor()
        assert extractor.can_handle("test.txt", "unknown/type")
        assert extractor.can_handle("test.md", "unknown/type")
        assert extractor.can_handle("test.html", "unknown/type")
        assert extractor.can_handle("test.json", "unknown/type")
        assert extractor.can_handle("test.csv", "unknown/type")
        assert not extractor.can_handle("test.pdf", "unknown/type")
    
    def test_extract_text_success(self):
        """Test successful text extraction"""
        extractor = PlainTextExtractor()
        test_content = "This is test content\nWith multiple lines"
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = extractor.extract_text("test.txt")
        
        assert result == test_content
    
    def test_extract_text_encoding_error(self):
        """Test text extraction with encoding handling"""
        extractor = PlainTextExtractor()
        
        # Mock file that raises UnicodeDecodeError first, then succeeds
        mock_file = mock_open(read_data="test content")
        mock_file.return_value.read.side_effect = [
            UnicodeDecodeError('utf-8', b'', 0, 1, 'test'),
            "test content"
        ]
        
        with patch('builtins.open', mock_file):
            # Should handle encoding errors gracefully
            result = extractor.extract_text("test.txt")
        
        # The function uses errors='ignore', so it should still return content
        assert result == "test content"


class TestDocumentTextExtractor:
    """Test main document text extraction service"""
    
    def test_initialization(self):
        """Test extractor initialization"""
        extractor = DocumentTextExtractor()
        assert len(extractor.extractors) == 4
        assert isinstance(extractor.extractors[0], PDFExtractor)
        assert isinstance(extractor.extractors[1], DOCXExtractor)
        assert isinstance(extractor.extractors[2], DOCExtractor)
        assert isinstance(extractor.extractors[3], PlainTextExtractor)
    
    def test_extract_text_pdf(self):
        """Test text extraction routing for PDF"""
        extractor = DocumentTextExtractor()
        
        with patch.object(extractor.extractors[0], 'extract_text', return_value="PDF content") as mock_extract:
            result = extractor.extract_text("test.pdf", "application/pdf")
        
        assert result == "PDF content"
        mock_extract.assert_called_once_with("test.pdf")
    
    def test_extract_text_docx(self):
        """Test text extraction routing for DOCX"""
        extractor = DocumentTextExtractor()
        
        with patch.object(extractor.extractors[1], 'extract_text', return_value="DOCX content") as mock_extract:
            result = extractor.extract_text("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        assert result == "DOCX content"
        mock_extract.assert_called_once_with("test.docx")
    
    def test_extract_text_plain_text(self):
        """Test text extraction routing for plain text"""
        extractor = DocumentTextExtractor()
        
        with patch.object(extractor.extractors[3], 'extract_text', return_value="Plain text content") as mock_extract:
            result = extractor.extract_text("test.txt", "text/plain")
        
        assert result == "Plain text content"
        mock_extract.assert_called_once_with("test.txt")
    
    def test_extract_text_unsupported_type(self):
        """Test extraction with unsupported file type"""
        extractor = DocumentTextExtractor()
        
        with pytest.raises(ValueError, match="No extractor available for file type"):
            extractor.extract_text("test.xyz", "unknown/type")
    
    @patch('src.services.document_extractor.LANGCHAIN_AVAILABLE', True)
    def test_extract_and_chunk_text_with_langchain(self):
        """Test text extraction and chunking with langchain"""
        extractor = DocumentTextExtractor()
        
        # Mock text splitter
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = ["chunk1", "chunk2", "chunk3"]
        extractor.text_splitter = mock_splitter
        
        with patch.object(extractor, 'extract_text', return_value="Full document text"):
            result = extractor.extract_and_chunk_text("test.txt", "text/plain")
        
        assert result["full_text"] == "Full document text"
        assert result["chunks"] == ["chunk1", "chunk2", "chunk3"]
        assert result["chunk_count"] == 3
        assert result["total_characters"] == 18
        assert result["extraction_method"] == "langchain"
    
    @patch('src.services.document_extractor.LANGCHAIN_AVAILABLE', False)
    @patch('src.services.document_extractor.settings')
    def test_extract_and_chunk_text_fallback(self, mock_settings):
        """Test text extraction and chunking with fallback method"""
        mock_settings.text_chunk_size = 5
        
        extractor = DocumentTextExtractor()
        extractor.text_splitter = None
        
        with patch.object(extractor, 'extract_text', return_value="0123456789"):
            result = extractor.extract_and_chunk_text("test.txt", "text/plain")
        
        assert result["full_text"] == "0123456789"
        assert result["chunks"] == ["01234", "56789"]
        assert result["chunk_count"] == 2
        assert result["total_characters"] == 10
        assert result["extraction_method"] == "fallback"
    
    @patch('os.stat')
    def test_get_document_metadata(self, mock_stat):
        """Test document metadata extraction"""
        # Mock file stats
        mock_stat.return_value.st_size = 1024
        mock_stat.return_value.st_ctime = 1234567890
        mock_stat.return_value.st_mtime = 1234567895
        
        extractor = DocumentTextExtractor()
        result = extractor.get_document_metadata("/path/to/test.pdf")
        
        assert result["file_size"] == 1024
        assert result["file_extension"] == ".pdf"
        assert result["file_name"] == "test.pdf"
        assert result["creation_time"] == 1234567890
        assert result["modification_time"] == 1234567895
    
    @patch('os.stat')
    def test_get_document_metadata_error(self, mock_stat):
        """Test document metadata extraction with error"""
        mock_stat.side_effect = OSError("File not found")
        
        extractor = DocumentTextExtractor()
        result = extractor.get_document_metadata("/path/to/nonexistent.pdf")
        
        assert result == {}


class TestGlobalInstance:
    """Test the global document extractor instance"""
    
    def test_global_instance_exists(self):
        """Test that global instance is available"""
        assert document_extractor is not None
        assert isinstance(document_extractor, DocumentTextExtractor)
    
    def test_global_instance_functionality(self):
        """Test that global instance works correctly"""
        with patch.object(document_extractor, 'extract_text', return_value="Global test content"):
            result = document_extractor.extract_text("test.txt", "text/plain")
        
        assert result == "Global test content"


class TestIntegrationScenarios:
    """Integration tests for various document processing scenarios"""
    
    def test_healthcare_document_processing(self):
        """Test processing of healthcare documents"""
        extractor = DocumentTextExtractor()
        
        # Mock PDF extraction for medical protocol
        with patch.object(extractor.extractors[0], 'extract_text', return_value="MEDICAL PROTOCOL\n\nPatient care guidelines..."):
            result = extractor.extract_text("protocol.pdf", "application/pdf")
        
        assert "MEDICAL PROTOCOL" in result
        assert "Patient care guidelines" in result
    
    def test_university_document_processing(self):
        """Test processing of university documents"""
        extractor = DocumentTextExtractor()
        
        # Mock DOCX extraction for academic syllabus
        with patch.object(extractor.extractors[1], 'extract_text', return_value="COURSE SYLLABUS\n\nCS 101 - Introduction to Programming"):
            result = extractor.extract_text("syllabus.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        assert "COURSE SYLLABUS" in result
        assert "CS 101" in result
    
    def test_mixed_format_batch_processing(self):
        """Test processing multiple document formats"""
        extractor = DocumentTextExtractor()
        
        test_files = [
            ("doc1.pdf", "application/pdf", "PDF content"),
            ("doc2.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "DOCX content"),
            ("doc3.txt", "text/plain", "Plain text content")
        ]
        
        results = []
        for filename, mime_type, expected_content in test_files:
            # Find the appropriate extractor and mock it
            for extractor_obj in extractor.extractors:
                if extractor_obj.can_handle(filename, mime_type):
                    with patch.object(extractor_obj, 'extract_text', return_value=expected_content):
                        result = extractor.extract_text(filename, mime_type)
                        results.append(result)
                    break
        
        assert len(results) == 3
        assert "PDF content" in results
        assert "DOCX content" in results
        assert "Plain text content" in results


if __name__ == "__main__":
    pytest.main([__file__]) 