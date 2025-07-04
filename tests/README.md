# Tests Directory

This directory contains pytest-compatible test files for the SuperIntelligence AI System.

## Test Files

### File Processing Tests
- `test_file_processor.py` - Tests for file processor functionality
- `test_file_upload_service.py` - Tests for file upload service
- `test_text_workflow.py` - Tests for text workflow processing

### Milvus Database Tests
- `test_milvus_database.py` - Tests for basic Milvus database functionality
- `test_pydantic_milvus.py` - Tests for Pydantic-based Milvus database

## Running Tests

### All Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

### Specific Test Files
```bash
# Run file processing tests
pytest tests/test_file_processor.py -v

# Run database tests
pytest tests/test_milvus_database.py -v
pytest tests/test_pydantic_milvus.py -v
```

### Test Requirements

For Milvus database tests:
- Milvus server running: `docker run -p 19530:19530 milvusdb/milvus:latest`
- Additional dependencies: `pip install -r requirements_milvus.txt`

## Test Configuration

The tests use pytest fixtures and configuration from `conftest.py` and `pytest.ini`.

### Test Fixtures

- `db` - Database connection fixture
- `db_with_collections` - Database with collections created
- `healthcare_document` - Sample healthcare document for testing
- `university_document` - Sample university document for testing

### Test Skipping

Tests will automatically skip if required services are not available:
- Milvus database tests skip if Milvus server is not running
- File processing tests skip if dependencies are missing

## Running Tests in CI/CD

Tests can be run in continuous integration environments:

```bash
# Install test dependencies
pip install -r requirements.txt
pip install -r requirements_milvus.txt
pip install pytest pytest-cov

# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term
```

## Test Data

Test files use fixtures to create realistic test data:
- Healthcare documents with HIPAA compliance metadata
- University documents with FERPA compliance metadata
- Various file types and sizes for upload testing

## Contributing

When adding new tests:
1. Follow pytest naming conventions (`test_*.py`)
2. Use appropriate fixtures for setup/teardown
3. Include docstrings for test methods
4. Add proper assertions and error handling
5. Update this README with new test descriptions 