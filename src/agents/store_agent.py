from typing import Dict, List, Optional, Any, Union
import logging
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import hashlib
import time
import random

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
                 postgres_db,
                 milvus_db,
                 name: str = "StoreAgent",
                 description: str = "Processes raw data and stores embeddings in Milvus",
                 config: Optional[Dict[str, Any]] = None):
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
        self.postgres_db = postgres_db #if db is not None else self._initialize_database()
        self.milvus_db = milvus_db
        self.llm = self._initialize_llm()
        
        # Default configuration
        self.default_config = {
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'collection_name': 'documents',
            'embedding_model': 'text-embedding-ada-002',
            'max_errors': 5,
            'vector_dim': 3072
        }
        
        # Update with provided config
        self.config = {**self.default_config, **self.config}
    
    def _generate_dummy_embedding(self, dimension: int = 1536) -> List[float]:
        """Generate dummy embedding vector for testing purposes"""
        return [random.uniform(-1.0, 1.0) for _ in range(dimension)]
    
    def classify_and_store_query(self, query: str, collection_name: str = "documents") -> Dict[str, Any]:
        """
        Classify query content and store it in Milvus with tags
        
        Args:
            query: Raw text content to analyze and store
            collection_name: Milvus collection name
            
        Returns:
            Dictionary with storage results
        """
        try:
            print(f"Query: {query}")
            
            # Analyze content to get tags
            tags = self.analyze_content(query)
            print(f"Tags: {tags}")
            
            # Generate dummy embedding
            dummy_embedding = self._generate_dummy_embedding(self.config['vector_dim'])
            
            # Create metadata with tags and raw text
            metadata = {
                "content": query,
                "tags": tags if isinstance(tags, list) else [tags],
                "processed_at": time.time(),
                "agent_name": self.name,
                "organizational": {
                    "role": "user",
                    "organization_type": "university",
                    "security_level": "internal"
                }
            }
            
            # Calculate content hash
            content_hash = hashlib.sha256(query.encode()).hexdigest()
            
            # Store in Milvus (insert_data will handle collection creation/dimension checking)
            doc_id = self.milvus_db.insert_data(
                collection_name=collection_name,
                vector=dummy_embedding,
                metadata=metadata,
                content_type="text",
                department="general",
                file_size=len(query.encode()),
                content_hash=content_hash
            )
            
            if doc_id:
                print(f"Successfully stored document with ID: {doc_id}")
                return {
                    'success': True,
                    'document_id': doc_id,
                    'tags': tags,
                    'content_length': len(query),
                    'collection_name': collection_name,
                    'embedding_dim': len(dummy_embedding)
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to store document in Milvus',
                    'tags': tags
                }
                
        except Exception as e:
            print(f"Error in classify_and_store_query: {e}")
            return {
                'success': False,
                'error': str(e),
                'tags': None
            }
    
    def get_analyze_prompt(self, content: str, milvus_tags: List[str]) -> str:
        """Generate prompt for content analysis"""
        return f"""
        You are a document classifier. Use the provided tags to classify the document. 
        Each document can have multiple tags.

        Input:
            Tags: {milvus_tags}    # allowed labels
            Text: {content}
            Instructions

        Read Text and select every tag from Tags that truly describes Text.
        Output the chosen tags, one per line.
        """
    
    def analyze_content(self, input_data: str) -> List[str]:
        """
        Analyze content and return applicable tags
        
        Args:
            input_data: Raw text to analyze
            
        Returns:
            List of applicable tags
        """
        try:
            milvus_tags = self.milvus_db.get_possible_tags()
            print(f"Milvus tags: {milvus_tags}")
            
            analyze_prompt = self.get_analyze_prompt(input_data, milvus_tags)
            response = self.llm.generate_content(analyze_prompt)
            
            # Parse response to extract tags
            if hasattr(response, 'text'):
                tags_text = response.text
            else:
                tags_text = str(response)
                
            # Split by lines and clean up
            tags = [tag.strip() for tag in tags_text.split('\n') if tag.strip()]
            
            # Filter to only include valid tags
            valid_tags = [tag for tag in tags if tag in milvus_tags]
            
            # If no valid tags found, return a default tag
            if not valid_tags:
                valid_tags = ['general']
                
            return valid_tags
            
        except Exception as e:
            print(f"Error in analyze_content: {e}")
            return ['general']  # Default tag if analysis fails