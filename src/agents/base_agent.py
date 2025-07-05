from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging
import os
from langchain.schema import BaseMessage
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
#from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

from src.database.milvus_db import MilvusVectorDatabase
from src.database.config import CollectionConfig
from src.services.file_processor import ProcessingJob
from src.config.settings import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    Provides common functionality and interfaces.
    """
    
    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            description: Agent description
            config: Configuration dictionary
        """
        # add access to MilvusVectorDatabase
        self.milvus_db_manager = MilvusVectorDatabase()
        self.milvus_db_manager.connect()

        #TODO: Update configuration
        # Use the default documents collection configuration
        from src.database.config import get_default_collections_config
        collections_config = get_default_collections_config()
        self.milvus_db_manager.create_collection("documents")


        self.name = name
        self.description = description
        self.config = config or {}
        self.is_active = True
        self.error_count = 0
        self.max_errors = self.config.get('max_errors', 5)
        
#    @abstractmethod
#    def process(self, input_data: Any) -> Any:
#        """
#        Process input data and return output
#        Must be implemented by subclasses
#        """
#        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data
        Can be overridden by subclasses
        """
        return input_data is not None
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle errors and update error count
        """
        self.error_count += 1
        logger.error(f"Agent {self.name} error ({self.error_count}/{self.max_errors}): {error} - {context}")
        
        if self.error_count >= self.max_errors:
            self.is_active = False
            logger.warning(f"Agent {self.name} deactivated due to too many errors")
    
    def reset_errors(self) -> None:
        """
        Reset error count and reactivate agent
        """
        self.error_count = 0
        self.is_active = True
        logger.info(f"Agent {self.name} error count reset and reactivated")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status information
        """
        return {
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "error_count": self.error_count,
            "max_errors": self.max_errors
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update agent configuration
        """
        self.config.update(new_config)
        logger.info(f"Agent {self.name} configuration updated")
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', active={self.is_active})"
   
    def __repr__(self) -> str:
        return self.__str__() 

    def _initialize_llm(self) -> genai.GenerativeModel:
        """Initialize LLM with Google Gemini"""
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel(settings.llm_model)

        return model