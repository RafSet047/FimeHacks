# End-to-End Workflow Usage Examples

The `demo_end_to_end_workflow.py` now supports multiple commands for different operations.

## Prerequisites

Set your Google API key:
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

## Available Commands

### 1. Demo Command
Run a complete demonstration with a sample document:

```bash
python demo_end_to_end_workflow.py demo
```

This will:
- Create a sample healthcare document
- Process it through the complete pipeline
- Store chunks in Milvus
- Run similarity search
- Show stored documents
- Clean up the sample file

### 2. Add Command
Add a document to the collection:

```bash
# Add a text file
python demo_end_to_end_workflow.py add document.txt

# Add a PDF with custom filename
python demo_end_to_end_workflow.py add report.pdf --filename "quarterly_report.pdf"

# Use a different collection
python demo_end_to_end_workflow.py add document.txt --collection documents
```

### 3. Read Command
Read and display stored documents:

```bash
# Show first 10 documents
python demo_end_to_end_workflow.py read

# Show first 5 documents
python demo_end_to_end_workflow.py read --limit 5

# Read from specific collection
python demo_end_to_end_workflow.py read --collection documents --limit 20
```

### 4. Query Command
Search for similar content:

```bash
# Basic similarity search
python demo_end_to_end_workflow.py query "healthcare quality improvement"

# Get more results
python demo_end_to_end_workflow.py query "patient safety protocols" --limit 10

# Search in specific collection
python demo_end_to_end_workflow.py query "research methods" --collection documents
```

## Global Options

All commands support these global options:

- `--api-key`: Provide Google API key directly (instead of environment variable)
- `--collection`: Specify Milvus collection name (default: text_embeddings)

## Example Workflow

```bash
# 1. Run demo to set up initial data
python demo_end_to_end_workflow.py demo

# 2. Add your own documents
python demo_end_to_end_workflow.py add my_document.pdf
python demo_end_to_end_workflow.py add research_paper.txt

# 3. View all stored documents
python demo_end_to_end_workflow.py read --limit 20

# 4. Search for specific content
python demo_end_to_end_workflow.py query "implementation guidelines"
python demo_end_to_end_workflow.py query "quality metrics" --limit 3
```

## Output Examples

### Add Command Output
```
End-to-End Document Processing Workflow - ADD
============================================
Processing file: healthcare_protocol.txt

Stage 1: Uploading file healthcare_protocol.txt
Stage 2: Extracting text from healthcare_protocol.txt
Stage 3: Chunking extracted text
Stage 4: Processing 4 chunks through embeddings and storage

Success! Processed 4 chunks
Generated 4 embeddings
Stored 4 documents in Milvus
```

### Read Command Output
```
STORED DOCUMENTS
================================================================================
Collection: text_embeddings
Total Documents in Collection: 12
Showing: 5 documents

1. Document ID: 550e8400-e29b-41d4-a716-446655440001
   Department: demo
   Content Type: document
   Role: staff
   Security Level: internal
   Title: Processed Document
   Author: demo_user
   Tags: demo, end-to-end, workflow
   Chunk Index: 0
   Content Preview: Healthcare Quality Improvement Protocol This document outlines the standard procedures...
```

### Query Command Output
```
SIMILARITY SEARCH RESULTS
================================================================================
Query: healthcare quality improvement
Results Found: 3

1. Similarity Score: 0.8945
   Document ID: 550e8400-e29b-41d4-a716-446655440001
   Department: demo
   Content Type: document
   Chunk Index: 0
   Preview: Healthcare Quality Improvement Protocol This document outlines...

2. Similarity Score: 0.8234
   Document ID: 550e8400-e29b-41d4-a716-446655440003
   Department: demo
   Content Type: document
   Chunk Index: 2
   Preview: Key Components: 1. Assessment of current practices...
```

## Error Handling

The workflow handles various error scenarios gracefully:

- **Missing file**: `Error: File 'nonexistent.txt' not found!`
- **No API key**: `ERROR: Google API key not found!`
- **Empty collection**: `No documents found in collection 'text_embeddings'`
- **No search results**: `No similar content found.`

## Tips

1. **Start with demo**: Always run `demo` first to verify everything works
2. **Use specific queries**: More specific search terms give better results
3. **Monitor collection size**: Use `read --limit 1` to check if documents are being stored
4. **Different collections**: Use different collections for different document types
5. **File formats**: Supports .txt, .pdf, .docx, .csv, .xlsx, .pptx, .mp3 files 