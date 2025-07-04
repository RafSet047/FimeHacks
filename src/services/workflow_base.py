import sys
from pathlib import Path
# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from src.models.metadata import FileMetadata


@dataclass
class WorkflowInput:
    file_id: str
    file_path: str
    filename: str
    mime_type: str
    file_metadata: FileMetadata


@dataclass
class WorkflowOutput:
    file_id: str
    success: bool
    extracted_content: str
    structured_data: Dict[str, Any]
    embeddings: List[List[float]]
    processing_time: float
    error_message: Optional[str] = None


class BaseWorkflow(ABC):
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.logger = logging.getLogger(f"workflow.{workflow_name}")
    
    @abstractmethod
    def process(self, workflow_input: WorkflowInput) -> WorkflowOutput:
        pass
    
    def _create_success_output(
        self, 
        file_id: str, 
        content: str, 
        structured_data: Dict[str, Any], 
        embeddings: List[List[float]],
        processing_time: float
    ) -> WorkflowOutput:
        return WorkflowOutput(
            file_id=file_id,
            success=True,
            extracted_content=content,
            structured_data=structured_data,
            embeddings=embeddings,
            processing_time=processing_time,
            error_message=None
        )
    
    def _create_error_output(self, file_id: str, error_message: str, processing_time: float) -> WorkflowOutput:
        return WorkflowOutput(
            file_id=file_id,
            success=False,
            extracted_content="",
            structured_data={},
            embeddings=[],
            processing_time=processing_time,
            error_message=error_message
        ) 