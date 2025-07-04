from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.connection import Base
import uuid


class ProcessingEvent(Base):
    __tablename__ = "processing_events"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("files.file_id"), nullable=False)
    
    # Event information
    event_type = Column(String, nullable=False)  # uploaded, processing_started, processing_completed, processing_failed, indexed
    event_status = Column(String, nullable=False)  # success, error, warning, info
    event_message = Column(Text, nullable=True)
    
    # Processing details
    processing_step = Column(String, nullable=True)  # validation, content_extraction, embedding_generation, indexing
    workflow_type = Column(String, nullable=True)  # text_workflow, image_workflow, etc.
    processing_duration_seconds = Column(Integer, nullable=True)
    
    # Event metadata
    event_metadata = Column(JSON, nullable=True)  # Additional event-specific data
    error_details = Column(Text, nullable=True)  # Detailed error information
    
    # System information
    system_component = Column(String, nullable=True)  # file_upload, file_processor, workflow_manager
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationship
    file = relationship("File", backref="processing_events")
    
    def __repr__(self):
        return f"<ProcessingEvent(id={self.id}, file_id={self.file_id}, type={self.event_type}, status={self.event_status})>" 