# Project Context & Technical Requirements Summary

## Project Overview
Building an **on-premise super-intelligence system** for corporate environments (healthcare/hospitals and universities) that provides comprehensive knowledge management and AI-powered assistance for employees.

## Core Vision
- **Goal**: Create a system that knows "EVERYTHING" about a company's data and procedures
- **Scope**: Handle multimodal data (text, documents, images, audio, video, transcripts, meetings)
- **Usage**: Employees can ask specific questions about company procedures and receive factual, non-hallucinated responses
- **Deployment**: On-premise initially, with API-based LLM integration transitioning to local models later

## Target Domains

### Healthcare/Hospitals
- **Organizational Structure**: Departments (cardiology, neurology, emergency, etc.), roles (physician, nurse, administrator), security levels
- **Data Types**: Patient records, medical imaging, lab results, treatment protocols, research data
- **Compliance**: HIPAA requirements, PHI protection, audit trails
- **Specific Needs**: Medical terminology, clinical workflows, emergency access protocols

### Universities
- **Organizational Structure**: Departments (CS, biology, engineering, etc.), roles (student, faculty, researcher), academic levels
- **Data Types**: Research papers, lecture recordings, course materials, thesis work, lab data
- **Compliance**: FERPA requirements, research ethics, academic integrity
- **Specific Needs**: Citation analysis, collaboration networks, academic workflows

## Technical Architecture Decisions

### Simplified Approach (Current Phase)
- **External API Integration**: Use OpenAI, Anthropic, and Google GenAI APIs for content processing
- **No Local ML**: Avoid complex local machine learning initially
- **Modular Design**: Security and authorization to be implemented later
- **CLI-First**: Command-line tools for upload and search as primary interface

### Core Components
1. **File Management System**: Upload, validation, storage with metadata
2. **API Integration Layer**: Unified service for external AI APIs
3. **Search Engine**: Hybrid semantic + keyword search using vector database
4. **CLI Tools**: Upload and search command-line utilities
5. **REST API**: Web service endpoints for future integration
6. **Database Layer**: Metadata storage and content indexing

### Technology Stack

#### Backend Framework
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Database ORM with async support
- **Pydantic**: Data validation and settings management

#### Storage & Database
- **SQLite**: Simple database for development
- **PostgreSQL**: Production database (future)
- **ChromaDB**: Vector database for semantic search
- **Local Filesystem**: File storage (development)

#### External API Integration
- **OpenAI API**: Text analysis, embeddings, Whisper transcription
- **Anthropic API**: Text analysis and reasoning
- **Google GenAI**: Vision API for images and documents

#### Processing & Utilities
- **python-magic**: File type detection
- **aiofiles**: Async file operations
- **Basic file processing**: No complex local ML libraries

## Data Processing Strategy

### Content Analysis via APIs
- **Text Files**: OpenAI/Anthropic for summarization and key point extraction
- **Images**: Google GenAI Vision for description and OCR
- **Audio**: OpenAI Whisper for transcription, then text processing
- **Video**: Frame extraction + audio processing separately
- **Documents**: Convert to images, use Vision APIs for analysis

### Storage Strategy
- **File Storage**: Organized directory structure with unique identifiers
- **Metadata Storage**: Database with file information, processing results, embeddings
- **Content Indexing**: Vector embeddings for semantic search
- **Organizational Tags**: Flexible tagging system (department, project, type, etc.)

## Key Design Principles

### Flexibility Over Rigid Structure
- **No Hardcoded Hierarchies**: Avoid fixed company structures
- **User-Configurable**: Allow companies to define their own organizational taxonomy
- **Dynamic Classification**: AI-powered content categorization based on company rules
- **Tag-Based Organization**: Flexible tagging instead of rigid folder structures

### API-First Architecture
- **External Processing**: Leverage powerful external APIs for content analysis
- **Unified Interface**: Single API service layer for all external integrations
- **Error Handling**: Robust retry logic and graceful degradation
- **Rate Limiting**: Manage API usage and costs

