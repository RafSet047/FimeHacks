from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.connection import Base
import uuid


class Content(Base):
    __tablename__ = "content"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("files.file_id"), nullable=False)
    
    # Content information
    content_type = Column(String, nullable=False)  # text, summary, transcript, description
    content_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, default=0)
    total_chunks = Column(Integer, default=1)
    
    # Processing metadata
    processing_method = Column(String, nullable=True)  # openai, anthropic, google
    confidence_score = Column(Float, nullable=True)
    processing_metadata = Column(JSON, nullable=True)
    
    # Content summary and analysis
    content_summary = Column(Text, nullable=True)
    extracted_keywords = Column(Text, nullable=True)  # JSON string of keywords
    language_detected = Column(String, nullable=True)
    
    # Embeddings storage
    has_embeddings = Column(Boolean, default=False)
    embedding_model = Column(String, nullable=True)  # model used for embeddings
    embedding_dimension = Column(Integer, nullable=True)
    vector_id = Column(String, nullable=True)  # ChromaDB vector ID
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship
    file = relationship("File", backref="contents")
    
    def __repr__(self):
        return f"<Content(id={self.id}, file_id={self.file_id}, type={self.content_type})>" 