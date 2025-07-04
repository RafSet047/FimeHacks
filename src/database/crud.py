from sqlalchemy.orm import Session
from typing import List, Optional
from src.models import File, Content, SearchIndex
import logging

logger = logging.getLogger(__name__)


class FileCRUD:
    @staticmethod
    def create_file(db: Session, file_data: dict) -> File:
        db_file = File(**file_data)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        logger.info(f"Created file record: {db_file.filename}")
        return db_file
    
    @staticmethod
    def get_file_by_id(db: Session, file_id: str) -> Optional[File]:
        return db.query(File).filter(File.file_id == file_id).first()
    
    @staticmethod
    def get_files(db: Session, skip: int = 0, limit: int = 100) -> List[File]:
        return db.query(File).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_file_status(db: Session, file_id: str, status: str, error: str = None) -> Optional[File]:
        db_file = db.query(File).filter(File.file_id == file_id).first()
        if db_file:
            db_file.status = status
            if error:
                db_file.processing_error = error
            db.commit()
            db.refresh(db_file)
            logger.info(f"Updated file {file_id} status to {status}")
        return db_file
    
    @staticmethod
    def delete_file(db: Session, file_id: str) -> bool:
        db_file = db.query(File).filter(File.file_id == file_id).first()
        if db_file:
            db.delete(db_file)
            db.commit()
            logger.info(f"Deleted file: {file_id}")
            return True
        return False


class ContentCRUD:
    @staticmethod
    def create_content(db: Session, content_data: dict) -> Content:
        db_content = Content(**content_data)
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        logger.info(f"Created content record for file: {db_content.file_id}")
        return db_content
    
    @staticmethod
    def get_content_by_file_id(db: Session, file_id: str) -> List[Content]:
        return db.query(Content).filter(Content.file_id == file_id).all()
    
    @staticmethod
    def get_content_by_id(db: Session, content_id: str) -> Optional[Content]:
        return db.query(Content).filter(Content.content_id == content_id).first()
    
    @staticmethod
    def search_content(db: Session, query: str, limit: int = 10) -> List[Content]:
        return db.query(Content).filter(
            Content.content_text.contains(query)
        ).limit(limit).all()


class SearchIndexCRUD:
    @staticmethod
    def create_search_index(db: Session, index_data: dict) -> SearchIndex:
        db_index = SearchIndex(**index_data)
        db.add(db_index)
        db.commit()
        db.refresh(db_index)
        logger.info(f"Created search index for content: {db_index.content_id}")
        return db_index
    
    @staticmethod
    def get_search_index_by_content_id(db: Session, content_id: str) -> Optional[SearchIndex]:
        return db.query(SearchIndex).filter(SearchIndex.content_id == content_id).first()
    
    @staticmethod
    def get_all_search_indices(db: Session) -> List[SearchIndex]:
        return db.query(SearchIndex).all()


file_crud = FileCRUD()
content_crud = ContentCRUD()
search_index_crud = SearchIndexCRUD() 