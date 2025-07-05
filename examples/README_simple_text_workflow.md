# Simple Text Processing Workflow Demo

This example demonstrates the basic workflow for processing text files through the complete pipeline:

1. **File Upload** - Upload a text file to the system
2. **Text Extraction** - Extract text content from the file
3. **Text Chunking** - Split the text into smaller, manageable chunks

## Features

- Simple, focused workflow for basic text files
- Automatic sample file creation for testing
- Clear output showing each step's results
- Proper error handling and cleanup

## Requirements

- Python 3.7+
- FastAPI
- SQLAlchemy
- Required dependencies from `requirements.txt`

## Usage

### Quick Start

```bash
# Run the demo
python examples/demo_simple_text_workflow.py
```

### What It Does

1. **Creates a sample text file** with demonstration content
2. **Uploads the file** using the file upload service
3. **Extracts text** using the document extractor
4. **Chunks the text** using the text chunking service
5. **Displays results** showing:
   - Upload success and file metadata
   - Extracted text length and preview
   - Chunk details including sizes and positions

### Example Output

```
Simple Text Processing Workflow Demo
====================================
Created sample file: /tmp/tmpXXXXXX.txt

============================================================
SIMPLE TEXT WORKFLOW RESULTS
============================================================

1. UPLOAD RESULTS:
   Success: True
   File ID: abc123
   Filename: demo_sample.txt
   File Size: 1024 bytes

2. TEXT EXTRACTION:
   Extracted Characters: 1024
   Sample Text (first 200 chars):
   This is a sample text file for demonstrating the simple text workflow.

The workflow consists of three main steps:
1. Upload the file to the system
2. Extract text content...

3. TEXT CHUNKING:
   Total Chunks: 3
   Chunk Details:
   Chunk 1:
     Length: 500 characters
     Start Index: 0
     End Index: 500
     Preview: This is a sample text file for demonstrating the simple text workflow.

The workflow consists...

   Chunk 2:
     Length: 450 characters
     Start Index: 450
     End Index: 900
     Preview: ...making the chunks more coherent and meaningful for downstream processing...

   Chunk 3:
     Length: 124 characters
     Start Index: 850
     End Index: 974
     Preview: Finally, each chunk includes metadata about its position in the original text...

============================================================

Workflow completed successfully!
Cleaned up sample file: /tmp/tmpXXXXXX.txt
```

## Configuration

The example uses these chunking settings:
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters
- **Strategy**: Recursive (splits on natural boundaries)
- **Add Start Index**: True (tracks position in original text)

You can modify these settings in the `_chunk_text` method of the `SimpleTextWorkflow` class.

## Supported File Types

This example focuses on basic text files:
- `.txt` - Plain text files
- `.md` - Markdown files
- `.html` - HTML files
- `.json` - JSON files

## Error Handling

The workflow includes proper error handling:
- Upload failures are logged and reported
- Text extraction errors fall back to basic processing
- Chunking errors are caught and logged
- Temporary files are always cleaned up

## Extending the Example

To extend this example:

1. **Add more file types**: Modify `_get_mime_type` and test with PDFs, DOCX, etc.
2. **Custom chunking**: Adjust `ChunkingConfig` parameters
3. **Database integration**: Add actual file storage and retrieval
4. **Batch processing**: Process multiple files at once

## Related Files

- `src/services/file_upload.py` - File upload service
- `src/services/document_extractor.py` - Text extraction service
- `src/services/text_chunking.py` - Text chunking service
- `src/database/connection.py` - Database connection management

## Troubleshooting

If you encounter issues:

1. **Import errors**: Ensure all dependencies are installed
2. **Database errors**: Check that the database is initialized
3. **File permission errors**: Ensure write permissions for temporary files
4. **LangChain errors**: The chunking service will fall back to basic chunking if LangChain is not available 