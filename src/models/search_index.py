from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.connection import Base
import uuid


class SearchIndex(Base):
    __tablename__ = "search_index"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    index_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, ForeignKey("content.content_id"), nullable=False)
    file_id = Column(String, ForeignKey("files.file_id"), nullable=False)
    
    # Search metadata
    embedding_model = Column(String, nullable=False)  # openai, sentence-transformers, etc.
    embedding_dimension = Column(Integer, nullable=False)
    vector_id = Column(String, nullable=True)  # ChromaDB vector ID
    
    # Search optimization
    keywords = Column(Text, nullable=True)  # Extracted keywords for hybrid search
    summary = Column(Text, nullable=True)  # Short summary for search results
    searchable_text = Column(Text, nullable=True)  # Optimized text for search
    
    # Metadata for search filtering
    metadata_tags = Column(JSON, nullable=True)  # Flattened metadata for filtering
    department = Column(String, nullable=True)
    project = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    language = Column(String, nullable=True)
    
    # Search performance tracking
    search_weight = Column(Float, default=1.0)  # Importance weight for ranking
    is_active = Column(Boolean, default=True)  # Whether to include in search
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    content = relationship("Content", backref="search_indices")
    file = relationship("File", backref="search_indices")
    
    def __repr__(self):
        return f"<SearchIndex(id={self.id}, content_id={self.content_id}, model={self.embedding_model})>" 