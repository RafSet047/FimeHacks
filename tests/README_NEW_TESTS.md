# New Tests for Document Extraction & Google API Services

This directory contains comprehensive tests for the newly implemented document extraction and Google API services.

## 🧪 Test Files Overview

### `test_document_extractor.py`
Tests for the document text extraction service that handles PDF, DOC, DOCX, and plain text files.

**What it tests:**
- PDF text extraction (langchain + PyPDF2 fallbacks)
- DOCX text extraction (langchain + python-docx fallbacks)
- DOC text extraction (langchain with unstructured)
- Plain text file handling
- Document chunking and metadata extraction
- Error handling and fallback mechanisms

**Key test scenarios:**
- Healthcare document processing (medical protocols)
- University document processing (syllabi, lectures)
- Mixed format batch processing
- Library availability fallbacks

### `test_google_service.py`
Tests for the Google API service that handles text embeddings and audio transcription.

**What it tests:**
- API key retrieval from environment variables
- Text embedding generation with proper dimensions
- Audio transcription with speaker diarization
- Rate limiting and error handling
- Async operations
- Service status and health checks

**Key test scenarios:**
- Single and multi-chunk text embedding
- Audio transcription with speaker identification
- API error handling and fallbacks
- Performance and scaling considerations

### `test_integration_document_google.py`
Integration tests that combine document extraction with Google API services.

**What it tests:**
- Complete pipeline: Document → Text → Embeddings
- Complete pipeline: Audio → Transcription → Embeddings
- Multi-modal workflows (documents + audio)
- Error handling across the full pipeline
- Performance with large documents

**Key test scenarios:**
- Healthcare multimodal workflow (protocols + emergency calls)
- University multimodal workflow (slides + lecture recordings)
- Error propagation and fallback chains

## 🚀 Running the Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements_test.txt
```

Set up environment variable for testing:
```bash
export GOOGLE_API_KEY="your_test_api_key_here"
# or
export GOOGLE_GENERATIVE_AI_API_KEY="your_test_api_key_here"
```

### Running All New Tests

Use the test runner script:
```bash
python tests/run_new_tests.py
```

### Running Specific Test Files

```bash
# Run document extractor tests
python tests/run_new_tests.py --test test_document_extractor.py

# Run Google service tests
python tests/run_new_tests.py --test test_google_service.py

# Run integration tests
python tests/run_new_tests.py --test test_integration_document_google.py
```

### Running with Coverage

```bash
python tests/run_new_tests.py --coverage
```

This generates:
- Terminal coverage report
- HTML coverage report at `tests/htmlcov/index.html`

### Running Individual Test Methods

```bash
# Run specific test class
pytest tests/test_document_extractor.py::TestPDFExtractor -v

# Run specific test method
pytest tests/test_google_service.py::TestTextEmbeddingGeneration::test_generate_text_embeddings_single_chunk -v
```

## 🎯 Test Features

### Comprehensive Mocking
- **No Real API Calls**: All Google API calls are mocked
- **File System Mocking**: Document operations use mock file systems
- **Library Availability Testing**: Tests fallback behavior when libraries are unavailable

### Error Scenario Testing
- API failures and timeouts
- File corruption and read errors
- Missing dependencies
- Invalid configurations

### Performance Testing
- Large document handling
- Rate limiting behavior
- Memory usage patterns
- Concurrent operation support

### Integration Testing
- End-to-end pipeline validation
- Multi-modal content processing
- Healthcare and university specific workflows
- Data consistency across transformations

## 📊 Expected Test Results

When all tests pass, you should see:

```
🧪 Running new document extraction and Google API tests...
============================================================

📋 Running test_document_extractor.py...
----------------------------------------
✅ test_document_extractor.py - All tests passed!

📋 Running test_google_service.py...
----------------------------------------
✅ test_google_service.py - All tests passed!

📋 Running test_integration_document_google.py...
----------------------------------------
✅ test_integration_document_google.py - All tests passed!

============================================================
📊 TEST SUMMARY:
   ✅ Passed: 3 test files
   ❌ Failed: 0 test files
🎉 All new tests passed successfully!
```

## 🔧 Test Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Primary Google API key
- `GOOGLE_GENERATIVE_AI_API_KEY`: Alternative API key name
- Tests work with mock keys - real API calls are not made

### Mock Behavior
- **Document Extraction**: Mocks file reading and library calls
- **Google APIs**: Mocks all external API requests
- **Audio Processing**: Mocks audio file conversion and processing
- **Database Operations**: Tests use in-memory mock databases

## 🐛 Debugging Test Failures

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Missing Dependencies**: Install test requirements
3. **API Key Warnings**: Set environment variables (can be dummy values)
4. **Path Issues**: Run tests from project root directory

### Verbose Output
```bash
pytest tests/test_document_extractor.py -v -s --tb=long
```

### Debug Specific Test
```bash
pytest tests/test_google_service.py::TestTextEmbeddingGeneration::test_generate_text_embeddings_single_chunk -v -s --pdb
```

## 📈 Coverage Goals

Target coverage levels:
- **Document Extractor**: >90% line coverage
- **Google Service**: >90% line coverage
- **Integration Scenarios**: >80% line coverage

Current coverage can be viewed in the HTML report after running with `--coverage` flag.

## 🔄 Continuous Integration

These tests are designed to run in CI/CD environments:
- No external dependencies
- Deterministic results
- Fast execution (all mocked)
- Clear failure reporting

Add to your CI pipeline:
```yaml
- name: Run New Service Tests
  run: python tests/run_new_tests.py --coverage
```

## 📝 Adding New Tests

When adding new functionality:

1. **Unit Tests**: Add to appropriate test file
2. **Integration Tests**: Add to integration test file
3. **Mock Dependencies**: Follow existing mocking patterns
4. **Error Scenarios**: Include failure case testing
5. **Documentation**: Update this README

Follow the established patterns for test organization and naming conventions. 