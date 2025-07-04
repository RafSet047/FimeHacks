from typing import List, Dict, Any, Optional
from enum import Enum
import logging
from dataclasses import dataclass

# LangChain imports
try:
    from langchain.text_splitter import (
        RecursiveCharacterTextSplitter,
        CharacterTextSplitter,
        MarkdownHeaderTextSplitter,
        HTMLHeaderTextSplitter,
        Language,
        PythonCodeTextSplitter,
        LatexTextSplitter
    )
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available, using fallback text splitting")
    Document = None
    RecursiveCharacterTextSplitter = None
    CharacterTextSplitter = None

logger = logging.getLogger(__name__)

class ChunkingStrategy(str, Enum):
    """Supported text chunking strategies"""
    RECURSIVE = "recursive"
    CHARACTER = "character"
    MARKDOWN = "markdown"
    HTML = "html"
    CODE = "code"
    LATEX = "latex"

@dataclass
class ChunkingConfig:
    """Configuration for text chunking"""
    chunk_size: int = 500
    chunk_overlap: int = 50
    length_function: callable = len
    separators: List[str] = None
    keep_separator: bool = True
    strip_whitespace: bool = True
    add_start_index: bool = True
    
    # Markdown/HTML specific settings
    headers_to_split_on: List[Dict[str, str]] = None
    
    # Code specific settings
    language: str = "python"
    
    def __post_init__(self):
        if self.separators is None:
            self.separators = ["\n\n", "\n", ". ", " ", ""]
        if self.headers_to_split_on is None:
            # Format for MarkdownHeaderTextSplitter: list of tuples (markdown_header, header_name)
            self.headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3")
            ]

