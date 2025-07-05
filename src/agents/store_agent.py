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
        
        # Load available departments
        self.available_departments = self._load_available_departments()
        
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
    
    def _load_available_departments(self) -> List[str]:
        """Load available departments from static source"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config',
                'available_tags.json'
            )
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return config_data.get('departments', self._get_default_departments())
        except Exception as e:
            logger.warning(f"Failed to load departments from config: {e}")
        
        # Fallback to default departments
        return self._get_default_departments()
    
    def _get_default_departments(self) -> List[str]:
        """Get default departments for university/healthcare context"""
        return [
            'administration', 'finance', 'hr', 'it', 'legal', 'marketing',
            'operations', 'research', 'academic', 'student-services',
            'healthcare', 'medical', 'nursing', 'pharmacy', 'laboratory',
            'emergency', 'surgery', 'radiology', 'general'
        ]
    
    def analyze_content(self, input_data: str) -> Dict[str, Any]:
        """
        Analyze content and return applicable tags, description, and department
        
        Args:
            input_data: Raw text to analyze
            
        Returns:
            Dictionary containing:
                - tags: List of applicable tags
                - description: Brief description of the content
                - department: Most appropriate department
        """
        try:
            if not input_data or not input_data.strip():
                return {
                    'tags': ['general'],
                    'description': 'Empty or invalid document',
                    'department': 'general'
                }
            
            logger.info(f"Analyzing content: {input_data[:100]}...")
            
            analyze_prompt = self._get_analyze_prompt(input_data, self.available_tags, self.available_departments)
            response = self.llm.generate_content(analyze_prompt)
            
            # Parse response to extract tags, description, and department
            result = self._parse_analysis_response(response)
            
            # Validate and filter results
            result = self._validate_analysis_result(result)
            
            logger.info(f"Generated analysis: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_content: {e}")
            self.handle_error(e, "content_analysis")
            return {
                'tags': ['general'],
                'description': 'Error analyzing document content',
                'department': 'general'
            }
    
    def _get_analyze_prompt(self, content: str, available_tags: List[str], available_departments: List[str]) -> str:
        """Generate prompt for comprehensive content analysis"""
        return f"""
        You are a document classifier and analyzer. Analyze the provided document and extract three pieces of information:

        Available Tags: {available_tags}
        Available Departments: {available_departments}

        Document Content:
        {content}

        Instructions:
        1. Select ALL applicable tags from the Available Tags list that describe this document
        2. Choose the ONE most appropriate department from the Available Departments list
        3. Write a brief 1-2 sentence description of the document's content and purpose

        Output Format (exactly as shown):
        TAGS: tag1, tag2, tag3
        DEPARTMENT: department_name
        DESCRIPTION: Brief description of the document content and purpose.

        Example:
        TAGS: financial, policy, administrative
        DEPARTMENT: finance
        DESCRIPTION: Budget allocation document outlining financial planning and resource distribution for the upcoming fiscal year.
        """
    
    def _parse_analysis_response(self, response) -> Dict[str, Any]:
        """Parse LLM response to extract tags, description, and department"""
        try:
            # Extract text from response
            if hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = str(response)
            
            logger.info(f"Parsing response: {response_text[:200]}...")
            
            # Initialize result with defaults
            result = {
                'tags': ['general'],
                'description': 'Document content analysis',
                'department': 'general'
            }
            
            # Parse each line for the expected format
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('TAGS:'):
                    tags_str = line[5:].strip()
                    if tags_str:
                        # Split by comma and clean up
                        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                        result['tags'] = tags
                
                elif line.startswith('DEPARTMENT:'):
                    department = line[11:].strip()
                    if department:
                        result['department'] = department
                
                elif line.startswith('DESCRIPTION:'):
                    description = line[12:].strip()
                    if description:
                        result['description'] = description
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return {
                'tags': ['general'],
                'description': 'Error parsing document analysis',
                'department': 'general'
            }
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and filter analysis results"""
        try:
            # Filter tags to only include valid ones
            valid_tags = [tag for tag in result.get('tags', []) if tag in self.available_tags]
            if not valid_tags:
                valid_tags = ['general']
            result['tags'] = valid_tags
            
            # Validate department
            department = result.get('department', 'general')
            if department not in self.available_departments:
                department = 'general'
            result['department'] = department
            
            # Ensure description is reasonable length
            description = result.get('description', 'Document content analysis')
            if len(description) > 200:
                description = description[:200] + '...'
            result['description'] = description
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating analysis result: {e}")
            return {
                'tags': ['general'],
                'description': 'Error validating document analysis',
                'department': 'general'
            }