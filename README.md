# SuperIntelligence AI System - Phase 1 Foundation

This is the foundation setup for the SuperIntelligence AI System, designed for corporate environments (healthcare/hospitals and universities).

## Phase 1 Overview

Phase 1 establishes the basic project structure and core components:

- ✅ Project structure with proper organization
- ✅ Configuration system with environment variables
- ✅ Database models and CRUD operations
- ✅ Logging system
- ✅ Basic FastAPI application
- ✅ Database migration system (Alembic)

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment variables (update with your API keys)
cp .env.example .env

# Edit .env file with your configuration
# - Add your OpenAI, Anthropic, and Google API keys
# - Adjust paths and settings as needed
```

### 3. Foundation Validation

```bash
# Run foundation validation script
python init_foundation.py
```

This script will:
- Test configuration loading
- Create required directories
- Initialize the database
- Test model imports and CRUD operations
- Verify logging system

### 4. Start the Application

```bash
# Start the FastAPI server
python src/main.py
```

Visit:
- http://localhost:8000 - API root
- http://localhost:8000/docs - Interactive API documentation
- http://localhost:8000/health - Health check endpoint

## Project Structure

```
FimeHacks/
├── src/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── database/
│   │   ├── connection.py        # Database connection
│   │   └── crud.py              # CRUD operations
│   ├── models/
│   │   ├── file.py              # File model
│   │   ├── content.py           # Content model
│   │   └── search_index.py      # Search index model
│   ├── utils/
│   │   └── logging.py           # Logging configuration
│   └── main.py                  # FastAPI application
├── alembic/                     # Database migrations
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── init_foundation.py          # Foundation validation script
```

## Database Models

### File Model
- Stores file metadata (filename, path, size, type)
- Tracks processing status
- Supports organizational metadata (department, project, tags)

### Content Model
- Stores processed content from files
- Supports different content types (text, summary, transcript)
- Links to files via foreign key

### Search Index Model
- Stores search metadata and embeddings
- Supports vector search and keyword extraction
- Links to content via foreign key

## Configuration

Key configuration options in `.env`:

```env
# Database
DATABASE_URL=sqlite:///./app.db

# Storage
STORAGE_PATH=./storage
MAX_FILE_SIZE=104857600

# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Vector Database
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

## Database Migrations

Using Alembic for database migrations:

```bash
# Initialize Alembic (already done)
alembic init alembic

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Success Criteria - Phase 1

- ✅ Project structure is organized and modular
- ✅ Configuration system works across environments
- ✅ Database models are defined with proper relationships
- ✅ Basic CRUD operations function correctly
- ✅ Logging system is configured and working
- ✅ FastAPI application starts successfully
- ✅ Database migrations are set up

## Next Steps

Phase 1 is complete! Ready to move to Phase 2: File Management System.

Phase 2 will add:
- File upload and validation
- File storage mechanism
- File processing pipeline
- Content type routing logic

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the virtual environment and have installed all dependencies
2. **Database errors**: Check that the database file can be created in the specified location
3. **Configuration errors**: Verify your `.env` file has the correct settings
4. **Permission errors**: Ensure the application has write permissions for storage and log directories

### Support

For issues specific to this implementation, check:
- Configuration in `.env` file
- Database connection settings
- File permissions for storage directories
- Python environment and dependencies 