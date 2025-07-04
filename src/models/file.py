from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.sql import func
from src.database.connection import Base
from datetime import datetime
from typing import Optional
import uuid


class File(Base):
    __tablename__ = "files"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    
    # Processing status
    status = Column(String, default="uploaded")  # uploaded, processing, processed, failed, indexed
    processing_error = Column(Text, nullable=True)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_duration_seconds = Column(Float, nullable=True)
    content_extracted = Column(Boolean, default=False)
    content_indexed = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    
    # Organizational metadata (kept for backward compatibility)
    department = Column(String, nullable=True)
    project = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string of tags
    
    # Complete metadata structure (renamed to avoid SQLAlchemy reserved name)
    file_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<File(id={self.id}, filename={self.filename}, status={self.status})>" 