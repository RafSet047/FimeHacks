import sys
from pathlib import Path
# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from typing import List, Dict, Any
import re

from src.services.workflow_base import BaseWorkflow, WorkflowInput, WorkflowOutput


class TextWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__("TextWorkflow")
    
    def process(self, workflow_input: WorkflowInput) -> WorkflowOutput:
        start_time = datetime.now()
        
        try:
            # Read file content
            with open(workflow_input.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract structured data
            structured_data = self._extract_structured_data(content)
            
            # Generate simple embeddings (placeholder)
            embeddings = self._generate_embeddings(content)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return self._create_success_output(
                file_id=workflow_input.file_id,
                content=content,
                structured_data=structured_data,
                embeddings=embeddings,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return self._create_error_output(
                file_id=workflow_input.file_id,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _extract_structured_data(self, content: str) -> Dict[str, Any]:
        words = content.split()
        
        return {
            "word_count": len(words),
            "char_count": len(content),
            "line_count": len(content.split('\n')),
            "keywords": self._extract_keywords(content),
            "summary": self._generate_summary(content)
        }
    
    def _extract_keywords(self, content: str) -> List[str]:
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 10 keywords
        return [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    def _generate_summary(self, content: str) -> str:
        # Simple summary - first 200 characters
        return content[:200] + "..." if len(content) > 200 else content
    
    def _generate_embeddings(self, content: str) -> List[List[float]]:
        # Placeholder embedding generation - in real implementation use OpenAI/sentence-transformers
        chunks = [content[i:i+500] for i in range(0, len(content), 500)]
        embeddings = []
        
        for chunk in chunks:
            # Simple hash-based embedding (not for production)
            embedding = [float(hash(chunk + str(i)) % 100) / 100.0 for i in range(384)]
            embeddings.append(embedding)
        
        return embeddings 