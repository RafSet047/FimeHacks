# Examples Directory

This directory contains standalone scripts for testing individual components of the SuperIntelligence AI System.

## File Upload Test Script

### Usage

```bash
# Test with auto-generated file
python examples/test_file_upload.py

# Test with your own file
python examples/test_file_upload.py path/to/your/file.txt

# Test with sample file
python examples/test_file_upload.py examples/sample_document.txt
```

### What it does

- Tests the complete file upload workflow
- Validates file types and sizes
- Stores files in organized directory structure
- Creates database records with metadata
- Shows detailed upload results
- Displays storage directory structure

### Output

The script will show:
- Upload progress and status
- File metadata (ID, size, type, hash)
- Storage location path
- Directory structure visualization
- Success/failure confirmation

### Requirements

- Run from project root directory
- Database will be automatically initialized
- Storage directory will be created if needed

### Example Output

```
🚀 Starting File Upload Test
==================================================
📋 Initializing database...
📝 No file provided, creating test file...
📄 File: test_file.txt
📊 Size: 891 bytes
🏷️  Type: application/octet-stream

🔄 Starting upload process...
✅ Upload successful!

📋 Upload Results:
   File ID: 123e4567-e89b-12d3-a456-426614174000
   Original Name: test_file.txt
   Storage Path: ./storage/2025/01/15/123e4567-e89b-12d3-a456-426614174000.txt
   File Size: 891 bytes
   File Type: text file
   MIME Type: text/plain
   Hash: a1b2c3d4e5f6g7h8...
   Department: Engineering
   Project: File Upload Testing
   Tags: test, automation, example

📂 File stored at: /absolute/path/to/storage/2025/01/15/123e4567-e89b-12d3-a456-426614174000.txt
✅ File confirmed in storage!
   Actual size: 891 bytes

🗂️  Storage directory structure:
storage/
  2025/
    01/
      15/
        123e4567-e89b-12d3-a456-426614174000.txt

🎉 Test completed successfully!
```

## Adding More Test Scripts

To add more standalone test scripts:

1. Create new Python files in this directory
2. Add proper import path setup: `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))`
3. Import necessary modules from the `src` directory
4. Create main function with command-line argument parsing
5. Document usage in this README 