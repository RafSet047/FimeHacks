# End-to-End Document Processing Workflow

This demo shows how to connect the individual workflow components into a complete document processing pipeline that handles files from upload to searchable vector storage.

## Overview

The `demo_end_to_end_workflow.py` bridges the gap between:
- **File Upload & Processing** (`demo_simple_text_workflow.py`)
- **Embedding Generation & Vector Storage** (`demo_google_milvus_workflow.py`)

## What It Does

### Complete Pipeline
1. **File Upload** → Upload and validate file
2. **Text Extraction** → Extract text from various file formats
3. **Text Chunking** → Split text into manageable chunks
4. **Embedding Generation** → Generate vector embeddings for each chunk
5. **Vector Storage** → Store embeddings in Milvus with structured metadata
6. **Similarity Search** → Search for similar content using embeddings

### Key Features
- **Metadata Alignment**: Converts between different metadata structures
- **Batch Processing**: Handles multiple chunks efficiently
- **Error Resilience**: Continues processing even if individual chunks fail
- **Performance Monitoring**: Tracks processing time and success rates
- **Search Integration**: Enables similarity search across processed content
- **Command-Line Interface**: Four commands for different operations

## Prerequisites

### 1. Google API Key
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

### 2. Milvus Database
The demo uses Milvus Lite (embedded) by default, but you can also use a standalone Milvus server.

### 3. Python Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Interface

The workflow now supports four main commands:

#### 1. Demo Command (Recommended Start)
```bash
python demo_end_to_end_workflow.py demo
```
Runs a complete demonstration with sample data.

#### 2. Add Command
```bash
python demo_end_to_end_workflow.py add your_document.pdf
python demo_end_to_end_workflow.py add document.txt --filename "custom_name.txt"
```
Adds documents to the collection.

#### 3. Read Command
```bash
python demo_end_to_end_workflow.py read
python demo_end_to_end_workflow.py read --limit 5
```
Displays stored documents from the collection.

#### 4. Query Command
```bash
python demo_end_to_end_workflow.py query "your search text"
python demo_end_to_end_workflow.py query "healthcare protocols" --limit 10
```
Searches for similar content using vector embeddings.

### Global Options
- `--api-key`: Provide Google API key directly
- `--collection`: Specify collection name (default: text_embeddings)

### Help
```bash
python demo_end_to_end_workflow.py --help
python demo_end_to_end_workflow.py add --help
python demo_end_to_end_workflow.py query --help
```

## Quick Start

1. **Run the demo first**:
   ```bash
   python demo_end_to_end_workflow.py demo
   ```

2. **Add your own documents**:
   ```bash
   python demo_end_to_end_workflow.py add my_document.pdf
   ```

3. **Search for content**:
   ```bash
   python demo_end_to_end_workflow.py query "quality improvement"
   ```

4. **View stored documents**:
   ```bash
   python demo_end_to_end_workflow.py read --limit 10
   ```

## Architecture

### Data Flow
```
File (PDF/TXT/DOCX) 
    ↓
Upload Service (FileMetadata)
    ↓
Document Extractor (Raw Text)
    ↓
Text Chunker (List[Document])
    ↓
Google Service (List[List[float]])
    ↓
Metadata Converter (DocumentMetadata)
    ↓
Milvus Database (Vector Storage)
    ↓
Similarity Search (Results)
```

### Key Components

#### MetadataConverter
Converts between different metadata structures:
- `FileMetadata` (from file upload) → `DocumentMetadata` (for Milvus)
- Preserves important information like department, role, tags
- Adds chunk-specific information (index, text preview)

#### EndToEndWorkflow
Orchestrates the complete pipeline:
- Handles each processing stage
- Manages error recovery
- Provides comprehensive result tracking
- Enables similarity search

## Sample Output

### Add Command
```
End-to-End Document Processing Workflow - ADD
============================================
Processing file: healthcare_protocol.txt

Success! Processed 4 chunks
Generated 4 embeddings
Stored 4 documents in Milvus
```

