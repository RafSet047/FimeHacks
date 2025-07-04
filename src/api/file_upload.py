from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from src.database.connection import get_db
from src.services.file_upload import file_upload_service
from src.utils.logging import logger

router = APIRouter(prefix="/api/files", tags=["files"])


class FileUploadResponse(BaseModel):
    success: bool
    file_id: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    file_hash: Optional[str] = None
    database_id: Optional[int] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None


class FileInfoResponse(BaseModel):
    file_id: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    status: str
    department: Optional[str] = None
    project: Optional[str] = None
    tags: List[str] = []
    created_at: str
    updated_at: str


class FileListResponse(BaseModel):
    files: List[FileInfoResponse]
    total: int
    page: int
    page_size: int


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    department: Optional[str] = Form(None),
    project: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a file with optional metadata
    
    Args:
        file: File to upload
        department: Department tag (optional)
        project: Project tag (optional)
        tags: Comma-separated tags (optional)
        db: Database session
    
    Returns:
        FileUploadResponse with upload results
    """
    try:
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Upload file
        result = await file_upload_service.upload_file(
            file=file,
            db=db,
            department=department,
            project=project,
            tags=tag_list
        )
        
        return FileUploadResponse(**result)
    
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/info/{file_id}", response_model=FileInfoResponse)
async def get_file_info(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Get file information by file ID
    
    Args:
        file_id: Unique file identifier
        db: Database session
    
    Returns:
        FileInfoResponse with file details
    """
    try:
        file_info = await file_upload_service.get_file_info(file_id, db)
        
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_id}"
            )
        
        return FileInfoResponse(**file_info)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving file info: {str(e)}"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a file by file ID
    
    Args:
        file_id: Unique file identifier
        db: Database session
    
    Returns:
        Success message
    """
    try:
        success = await file_upload_service.delete_file(file_id, db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found or could not be deleted: {file_id}"
            )
        
        return {"message": f"File {file_id} deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )


@router.get("/list", response_model=FileListResponse)
async def list_files(
    page: int = 1,
    page_size: int = 10,
    department: Optional[str] = None,
    project: Optional[str] = None,
    file_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List files with optional filtering
    
    Args:
        page: Page number (1-based)
        page_size: Number of files per page
        department: Filter by department
        project: Filter by project
        file_type: Filter by file type
        db: Database session
    
    Returns:
        FileListResponse with file list
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get files from database
        files = await _get_filtered_files(db, offset, page_size, department, project, file_type)
        
        # Convert to response format
        file_responses = []
        for file in files:
            file_info = await file_upload_service.get_file_info(file.file_id, db)
            if file_info:
                file_responses.append(FileInfoResponse(**file_info))
        
        return FileListResponse(
            files=file_responses,
            total=len(file_responses),
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}"
        )


async def _get_filtered_files(
    db: Session, 
    offset: int, 
    limit: int,
    department: Optional[str] = None,
    project: Optional[str] = None,
    file_type: Optional[str] = None
):
    """Helper function to get filtered files"""
    from src.database.crud import file_crud
    
    # For now, use simple pagination - will enhance with filtering later
    return file_crud.get_files(db, skip=offset, limit=limit)


@router.get("/stats")
async def get_file_stats(db: Session = Depends(get_db)):
    """
    Get file statistics
    
    Returns:
        File statistics including count, total size, etc.
    """
    try:
        from src.database.crud import file_crud
        
        files = file_crud.get_files(db, skip=0, limit=1000)  # Get all files for stats
        
        stats = {
            "total_files": len(files),
            "total_size": sum(f.file_size for f in files),
            "file_types": {},
            "departments": {},
            "projects": {}
        }
        
        for file in files:
            # Count file types
            file_type = file.file_type
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
            
            # Count departments
            if file.department:
                stats["departments"][file.department] = stats["departments"].get(file.department, 0) + 1
            
            # Count projects
            if file.project:
                stats["projects"][file.project] = stats["projects"].get(file.project, 0) + 1
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting file stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting file stats: {str(e)}"
        ) 