#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from src.config.settings import settings
from src.database.connection import init_db, get_db
from src.utils.logging import setup_logging
from src.api.file_upload import router as file_upload_router
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import time

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.services.external_apis.google_service import get_google_service
from src.database.milvus_db import MilvusVectorDatabase
from src.services.document_extractor import document_extractor
from src.services.text_chunking import TextChunker, ChunkingStrategy, ChunkingConfig
from src.utils.logging import setup_logging

# Import StoreAgent and MetadataAdapter
from src.agents.store_agent import StoreAgent
from src.services.metadata_adapter import MetadataAdapter

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vector Store API",
    description="Simplified API for document processing and vector search",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount React build assets
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Mount Admin Panel build assets
app.mount("/admin/assets", StaticFiles(directory="admin-panel/dist/assets"), name="admin_assets")

# Include routers
app.include_router(file_upload_router)

# Global services
google_service = None
milvus_db = None
text_chunker = None
store_agent = None

# Request/Response models
class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    collection_name: str = "text_embeddings"

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int

class ProcessResponse(BaseModel):
    success: bool
    message: str
    document_ids: List[str]
    chunks_processed: int
    embeddings_generated: int
    ai_tags: Optional[List[str]] = None
    analysis_time: Optional[float] = None
    file_id: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    database_id: Optional[int] = None
    department: Optional[str] = None
    project: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, bool]
    message: str

