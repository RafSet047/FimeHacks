import sys
from pathlib import Path
# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Type, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from src.services.workflow_base import BaseWorkflow, WorkflowInput, WorkflowOutput
from src.services.content_types import ContentType
from src.models.metadata import FileMetadata


class WorkflowManager:
    def __init__(self):
        self.workflows: Dict[ContentType, Type[BaseWorkflow]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_workflow(self, content_type: ContentType, workflow_class: Type[BaseWorkflow]):
        self.workflows[content_type] = workflow_class
        self.logger.info(f"Registered {workflow_class.__name__} for {content_type.value}")
    
    def execute_workflow(
        self,
        content_type: ContentType,
        file_id: str,
        file_path: str,
        filename: str,
        mime_type: str,
        file_metadata: FileMetadata,
        db: Session = None
    ) -> WorkflowOutput:
        workflow_class = self.workflows.get(content_type)
        if not workflow_class:
            self.logger.error(f"No workflow registered for {content_type.value}")
            return WorkflowOutput(
                file_id=file_id,
                success=False,
                extracted_content="",
                structured_data={},
                embeddings=[],
                processing_time=0.0,
                error_message=f"No workflow available for {content_type.value}"
            )
        
        workflow_input = WorkflowInput(
            file_id=file_id,
            file_path=file_path,
            filename=filename,
            mime_type=mime_type,
            file_metadata=file_metadata
        )
        
        workflow_instance = workflow_class()
        
        try:
            return workflow_instance.process(workflow_input)
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            return WorkflowOutput(
                file_id=file_id,
                success=False,
                extracted_content="",
                structured_data={},
                embeddings=[],
                processing_time=0.0,
                error_message=str(e)
            )


workflow_manager = WorkflowManager() 