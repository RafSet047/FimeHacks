from typing import Dict, List, Optional, Any, Union
import logging
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import hashlib
import time

from src.agents.base_agent import BaseAgent
from src.database.milvus_db import MilvusVectorDatabase

#TODO: Add logger
#logger = logging.getLogger(__name__)

#TODO: Remove embedding generation from here 

class StoreAgent(BaseAgent):
    """
    Store Agent: Receives raw data, processes it, generates embeddings, and stores in Milvus
    """
    
    def __init__(self, 
                 name: str = "StoreAgent",
                 description: str = "Processes raw data and stores embeddings in Milvus",
                 config: Optional[Dict[str, Any]] = None,
                 db: Optional[MilvusVectorDatabase] = None):
        """
        Initialize Store Agent
        
        Args:
            name: Agent name
            description: Agent description
            config: Configuration dictionary
        """
        super().__init__(name, description, config)
        
        # Initialize components
        #self.embeddings_model = self._initialize_embeddings()
        #self.text_splitter = self._initialize_text_splitter()
        self.db = db #if db is not None else self._initialize_database()
        self.llm = self._initialize_lmm()
        
        # Default configuration
        self.default_config = {
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'collection_name': 'documents',
            'embedding_model': 'text-embedding-ada-002',
            'max_errors': 5
        }
        
        # Update with provided config
        self.config = {**self.default_config, **self.config}
    
    def classify_and_store_query(self, query: str) -> str:
        tags = self.analyze_content(query)

        splitted_text = self.split_text(query)
        embeddings = self.embed_text(splitted_text)

        self.store_embeddings(tags, embeddings)

        return embeddings
    
    def store_embeddings(self, tags: List[str], embeddings: List[List[float]]) -> List[str]:
        self.db.store_embeddings(tags, embeddings)

    def get_analyze_prompt(self, content: str, db_structure: Dict[str, Any]) -> str:
        #TODO: Specify response format
        return """
        You are a helpful assistant that analyzes content and returns tags.
        You are given a content and a database structure.
        You need to analyze the content and return tags.

        Tags are a list of strings that describe the content.

        Content:
        {content}

        Database structure:
        {db_structure}
        """
    
    def analyze_content(self, input_data: str) -> Dict[str, Any]:
        db_structure = self.db.get_db_structure()
        analyze_prompt = self.get_analyze_prompt(input_data, db_structure)
        response = self.llm.invoke(analyze_prompt)
        return response.content
        
        
        
        
#    def _initialize_embeddings(self) -> OpenAIEmbeddings:
#        """Initialize embedding model"""
#        try:
#            return OpenAIEmbeddings(
#                model=self.config.get('embedding_model', 'text-embedding-ada-002')
#            )
#        except Exception as e:
#            logger.error(f"Failed to initialize embeddings: {e}")
#            raise
#    
#    def _initialize_text_splitter(self) -> RecursiveCharacterTextSplitter:
#        """Initialize text splitter"""
#        return RecursiveCharacterTextSplitter(
#            chunk_size=self.config.get('chunk_size', 1000),
#            chunk_overlap=self.config.get('chunk_overlap', 200),
#            length_function=len,
#            separators=["\n\n", "\n", " ", ""]
#        )
#    
#    #TODO: Do this in base class?
#
#    def _initialize_database(self) -> MilvusVectorDatabase:
#        """Initialize Milvus database connection"""
#        try:
#            db = MilvusVectorDatabase()
#            if not db.connect():
#                raise Exception("Failed to connect to Milvus")
#            return db
#        except Exception as e:
#            logger.error(f"Failed to initialize database: {e}")
#            raise
#    
#    def validate_input(self, input_data: Union[str, Dict[str, Any]]) -> bool:
#        """
#        Validate input data
#        
#        Args:
#            input_data: Raw data (string or dict with 'content' key)
#        """
#        if isinstance(input_data, str):
#            return len(input_data.strip()) > 0
#        elif isinstance(input_data, dict):
#            return 'content' in input_data and len(str(input_data['content']).strip()) > 0
#        return False
#    
#    def process(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
#        """
#        Process raw data: split, embed, and store in Milvus
#        
#        Args:
#            input_data: Raw data (string or dict with metadata)
#            
#        Returns:
#            Dict with processing results
#        """
#        try:
#            if not self.is_active:
#                raise Exception("Agent is not active")
#            
#            if not self.validate_input(input_data):
#                raise ValueError("Invalid input data")
#            
#            # Extract content and metadata
#            if isinstance(input_data, str):
#                content = input_data
#                metadata = {}
#            else:
#                content = input_data['content']
#                metadata = {k: v for k, v in input_data.items() if k != 'content'}
#            
#            # Split text into chunks
#            documents = self.text_splitter.split_text(content)
#            logger.info(f"Split content into {len(documents)} chunks")
#            
#            # Generate embeddings and store
#            stored_ids = []
#            for i, doc_text in enumerate(documents):
#                try:
#                    # Generate embedding
#                    embedding = self.embeddings_model.embed_query(doc_text)
#                    
#                    # Create document metadata
#                    doc_metadata = {
#                        'chunk_index': i,
#                        'total_chunks': len(documents),
#                        'content': doc_text,
#                        'content_type': metadata.get('content_type', 'text'),
#                        'department': metadata.get('department', 'general'),
#                        'role': metadata.get('role', 'all'),
#                        'organization_type': metadata.get('organization_type', 'general'),
#                        'security_level': metadata.get('security_level', 'public'),
#                        **metadata
#                    }
#                    
#                    # Calculate content hash
#                    content_hash = hashlib.sha256(doc_text.encode()).hexdigest()
#                    
#                    # Store in Milvus
#                    doc_id = self.db.insert_document(
#                        collection_name=self.config['collection_name'],
#                        vector=embedding,
#                        metadata=doc_metadata,
#                        file_size=len(doc_text.encode()),
#                        content_hash=content_hash
#                    )
#                    
#                    if doc_id:
#                        stored_ids.append(doc_id)
#                        logger.debug(f"Stored chunk {i+1}/{len(documents)} with ID: {doc_id}")
#                    
#                except Exception as e:
#                    logger.error(f"Failed to process chunk {i}: {e}")
#                    self.handle_error(e, f"chunk_processing_{i}")
#            
#            return {
#                'success': True,
#                'total_chunks': len(documents),
#                'stored_chunks': len(stored_ids),
#                'stored_ids': stored_ids,
#                'collection_name': self.config['collection_name']
#            }
#            
#        except Exception as e:
#            self.handle_error(e, "process_input")
#            return {
#                'success': False,
#                'error': str(e),
#                'total_chunks': 0,
#                'stored_chunks': 0,
#                'stored_ids': []
#            }
#    
#    def get_processing_stats(self) -> Dict[str, Any]:
#        """Get processing statistics"""
#        try:
#            stats = self.db.get_stats(self.config['collection_name'])
#            return {
#                'collection_name': self.config['collection_name'],
#                'total_documents': stats.get('total_documents', 0),
#                'collection_size': stats.get('collection_size', 0),
#                'agent_status': self.get_status()
#            }
#        except Exception as e:
#            logger.error(f"Failed to get stats: {e}")
#            return {'error': str(e)}
#    
#    def cleanup(self):
#        """Cleanup resources"""
#        try:
#            if hasattr(self, 'db'):
#                self.db.disconnect()
#        except Exception as e:
#            logger.error(f"Error during cleanup: {e}") 