# Add chat-specific models
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global google_service, milvus_db, text_chunker, store_agent

    try:
        # Initialize services
        google_service = get_google_service()
        milvus_db = MilvusVectorDatabase()
        text_chunker = TextChunker()

        # Connect to Milvus
        if not milvus_db.connect():
            logger.error("Failed to connect to Milvus database")
            raise RuntimeError("Milvus connection failed")

        # Create collections
        if not milvus_db.create_all_collections():
            logger.error("Failed to create collections")
            raise RuntimeError("Collection creation failed")

        # Initialize StoreAgent
        store_agent = StoreAgent(
            name="ContentAnalyzer",
            description="Analyzes document content and generates intelligent tags"
        )

        logger.info("All services initialized successfully")
        logger.info(f"StoreAgent initialized with {len(store_agent.available_tags)} available tags")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    print('🌿 Starting AI Chat - Green Theme with Glassmorphism')
    print('🎨 Features: Modern green design (#5f9c4a), glass triangles, clean UI')
    print('💎 Transparent geometric patterns with glass effects')
    print('📱 Access at: http://localhost:8080')
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global milvus_db
    if milvus_db:
        milvus_db.disconnect()
    logger.info("Services shutdown complete")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Google service
        google_status = False
        if google_service:
            status_info = google_service.get_service_status()
            google_status = status_info.get("genai_configured", False)

        # Check Milvus
        milvus_status = False
        if milvus_db:
            milvus_status = milvus_db.health_check()

        # Check StoreAgent
        store_agent_status = False
        if store_agent:
            agent_status = store_agent.get_status()
            store_agent_status = agent_status.get("is_active", False)

        # Overall status
        overall_status = "healthy" if (google_status and milvus_status and store_agent_status) else "unhealthy"

        return HealthResponse(
            status=overall_status,
            services={
                "google_api": google_status,
                "milvus": milvus_status,
                "text_chunker": text_chunker is not None,
                "store_agent": store_agent_status
            },
            message="Service health check completed"
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

@app.post("/process", response_model=ProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    metadata: str = Form(default='{"department": "demo", "description": "uploaded document"}'),
    db: Session = Depends(get_db)
):
    """Process document: upload → extract → analyze → chunk → embed → store"""
    logger.info(f"Processing document upload: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")

    try:
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
            logger.info(f"Parsed metadata: {metadata_dict}")
        except json.JSONDecodeError:
            metadata_dict = {"department": "demo", "description": "uploaded document"}
            logger.warning("Invalid metadata JSON, using defaults")

        # Use file upload service for file upload and storage
        from src.services.file_upload import file_upload_service
        from src.models.metadata import FileMetadata
        
        # Create FileMetadata object
        file_metadata = FileMetadata(
            department=metadata_dict.get("department", "demo"),
            project_name=metadata_dict.get("project", ""),
            description=metadata_dict.get("description", "uploaded document"),
            tags=metadata_dict.get("tags", []),
            document_type=metadata_dict.get("document_type", "other"),
            content_category=metadata_dict.get("content_category", "other"),
            priority_level=metadata_dict.get("priority_level", "medium"),
            access_level=metadata_dict.get("access_level", "internal"),
            employee_role=metadata_dict.get("employee_role", "staff"),
            uploaded_by=metadata_dict.get("uploaded_by", "system"),
            domain_type=metadata_dict.get("domain_type", "general")
        )
        
        # Upload file using the service
        upload_result = await file_upload_service.upload_file(
            file=file,
            db=db,
            file_metadata=file_metadata
        )
        
        if not upload_result["success"]:
            logger.error(f"File upload failed: {upload_result.get('errors', [])}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File upload failed: {upload_result.get('errors', [])}"
            )
        
        # Get the uploaded file path for processing
        temp_file_path = upload_result["storage_path"]
        logger.info(f"File uploaded successfully to: {temp_file_path}")
        
        # Get file content for processing
        with open(temp_file_path, 'rb') as f:
            content = f.read()

        # Extract text
        mime_type = upload_result["mime_type"]
        logger.info(f"Extracting text from {file.filename} (MIME: {mime_type})")
        extracted_text = document_extractor.extract_text(temp_file_path, mime_type)

        if not extracted_text.strip():
            logger.error(f"No text extracted from {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text could be extracted from the file"
            )

        logger.info(f"Extracted {len(extracted_text)} characters from {file.filename}")

        # NEW: StoreAgent Content Analysis
        analysis_start_time = time.time()
        logger.info("Analyzing document content with StoreAgent")
        
        # Use first 2000 characters for analysis to manage LLM context
        analysis_text = extracted_text[:2000] if len(extracted_text) > 2000 else extracted_text
        ai_tags = store_agent.analyze_content(analysis_text)
        
        analysis_time = time.time() - analysis_start_time
        logger.info(f"Content analysis completed in {analysis_time:.2f}s, generated tags: {ai_tags}")

        # Prepare base metadata for all chunks
        base_metadata = {
            "filename": upload_result.get("filename", file.filename),
            "original_filename": upload_result.get("original_filename", file.filename),
            "file_id": upload_result.get("file_id"),
            "department": upload_result.get("department", "demo"),
            "description": metadata_dict.get("description", ""),
            "tags": upload_result.get("tags", []),
            "project": upload_result.get("project", ""),
            "content_length": len(extracted_text),
            "mime_type": mime_type,
            "analysis_time": analysis_time,
            "upload_timestamp": time.time(),
            "file_size": upload_result.get("file_size"),
            "file_type": upload_result.get("file_type"),
            "database_id": upload_result.get("database_id")
        }

        # Chunk text
        config = ChunkingConfig(
            chunk_size=500,
            chunk_overlap=50,
            add_start_index=True
        )

        logger.info(f"Chunking text with config: size={config.chunk_size}, overlap={config.chunk_overlap}")
        chunks = text_chunker.chunk_text(
            text=extracted_text,
            strategy=ChunkingStrategy.RECURSIVE,
            config=config,
            metadata={"source": file.filename}
        )
        logger.info(f"Created {len(chunks)} chunks from {file.filename}")

        # Process chunks: embed and store with AI-enhanced metadata
        document_ids = []
        embeddings_generated = 0

        for i, chunk in enumerate(chunks):
            try:
                # Generate embeddings
                chunk_text = chunk.page_content
                embeddings = google_service.generate_text_embeddings(chunk_text)

                if not embeddings:
                    logger.warning(f"Failed to generate embeddings for chunk {i}")
                    continue

                embeddings_generated += 1

                # Create enhanced metadata using MetadataAdapter
                chunk_metadata = MetadataAdapter.prepare_chunk_metadata(
                    base_metadata=base_metadata,
                    chunk_text=chunk_text,
                    chunk_index=i,
                    total_chunks=len(chunks)
                )

                # Enhance metadata with AI tags
                enhanced_metadata = MetadataAdapter.simple_to_enhanced(
                    simple_metadata=chunk_metadata,
                    ai_tags=ai_tags,
                    chunk_info={
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "start_index": chunk.metadata.get("start_index", 0),
                        "end_index": chunk.metadata.get("end_index", 0)
                    }
                )

                # Store in Milvus with enhanced metadata
                doc_id = milvus_db.insert_data(
                    collection_name="text_embeddings",
                    vector=embeddings[0],
                    metadata=enhanced_metadata,
                    content_type="document",
                    department=upload_result.get("department", "demo"),
                    file_size=len(chunk_text.encode()),
                    content_hash=f"chunk_{i}_{upload_result.get('file_id')}_{int(time.time())}"
                )

                if doc_id:
                    document_ids.append(doc_id)
                    logger.info(f"Stored chunk {i+1}/{len(chunks)} with AI tags: {doc_id}")

            except Exception as e:
                logger.error(f"Error processing chunk {i}: {e}")
                continue

        # Return results with AI analysis information and file upload details
        logger.info(f"Document processing complete: {len(chunks)} chunks processed, {len(document_ids)} documents stored, {embeddings_generated} embeddings generated")
        return ProcessResponse(
            success=len(document_ids) > 0,
            message=f"File uploaded and processed: {len(chunks)} chunks with AI analysis, stored {len(document_ids)} documents",
            document_ids=document_ids,
            chunks_processed=len(chunks),
            embeddings_generated=embeddings_generated,
            ai_tags=ai_tags,
            analysis_time=analysis_time,
            file_id=upload_result.get("file_id"),
            filename=upload_result.get("filename"),
            file_size=upload_result.get("file_size"),
            file_type=upload_result.get("file_type"),
            database_id=upload_result.get("database_id"),
            department=upload_result.get("department"),
            project=upload_result.get("project")
        )

    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )

    finally:
        # No cleanup needed - file upload service manages file storage
        pass

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Vector search for similar documents"""
    try:
        logger.info(f"Search request received: query='{request.query[:50]}...', limit={request.limit}")

        # Generate query embeddings
        query_embeddings = google_service.generate_text_embeddings(request.query)

        if not query_embeddings:
            logger.error("Failed to generate query embeddings")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to generate query embeddings"
            )

        logger.info(f"Generated embeddings for query, vector size: {len(query_embeddings[0])}")

        # Search in Milvus
        results = milvus_db.vector_search(
            collection_name=request.collection_name,
            query_vector=query_embeddings[0],
            limit=request.limit
        )

        logger.info(f"Search completed, found {len(results)} results")

        # Simplify results for response
        simplified_results = []
        for result in results:
            simplified_result = {
                "id": result.get("id"),
                "score": result.get("score"),
                "department": result.get("department"),
                "content_type": result.get("content_type"),
                "metadata": result.get("metadata", {})
            }
            simplified_results.append(simplified_result)

        return SearchResponse(
            results=simplified_results,
            query=request.query,
            total_results=len(simplified_results)
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Chat endpoint that uses vector search to find relevant documents"""
    try:
        user_message = chat_message.message.strip()
        logger.info(f"Chat message received: '{user_message[:100]}...'")

        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Use search functionality to find relevant documents
        search_request = SearchRequest(
            query=user_message,
            limit=3,  # Get top 3 most relevant results
            collection_name="text_embeddings"
        )

        logger.info(f"Performing vector search for chat query")

        # Generate query embeddings
        query_embeddings = google_service.generate_text_embeddings(user_message)

        if not query_embeddings:
            logger.warning("Failed to generate embeddings for chat query")
            return ChatResponse(
                response="I'm having trouble understanding your question right now. Please try again.",
                status="error"
            )

        logger.info(f"Generated embeddings for chat query, vector size: {len(query_embeddings[0])}")

        # Search in Milvus
        results = milvus_db.vector_search(
            collection_name="text_embeddings",
            query_vector=query_embeddings[0],
            limit=3
        )

        logger.info(f"Found {len(results)} relevant documents for chat query")

        # Generate response based on search results
        if results:
            # Format the response based on the search results
            response_parts = []
            response_parts.append(f"Based on the documents in our knowledge base, here's what I found:")

            for i, result in enumerate(results, 1):
                metadata = result.get("metadata", {})
                score = result.get("score", 0)

                # Extract relevant information from metadata
                filename = metadata.get("filename", "Unknown document")
                chunk_text = metadata.get("chunk_text", "")
                department = result.get("department", "General")

                if chunk_text:
                    response_parts.append(f"\n{i}. From {filename} (Department: {department}):")
                    response_parts.append(f"   {chunk_text}")
                    if score:
                        response_parts.append(f"   (Relevance: {score:.2f})")

            response = "\n".join(response_parts)
            logger.info(f"Generated response with {len(results)} search results")

        else:
            response = "I couldn't find any relevant documents for your question. Could you try rephrasing your question or check if any documents have been uploaded to the system?"
            logger.info("No search results found, returning fallback response")

        return ChatResponse(response=response)

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            response="I encountered an error while processing your request. Please try again.",
            status="error"
        )

def _get_mime_type(filename: str) -> str:
    """Get MIME type from filename"""
    extension = Path(filename).suffix.lower()

    mime_types = {
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.html': 'text/html',
        '.json': 'application/json',
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    return mime_types.get(extension, 'text/plain')

@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/", response_class=HTMLResponse)
async def serve_admin_panel():
    """Serve the admin panel application"""
    try:
        with open("admin-panel/dist/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Admin panel not built yet. Run: cd admin-panel && npm run build</h1>",
            status_code=404
        )

@app.get("/admin/{path:path}", response_class=HTMLResponse)
async def serve_admin_panel_catch_all(path: str):
    """Serve the admin panel for all /admin/* routes (client-side routing)"""
    try:
        with open("admin-panel/dist/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Admin panel not built yet. Run: cd admin-panel && npm run build</h1>",
            status_code=404
        )

@app.get("/", response_class=HTMLResponse)
async def serve_react_app():
    """Serve the React chat application"""
    try:
        with open("frontend/dist/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>React app not built yet. Run: cd frontend && npm run build</h1>",
            status_code=404
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