### Modular & Extensible
- **Security Layer**: Can be added later without architecture changes
- **Authentication**: Placeholder for future LDAP/SSO integration
- **Local Models**: Architecture ready for future local LLM integration
- **Compliance**: Framework ready for HIPAA/FERPA requirements

## Implementation Constraints

### Current Limitations
- **No Authentication**: Security implementation deferred
- **No Complex Processing**: Minimal local ML/NLP
- **No Real-time**: Batch processing acceptable initially
- **No UI**: Focus on backend and CLI tools only

### Future Considerations
- **Scalability**: Architecture designed for horizontal scaling
- **Compliance**: Framework ready for regulatory requirements
- **Local Models**: Can transition from APIs to local LLMs
- **Advanced Features**: Role-based access, real-time processing, advanced UI

## Critical Requirements

### Data Accuracy
- **No Hallucination**: System must respond only with factual information from stored data
- **Source Attribution**: Clear indication of information sources
- **Confidence Levels**: Indicate uncertainty when data is incomplete
- **Company-Specific**: Responses must be based on company's actual data

### Search Capabilities
- **Semantic Search**: Vector similarity for concept-based queries
- **Keyword Search**: Traditional text matching for specific terms
- **Hybrid Results**: Combine and rank semantic + keyword results
- **Filtering**: Search by department, document type, date, etc.

### File Processing
- **Multimodal Support**: Handle text, images, audio, video, documents
- **Metadata Extraction**: Automatic content analysis and tagging
- **Content Chunking**: Break large files into searchable segments
- **Format Flexibility**: Support various file formats and types

## CLI Tool Requirements

### Upload CLI
- **File Upload**: Single and batch file upload with progress tracking
- **Metadata Tagging**: Add organizational tags and categories
- **Validation**: File type and size validation
- **Processing Status**: Track upload and processing progress

### Search CLI
- **Query Processing**: Natural language search queries
- **Result Display**: Formatted search results with relevance scoring
- **Filtering Options**: Search by metadata, tags, departments
- **Export Functionality**: Save search results to files

## Success Metrics

### Technical Performance
- **Upload Speed**: Efficient file processing and storage
- **Search Accuracy**: Relevant results for user queries
- **API Integration**: Reliable external service connections
- **Error Handling**: Graceful failure management

### User Experience
- **CLI Usability**: Simple, intuitive command-line interface
- **Result Quality**: Accurate, relevant search results
- **Processing Time**: Reasonable response times for all operations
- **Reliability**: Consistent system behavior

## Next Steps Context
- **Phase 1**: Foundation setup with project structure and database
- **Phase 2**: File management system implementation
- **Phase 3**: External API integration for content analysis
- **Phase 4**: Search system with vector database
- **Phase 5**: CLI tools development
- **Implementation Timeline**: 5-week development cycle with specific deliverables

## Domain-Specific Considerations

### Healthcare Context
- **Data Sensitivity**: Prepare for HIPAA compliance requirements
- **Medical Terminology**: Consider medical NLP models for better accuracy
- **Emergency Access**: Plan for urgent access scenarios
- **Audit Requirements**: Comprehensive logging for regulatory compliance

### University Context
- **Academic Workflows**: Research collaboration and citation tracking
- **Student Privacy**: FERPA compliance for student data
- **Research Data**: Version control and reproducibility tracking
- **Intellectual Property**: Protection of patent-pending research

## Technical Debt & Future Refactoring
- **Security Implementation**: Complete authentication and authorization system
- **Performance Optimization**: Caching, concurrent processing, load balancing
- **Local Model Integration**: Transition from APIs to on-premise LLMs
- **Advanced Features**: Real-time processing, sophisticated UI, system integrations

This document serves as the complete technical context for continuing development and making informed architectural decisions. 