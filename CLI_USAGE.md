# CLI Usage Guide - Milvus Vector Database

## Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_milvus.txt
   ```

2. **Start Milvus**:
   ```bash
   docker run -p 19530:19530 milvusdb/milvus:latest
   ```

## Quick Start

### Run All Examples
```bash
python cli_example.py
```
or
```bash
python cli_example.py --all
```

## Specific Examples

### 1. Setup Database and Collections
```bash
python cli_example.py --setup
```

### 2. Insert Sample Data
```bash
python cli_example.py --setup --insert
```

### 3. Run Search Examples
```bash
python cli_example.py --setup --insert --search
```

### 4. Show Database Statistics
```bash
python cli_example.py --setup --stats
```

### 5. Show Configuration Examples
```bash
python cli_example.py --config
```

## Individual Test Files

### Run Tests with pytest
```bash
# Run all database tests
pytest tests/test_milvus_database.py tests/test_pydantic_milvus.py -v

# Run basic database tests
pytest tests/test_milvus_database.py -v

# Run Pydantic tests
pytest tests/test_pydantic_milvus.py -v
```

### Run Examples
```bash
# Run comprehensive demo
python examples/demo_milvus_database.py

# Run initialization example
python examples/init_milvus_database.py

# Run test runner
python examples/run_tests.py
```

## Expected Output

When you run the CLI example, you'll see:

```
🎓 Milvus Vector Database CLI Usage Examples
============================================================

🔧 Setting up Milvus Vector Database...
✅ Database setup completed!

📝 Inserting sample data...
✅ Healthcare document inserted: 12345678...
✅ University document inserted: 87654321...

🔍 Search Examples:

1. Search by organization type (healthcare):
   Found 1 healthcare documents:
   - Advanced Cardiac Life Support Protocol

2. Search by security level (confidential):
   Found 1 confidential documents:
   - Advanced Cardiac Life Support Protocol

3. Search by department and role:
   Found 1 emergency medicine documents by attending physicians:
   - Advanced Cardiac Life Support Protocol

4. Vector similarity search:
   Found 2 similar documents:
   1. Advanced Cardiac Life Support Protocol (similarity: 0.856)
   2. Deep Learning Fundamentals Lecture (similarity: 0.743)

5. Hybrid search (vector + metadata filter):
   Found 1 similar healthcare documents:
   1. Advanced Cardiac Life Support Protocol (similarity: 0.856)

📊 Database Statistics:
   Organization Type: healthcare
   Default Security Level: internal
   Audit Logging: True
   Total Collections: 4
   Enabled Collections: 4

   Collection Statistics:
     documents: 2 entities
       - Enabled: True
       - Vector Dimensions: 1536
       - Content Types: ['document']
     images: 0 entities
       - Enabled: True
       - Vector Dimensions: 512
       - Content Types: ['image']
     audio_recordings: 0 entities
       - Enabled: True
       - Vector Dimensions: 768
       - Content Types: ['audio']
     video_content: 0 entities
       - Enabled: True
       - Vector Dimensions: 1024
       - Content Types: ['video']

⚙️  Configuration Examples:

1. Default Configuration:
   Organization Type: healthcare
   Default Security Level: internal
   Collections: ['documents', 'images', 'audio_recordings', 'video_content']

2. Custom Configuration for University:
   Organization Type: university
   Default Security Level: internal
   Enabled Collections: ['documents', 'video_content']

3. Configuration Export (for UI integration):
   Configuration exported with 7 keys
   Keys: ['host', 'port', 'collections', 'organization_type', 'default_security_level', 'enable_audit_logging', 'max_vector_dim']

🎉 All examples completed successfully!
```

## Troubleshooting

### Connection Issues
If you see connection errors:
```
❌ Failed to connect to Milvus!
Make sure Milvus is running: docker run -p 19530:19530 milvusdb/milvus:latest
```

1. Ensure Docker is running
2. Start Milvus container: `docker run -p 19530:19530 milvusdb/milvus:latest`
3. Wait a few seconds for Milvus to initialize
4. Try running the CLI example again

### Import Errors
If you see import errors:
```bash
pip install -r requirements_milvus.txt
```

Make sure all dependencies are installed, especially:
- pymilvus>=2.3.0
- pydantic>=2.0.0

## Features Demonstrated

✅ **Database Setup**: Connection and collection creation
✅ **Data Insertion**: Structured metadata with Pydantic models
✅ **Metadata Search**: Filter by organization, security, department, role
✅ **Vector Search**: Semantic similarity search
✅ **Hybrid Search**: Combined vector + metadata filtering
✅ **Statistics**: Collection and organization information
✅ **Configuration**: Default and custom configuration examples
✅ **UI Integration**: Configuration export/import for UI systems

## Files Structure

```
FimeHacks/
├── cli_example.py              # Main CLI example script
├── CLI_USAGE.md               # This file
├── requirements_milvus.txt    # Dependencies
├── src/
│   └── database/
│       ├── config.py          # Pydantic configuration models
│       ├── milvus_db.py       # Main database class
│       └── README.md          # Detailed documentation
├── tests/
│   ├── test_milvus_database.py # Basic database tests
│   ├── test_pydantic_milvus.py # Pydantic tests
│   └── README.md              # Test documentation
└── examples/
    ├── demo_milvus_database.py # Comprehensive demo
    ├── init_milvus_database.py # Initialization example
    ├── run_tests.py           # Test runner
    └── README.md              # Examples documentation
``` 