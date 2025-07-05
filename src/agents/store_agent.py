from typing import Dict, List, Optional, Any
import logging
import time
import json
import os

from src.agents.base_agent import BaseAgent

from src.utils.logging import setup_logging
logger = setup_logging()

class StoreAgent(BaseAgent):
    """
    Store Agent: Analyzes content and generates tags using LLM
    """
    
    def __init__(self, 
                 name: str = "StoreAgent",
                 description: str = "Analyzes content and generates applicable tags",
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize Store Agent
        
        Args:
            name: Agent name
            description: Agent description
            config: Configuration dictionary
        """
        super().__init__(name, description, config)
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Load available tags
        self.available_tags = self._load_available_tags()
        
        # Default configuration for LLM processing
        self.default_config = {
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'max_errors': 5,
        }
        
        # Update with provided config
        self.config = {**self.default_config, **self.config}
    
    def _load_available_tags(self) -> List[str]:
        """Load available tags from static source"""
        # Try to load from config file first
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config',
                'available_tags.json'
            )
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data.get('tags', self._get_default_tags())
        except Exception as e:
            logger.warning(f"Failed to load tags from config: {e}")
        
        # Fallback to default tags
        return self._get_default_tags()
    
    def _get_default_tags(self) -> List[str]:
        """Get default tags for university/healthcare context"""
        return [
            'academic', 'research', 'administrative', 'student-records',
            'faculty-info', 'curriculum', 'policy', 'financial', 'general',
            'healthcare', 'patient-records', 'medical', 'clinical', 'laboratory',
            'radiology', 'pharmacy', 'nursing', 'emergency', 'surgery'
        ]
    
    def analyze_content(self, input_data: str) -> List[str]:
        """
        Analyze content and return applicable tags
        
        Args:
            input_data: Raw text to analyze
            
        Returns:
            List of applicable tags
        """
        try:
            if not input_data or not input_data.strip():
                return ['general']
            
            logger.info(f"Analyzing content: {input_data[:100]}...")
            
            analyze_prompt = self._get_analyze_prompt(input_data, self.available_tags)
            response = self.llm.generate_content(analyze_prompt)
            
            # Parse response to extract tags
            tags = self._parse_tags_response(response)
            
            # Filter to only include valid tags
            valid_tags = [tag for tag in tags if tag in self.available_tags]
            
            # If no valid tags found, return a default tag
            if not valid_tags:
                valid_tags = ['general']
                
            logger.info(f"Generated tags: {valid_tags}")
            return valid_tags
            
        except Exception as e:
            logger.error(f"Error in analyze_content: {e}")
            self.handle_error(e, "content_analysis")
            return ['general']  # Default tag if analysis fails
    
    def _get_analyze_prompt(self, content: str, available_tags: List[str]) -> str:
        """Generate prompt for content analysis"""
        return f"""
        You are a document classifier. Use the provided tags to classify the document. 
        Each document can have multiple tags.

        Input:
            Tags: {available_tags}    # allowed labels
            Text: {content}

        Instructions:
        Read the Text and select every tag from Tags that truly describes the Text.
        Output the chosen tags, one per line.
        """
    
    def _parse_tags_response(self, response) -> List[str]:
        """Parse LLM response to extract tags"""
        try:
            # Extract text from response
            if hasattr(response, 'text'):
                tags_text = response.text
            else:
                tags_text = str(response)
            
            # Split by lines and clean up
            tags = [tag.strip() for tag in tags_text.split('\n') if tag.strip()]
            
            # Remove any extra formatting or numbering
            cleaned_tags = []
            for tag in tags:
                # Remove numbers, bullets, dashes at the beginning
                cleaned_tag = tag.lstrip('0123456789.- ').strip()
                if cleaned_tag:
                    cleaned_tags.append(cleaned_tag)
            
            return cleaned_tags
            
        except Exception as e:
            logger.error(f"Error parsing tags response: {e}")
            return ['general']