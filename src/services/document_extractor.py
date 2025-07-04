import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from abc import ABC, abstractmethod

# Document processing imports
try:
    from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("langchain not available, using fallback document processing")

# Fallback imports
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from docx import Document
    PYTHON_DOCX_AVAILABLE = True
except ImportError:
    PYTHON_DOCX_AVAILABLE = False

from src.config.settings import settings

logger = logging.getLogger(__name__)


class DocumentExtractor(ABC):
    """Abstract base class for document extractors"""
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass
    
    @abstractmethod
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        pass


class PDFExtractor(DocumentExtractor):
    """Extract text from PDF files"""
    
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        return (
            mime_type == "application/pdf" or 
            file_path.lower().endswith('.pdf')
        )
    
    def extract_text(self, file_path: str) -> str:
        if LANGCHAIN_AVAILABLE:
            return self._extract_with_langchain(file_path)
        elif PYPDF2_AVAILABLE:
            return self._extract_with_pypdf2(file_path)
        else:
            raise RuntimeError("No PDF processing library available")
    
    def _extract_with_langchain(self, file_path: str) -> str:
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        except Exception as e:
            logger.error(f"Langchain PDF extraction failed: {e}")
            if PYPDF2_AVAILABLE:
                return self._extract_with_pypdf2(file_path)
            raise
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            raise


class DOCXExtractor(DocumentExtractor):
    """Extract text from DOCX files"""
    
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        return (
            mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or
            file_path.lower().endswith('.docx')
        )
    
    def extract_text(self, file_path: str) -> str:
        if LANGCHAIN_AVAILABLE:
            return self._extract_with_langchain(file_path)
        elif PYTHON_DOCX_AVAILABLE:
            return self._extract_with_python_docx(file_path)
        else:
            raise RuntimeError("No DOCX processing library available")
    
    def _extract_with_langchain(self, file_path: str) -> str:
        try:
            loader = UnstructuredWordDocumentLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        except Exception as e:
            logger.error(f"Langchain DOCX extraction failed: {e}")
            if PYTHON_DOCX_AVAILABLE:
                return self._extract_with_python_docx(file_path)
            raise
    
    def _extract_with_python_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"python-docx extraction failed: {e}")
            raise


class DOCExtractor(DocumentExtractor):
    """Extract text from DOC files"""
    
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        return (
            mime_type == "application/msword" or
            file_path.lower().endswith('.doc')
        )
    
    def extract_text(self, file_path: str) -> str:
        if LANGCHAIN_AVAILABLE:
            return self._extract_with_langchain(file_path)
        else:
            raise RuntimeError("DOC file processing requires langchain with unstructured")
    
    def _extract_with_langchain(self, file_path: str) -> str:
        try:
            loader = UnstructuredWordDocumentLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        except Exception as e:
            logger.error(f"Langchain DOC extraction failed: {e}")
            raise


class PlainTextExtractor(DocumentExtractor):
    """Extract text from plain text files"""
    
    def can_handle(self, file_path: str, mime_type: str) -> bool:
        return (
            mime_type.startswith("text/") or
            file_path.lower().endswith(('.txt', '.md', '.html', '.json', '.csv'))
        )
    
    def extract_text(self, file_path: str) -> str:
        encodings = ['utf-8', 'latin-1', 'ascii', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if encoding == encodings[-1]:  # Last encoding to try
                    logger.error(f"Plain text extraction failed: {e}")
                    raise
                continue
        
        # If all encodings fail, raise error
        raise RuntimeError("Failed to read file with any supported encoding")


class DocumentTextExtractor:
    """Main document text extraction service"""
    
    def __init__(self):
        self.extractors = [
            PDFExtractor(),
            DOCXExtractor(),
            DOCExtractor(),
            PlainTextExtractor()
        ]
        
        # Initialize text splitter for chunking
        if LANGCHAIN_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.text_chunk_size,
                chunk_overlap=settings.text_chunk_overlap,
                length_function=len
            )
        else:
            self.text_splitter = None
    
    def extract_text(self, file_path: str, mime_type: str) -> str:
        """Extract text from any supported document format"""
        try:
            # Find appropriate extractor
            for extractor in self.extractors:
                if extractor.can_handle(file_path, mime_type):
                    text = extractor.extract_text(file_path)
                    logger.info(f"Extracted {len(text)} characters from {file_path}")
                    return text
            
            # If no extractor found, raise error
            raise ValueError(f"No extractor available for file type: {mime_type}")
            
        except Exception as e:
            logger.error(f"Document text extraction failed for {file_path}: {e}")
            raise
    
    def extract_and_chunk_text(self, file_path: str, mime_type: str) -> Dict[str, Any]:
        """Extract text and split into chunks for processing"""
        try:
            # Extract full text
            full_text = self.extract_text(file_path, mime_type)
            
            # Split into chunks if langchain is available
            if self.text_splitter:
                chunks = self.text_splitter.split_text(full_text)
            else:
                # Fallback chunking
                chunk_size = settings.text_chunk_size
                chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
            
            return {
                "full_text": full_text,
                "chunks": chunks,
                "chunk_count": len(chunks),
                "total_characters": len(full_text),
                "extraction_method": "langchain" if LANGCHAIN_AVAILABLE else "fallback"
            }
            
        except Exception as e:
            logger.error(f"Document chunking failed for {file_path}: {e}")
            raise
    
    def get_document_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic document metadata"""
        try:
            file_stat = os.stat(file_path)
            return {
                "file_size": file_stat.st_size,
                "file_extension": Path(file_path).suffix.lower(),
                "file_name": Path(file_path).name,
                "creation_time": file_stat.st_ctime,
                "modification_time": file_stat.st_mtime
            }
        except Exception as e:
            logger.error(f"Failed to get document metadata for {file_path}: {e}")
            return {}


# Global instance
document_extractor = DocumentTextExtractor() 