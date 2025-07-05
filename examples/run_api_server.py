#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from src.api.file_upload import router as file_router

# Create FastAPI app
app = FastAPI(title="Document Processing API")

# Add routers
app.include_router(file_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 