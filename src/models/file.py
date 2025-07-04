from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
from src.database.connection import Base
from datetime import datetime
from typing import Optional
import uuid


class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    
    # Processing status
    status = Column(String, default="uploaded")  # uploaded, processing, processed, failed
    processing_error = Column(Text, nullable=True)
    
    # Organizational metadata
    department = Column(String, nullable=True)
    project = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string of tags
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<File(id={self.id}, filename={self.filename}, status={self.status})>" 