### Read Command
```
STORED DOCUMENTS
================================================================================
Collection: text_embeddings
Total Documents in Collection: 12
Showing: 5 documents

1. Document ID: 550e8400-e29b-41d4-a716-446655440001
   Department: demo
   Content Type: document
   Title: Processed Document
   Content Preview: Healthcare Quality Improvement Protocol...
```

### Query Command
```
SIMILARITY SEARCH RESULTS
================================================================================
Query: healthcare quality improvement
Results Found: 3

1. Similarity Score: 0.8945
   Document ID: 550e8400-e29b-41d4-a716-446655440001
   Preview: Healthcare Quality Improvement Protocol...
```

## Configuration

### Collection Settings
- **Collection Name**: `text_embeddings`
- **Vector Dimension**: 1536 (Google's text-embedding-004)
- **Metric Type**: COSINE similarity
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters

### Metadata Structure
Each stored chunk includes:
- **Organizational**: Department, role, security level
- **Content**: Title, author, tags, format
- **Processing**: API used, confidence score, processing time
- **Domain-specific**: Chunk index, text preview, position indices
- **Compliance**: Anonymization status, approval info

## Error Handling

The workflow handles various failure scenarios:
- **Upload failures**: File validation, storage issues
- **Extraction failures**: Unsupported formats, corrupted files
- **Chunking failures**: Text processing errors
- **Embedding failures**: API limits, network issues
- **Storage failures**: Milvus connection, insertion errors

Processing continues even if individual chunks fail, with detailed error reporting.

## Supported File Formats

- **Text**: .txt, .md, .html, .json
- **Documents**: .pdf, .docx, .doc
- **Spreadsheets**: .csv, .xlsx
- **Presentations**: .pptx
- **Audio**: .mp3, .wav, .m4a, .flac, .ogg

## Performance Considerations

### Optimization Tips
- **Batch Processing**: Process multiple chunks in parallel
- **Chunk Size**: Balance between context and processing speed
- **Index Configuration**: Optimize Milvus index for your use case
- **Caching**: Cache embeddings for repeated content

### Monitoring
- Processing time per chunk
- Embedding generation success rate
- Milvus storage success rate
- Memory usage during processing

## Troubleshooting

### Common Issues

1. **Google API Key Not Found**
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   ```

2. **Milvus Connection Failed**
   - Check if Milvus is running
   - Verify connection settings
   - Try Milvus Lite (embedded) mode

3. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

4. **Memory Issues with Large Files**
   - Reduce chunk size
   - Process files in smaller batches
   - Monitor memory usage

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration Examples

### Automated Processing
```bash
# Process multiple files
for file in *.pdf; do
    python demo_end_to_end_workflow.py add "$file"
done

# Search and save results
python demo_end_to_end_workflow.py query "research methodology" > search_results.txt
```

### Custom Workflow
```python
workflow = EndToEndWorkflow(google_api_key="your-key")

# Process your document
results = await workflow.process_file_end_to_end(
    file_path="your_document.pdf",
    filename="custom_document.pdf"
)

# Search similar content
search_results = await workflow.search_similar_content(
    query_text="your search query",
    limit=10
)
```

## Next Steps

1. **Customize Metadata**: Adapt metadata conversion for your domain
2. **Add File Types**: Extend support for additional file formats
3. **Optimize Performance**: Fine-tune chunk sizes and processing
4. **Add UI**: Create web interface for document upload and search
5. **Scale Processing**: Implement distributed processing for large volumes

## Related Files

- `demo_simple_text_workflow.py` - Basic file processing
- `demo_google_milvus_workflow.py` - Text embeddings and storage
- `WORKFLOW_ALIGNMENT_GUIDE.md` - Technical implementation details
- `USAGE_EXAMPLES.md` - Detailed command examples and output
- `demo_end_to_end_workflow.py` - Complete pipeline implementation 