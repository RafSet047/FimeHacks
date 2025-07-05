import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from src.config.settings import settings
from src.database.connection import init_db
from src.utils.logging import setup_logging
from src.api.file_upload import router as file_upload_router
from src.api.chat import router as chat_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="On-premise super-intelligence system for corporate environments"
)

# Mount React build assets
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Include routers
app.include_router(file_upload_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup_event():
    print('🌿 Starting AI Chat - Green Theme with Glassmorphism')
    print('🎨 Features: Modern green design (#5f9c4a), glass triangles, clean UI')
    print('💎 Transparent geometric patterns with glass effects')
    print('📱 Access at: http://localhost:8080')
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown complete")


@app.get("/api")
async def api_root():
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


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
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