class TextChunker:
    """Text chunking service supporting multiple strategies"""
    
    def __init__(self):
        self._validate_dependencies()
        self.default_config = ChunkingConfig()
    
    def _validate_dependencies(self):
        """Validate required dependencies are available"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning(
                "LangChain not available. Only basic chunking will be supported. "
                "Install langchain for advanced features."
            )
    
    def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
        config: Optional[ChunkingConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Chunk text using specified strategy and configuration
        
        Args:
            text: Text to chunk
            strategy: Chunking strategy to use
            config: Chunking configuration
            metadata: Optional metadata to add to each chunk
            
        Returns:
            List of LangChain Document objects
        """
        if not text:
            return []
            
        config = config or self.default_config
        metadata = metadata or {}
        
        try:
            if not LANGCHAIN_AVAILABLE and strategy != ChunkingStrategy.CHARACTER:
                logger.warning(f"Strategy {strategy} not available, falling back to character chunking")
                strategy = ChunkingStrategy.CHARACTER
            
            splitter = self._get_text_splitter(strategy, config)
            logger.info(f"Successfully created text splitter for strategy: {strategy}")
            
            # Add start indices if requested
            if config.add_start_index:
                chunks_with_index = []
                chunks = splitter.split_text(text)
                
                current_index = 0
                for chunk in chunks:
                    # Handle both string chunks and Document chunks
                    if isinstance(chunk, Document):
                        chunk_text = chunk.page_content
                        chunk_metadata = {**metadata, **chunk.metadata}
                    else:
                        chunk_text = chunk
                        chunk_metadata = metadata.copy()
                    
                    # Find chunk start in original text
                    chunk_start = text.find(chunk_text, current_index)
                    if chunk_start != -1:
                        current_index = chunk_start + len(chunk_text)
                        chunk_metadata.update({
                            "start_index": chunk_start,
                            "end_index": current_index
                        })
                        chunks_with_index.append(
                            Document(page_content=chunk_text, metadata=chunk_metadata)
                        )
                    else:
                        # If we can't find the chunk in the text, add it without indices
                        chunks_with_index.append(
                            Document(page_content=chunk_text, metadata=chunk_metadata)
                        )
                return chunks_with_index
            
            # Regular chunking without indices
            return splitter.create_documents([text], metadatas=[metadata])
            
        except Exception as e:
            logger.error(f"Error chunking text with strategy {strategy}: {type(e).__name__}: {e}")
            logger.warning(f"Falling back to basic character chunking for strategy {strategy}")
            # Fallback to basic character chunking
            return self._basic_character_chunking(text, config, metadata)
    
    def _get_text_splitter(self, strategy: ChunkingStrategy, config: ChunkingConfig):
        """Get appropriate text splitter based on strategy"""
        if not LANGCHAIN_AVAILABLE:
            return self._get_basic_splitter(config)
            
        try:
            # Force RecursiveCharacterTextSplitter as default for all strategies except specialized ones
            if strategy == ChunkingStrategy.RECURSIVE or strategy == ChunkingStrategy.CHARACTER:
                return RecursiveCharacterTextSplitter(
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap,
                    length_function=config.length_function,
                    separators=config.separators,
                    keep_separator=config.keep_separator,
                    strip_whitespace=config.strip_whitespace
                )
                
            elif strategy == ChunkingStrategy.MARKDOWN:
                # For markdown, we need to chain with recursive splitter for proper chunking
                markdown_splitter = MarkdownHeaderTextSplitter(
                    headers_to_split_on=config.headers_to_split_on
                )
                # Chain with recursive splitter to ensure proper chunk sizes
                recursive_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap,
                    length_function=config.length_function,
                    separators=config.separators,
                    keep_separator=config.keep_separator,
                    strip_whitespace=config.strip_whitespace
                )
                # Return a custom splitter that handles markdown then recursive splitting
                return self._create_markdown_recursive_splitter(markdown_splitter, recursive_splitter)
                
            elif strategy == ChunkingStrategy.HTML:
                # HTMLHeaderTextSplitter expects format: [("h1", "Header 1"), ("h2", "Header 2")]
                html_headers = [
                    ("h1", "Header 1"),
                    ("h2", "Header 2"),
                    ("h3", "Header 3")
                ]
                return HTMLHeaderTextSplitter(
                    headers_to_split_on=html_headers
                )
                
            elif strategy == ChunkingStrategy.CODE:
                # Handle language parameter safely
                try:
                    language = Language(config.language)
                except (ValueError, AttributeError):
                    # Fall back to Python if language is not supported
                    language = Language.PYTHON
                
                return PythonCodeTextSplitter(
                    language=language,
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap,
                    length_function=config.length_function
                )
                
            elif strategy == ChunkingStrategy.LATEX:
                return LatexTextSplitter(
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap
                )
                
            else:
                logger.warning(f"Unknown strategy {strategy}, using recursive chunking")
                return self._get_text_splitter(ChunkingStrategy.RECURSIVE, config)
                
        except Exception as e:
            logger.error(f"Error creating text splitter for strategy {strategy}: {type(e).__name__}: {e}")
            logger.warning(f"Falling back to basic character splitter for strategy {strategy}")
            return self._get_basic_splitter(config)
    
    def _create_markdown_recursive_splitter(self, markdown_splitter, recursive_splitter):
        """Create a combined markdown-recursive splitter"""
        class MarkdownRecursiveSplitter:
            def __init__(self, md_splitter, rec_splitter):
                self.md_splitter = md_splitter
                self.rec_splitter = rec_splitter
            
            def split_text(self, text):
                try:
                    # First split by markdown headers
                    md_chunks = self.md_splitter.split_text(text)
                    
                    # If we get Document objects, extract text and further split if needed
                    final_chunks = []
                    for chunk in md_chunks:
                        if isinstance(chunk, Document):
                            chunk_text = chunk.page_content
                            chunk_metadata = chunk.metadata
                        else:
                            chunk_text = chunk
                            chunk_metadata = {}
                        
                        # Further split large chunks using recursive splitter
                        if len(chunk_text) > self.rec_splitter.chunk_size:
                            sub_chunks = self.rec_splitter.split_text(chunk_text)
                            for sub_chunk in sub_chunks:
                                if isinstance(sub_chunk, Document):
                                    merged_metadata = {**chunk_metadata, **sub_chunk.metadata}
                                    final_chunks.append(Document(page_content=sub_chunk.page_content, metadata=merged_metadata))
                                else:
                                    final_chunks.append(Document(page_content=sub_chunk, metadata=chunk_metadata))
                        else:
                            final_chunks.append(Document(page_content=chunk_text, metadata=chunk_metadata))
                    
                    return final_chunks
                except Exception as e:
                    logger.warning(f"Markdown splitting failed: {e}, falling back to recursive")
                    # Fall back to recursive splitting
                    return self.rec_splitter.split_text(text)
            
            def create_documents(self, texts, metadatas=None):
                """Create documents from texts"""
                if metadatas is None:
                    metadatas = [{}] * len(texts)
                
                all_chunks = []
                for text, metadata in zip(texts, metadatas):
                    chunks = self.split_text(text)
                    for chunk in chunks:
                        if isinstance(chunk, Document):
                            merged_metadata = {**metadata, **chunk.metadata}
                            all_chunks.append(Document(page_content=chunk.page_content, metadata=merged_metadata))
                        else:
                            all_chunks.append(Document(page_content=chunk, metadata=metadata))
                
                return all_chunks
        
        return MarkdownRecursiveSplitter(markdown_splitter, recursive_splitter)

    def _get_basic_splitter(self, config: ChunkingConfig):
        """Get basic character splitter when LangChain is not available"""
        return CharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=config.length_function,
            separator=config.separators[0] if config.separators else "\n\n"
        )
    
    def _basic_character_chunking(
        self,
        text: str,
        config: ChunkingConfig,
        metadata: Dict[str, Any]
    ) -> List[Document]:
        """Basic character-based chunking as fallback"""
        try:
            chunks = []
            start = 0
            text_length = len(text)
            
            while start < text_length:
                # Calculate chunk end
                chunk_end = min(start + config.chunk_size, text_length)
                
                # Extract chunk and strip whitespace
                chunk = text[start:chunk_end].strip()
                
                # Skip empty chunks
                if not chunk:
                    start = chunk_end
                    continue
                
                # Add chunk as Document with proper metadata
                chunk_metadata = {
                    **metadata,
                    "start_index": start,
                    "end_index": chunk_end
                }
                chunks.append(Document(page_content=chunk, metadata=chunk_metadata))
                
                # Move start position for next chunk, considering overlap
                if config.chunk_overlap > 0 and chunk_end < text_length:
                    start = max(chunk_end - config.chunk_overlap, start + 1)
                else:
                    start = chunk_end
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error in basic character chunking: {e}")
            # Return single chunk as last resort
            return [Document(page_content=text.strip(), metadata=metadata)]

    def merge_chunks(
        self,
        chunks: List[Document],
        max_chunk_size: Optional[int] = None
    ) -> List[Document]:
        """
        Merge small chunks to optimize chunk sizes
        
        Args:
            chunks: List of Document chunks to merge
            max_chunk_size: Maximum size for merged chunks
            
        Returns:
            List of merged Document chunks
        """
        if not chunks:
            return []
            
        try:
            merged_chunks = []
            current_chunk = chunks[0].page_content
            current_metadata = chunks[0].metadata.copy()
            
            for chunk in chunks[1:]:
                # Check if merging would exceed max size
                if max_chunk_size and len(current_chunk) + len(chunk.page_content) > max_chunk_size:
                    # Save current chunk and start new one
                    merged_chunks.append(Document(
                        page_content=current_chunk,
                        metadata=current_metadata
                    ))
                    current_chunk = chunk.page_content
                    current_metadata = chunk.metadata.copy()
                else:
                    # Merge chunks
                    current_chunk += "\n" + chunk.page_content
                    # Update metadata
                    if "end_index" in chunk.metadata:
                        current_metadata["end_index"] = chunk.metadata["end_index"]
            
            # Add final chunk
            merged_chunks.append(Document(
                page_content=current_chunk,
                metadata=current_metadata
            ))
            
            return merged_chunks
            
        except Exception as e:
            logger.error(f"Error merging chunks: {e}")
            return chunks 