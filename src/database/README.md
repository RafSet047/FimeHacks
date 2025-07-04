# Pydantic-based Milvus Vector Database

A robust, configurable vector database system built on Milvus with Pydantic for structured metadata and configuration management.

## Key Features

### 🔧 **Structured Configuration**
- Pydantic-based configuration system
- UI-configurable settings
- Type-safe configuration validation
- Export/import configuration as JSON

### 📊 **Sophisticated Metadata**
- Structured metadata using Pydantic models
- Generic organizational metadata (supports healthcare, university, corporate)
- Role-based access control preparation
- Compliance framework support (HIPAA, FERPA, etc.)

### 🎯 **Multi-Modal Collections**
- **Documents**: Text documents, PDFs, reports, protocols (1536D vectors)
- **Images**: Medical images, diagrams, charts (512D vectors)
- **Audio**: Meeting transcripts, lectures, consultations (768D vectors)
- **Video**: Training materials, procedures, demonstrations (1024D vectors)

### 🔍 **Advanced Search**
- Vector similarity search
- Metadata filtering search
- Hybrid search (vector + metadata)
- Cross-collection search support

### 🏥 **Generic Organizational Support**
- Healthcare: doctors, nurses, patients, medical staff
- University: professors, students, researchers, TAs
- Corporate: employees, managers, teams, projects

## Quick Start

```python
from database.milvus_db import MilvusVectorDatabase
from database.config import get_default_database_config

# Create database with default configuration
db = MilvusVectorDatabase()

# Or with custom configuration
config = get_default_database_config()
config.organization_type = OrganizationTypeEnum.UNIVERSITY
db = MilvusVectorDatabase(config=config)

# Connect and create collections
db.connect()
db.create_all_collections()
```

## Configuration System

### Default Configuration
```python
# Get default configuration
config = get_default_database_config()

# Modify for your organization
config.organization_type = OrganizationTypeEnum.HEALTHCARE
config.default_security_level = SecurityLevelEnum.CONFIDENTIAL

# Enable/disable collections
config.collections["images"].enabled = False
```

### UI Integration
```python
# Export configuration for UI
config_dict = db.get_config_dict()

# Modify via UI and reimport
db.update_config(modified_config_dict)

# Or create new database from UI config
db2 = MilvusVectorDatabase.from_dict(config_dict)
```

## Structured Metadata

### Document Metadata Structure
```python
DocumentMetadata(
    organizational=OrganizationalMetadata(
        department="emergency_medicine",
        role="attending_physician",
        organization_type=OrganizationTypeEnum.HEALTHCARE,
        security_level=SecurityLevelEnum.CONFIDENTIAL,
        access_groups=["doctors", "nurses"]
    ),
    content=ContentMetadata(
        title="Emergency Protocol",
        author="Dr. Smith",
        content_type=ContentTypeEnum.DOCUMENT,
        tags=["emergency", "protocol"],
        keywords=["cardiac", "resuscitation"]
    ),
    processing=ProcessingMetadata(
        api_used="openai_gpt4",
        confidence_score=0.95,
        model_version="gpt-4-turbo"
    ),
    domain_specific=DomainSpecificMetadata(
        specialty="emergency_medicine",
        priority="critical",
        custom_fields={"medical_code": "ICD-10-I46.9"}
    ),
    compliance=ComplianceMetadata(
        compliance_frameworks=["HIPAA", "Joint_Commission"],
        approved_by="Chief Medical Officer",
        anonymized=True
    )
)
```

## Search Examples

### Metadata Search
```python
# Search by organization type
results = db.metadata_search(
    "documents",
    'organization_type == "healthcare"',
    limit=10
)

# Search by security level
results = db.metadata_search(
    "documents",
    'security_level == "confidential"',
    limit=10
)

# Search by department and role
results = db.metadata_search(
    "documents",
    'department == "emergency_medicine" and role == "attending_physician"',
    limit=10
)
```

### Vector Search
```python
# Semantic similarity search
query_vector = generate_embeddings("cardiac arrest protocol")
results = db.vector_search(
    "documents",
    query_vector,
    limit=5
)
```

### Hybrid Search
```python
# Vector search with metadata filtering
results = db.hybrid_search(
    "documents",
    query_vector,
    metadata_filter='security_level == "confidential"',
    limit=5
)
```

## Collection Information

### Agentic Descriptions
Each collection has AI-readable descriptions for intelligent query routing:

```python
info = db.get_collection_info("documents")
print(info['agentic_description'])
# {
#   "purpose": "Stores textual content including protocols, research papers...",
#   "best_for": "Procedural questions, policy lookups, research queries",
#   "typical_queries": ["What is the protocol for X?", "How do we handle Y?"],
#   "authority_level": "high"
# }
```

## Installation

```bash
pip install -r requirements_milvus.txt
```

## Usage

1. **Start Milvus**: `docker run -p 19530:19530 milvusdb/milvus:latest`
2. **Run tests**: `python src/database/test_milvus_db.py`
3. **Try demo**: `python src/database/init_milvus.py`

## Files

- `milvus_db.py` - Main database class
- `config.py` - Pydantic configuration models
- `test_milvus_db.py` - Test suite
- `init_milvus.py` - Demo script
- `requirements_milvus.txt` - Dependencies

## Benefits

✅ **Type Safety**: Pydantic ensures data validation
✅ **UI Integration**: Easy configuration export/import
✅ **Generic Design**: Works for healthcare, university, corporate
✅ **Scalable**: Handles millions of vectors
✅ **Compliance Ready**: HIPAA, FERPA metadata structure
✅ **AI-Native**: Agentic descriptions for intelligent routing 