#!/usr/bin/env python3
"""
Standalone File Upload Test Script

Usage:
    python examples/test_file_upload.py [file_path]

Examples:
    python examples/test_file_upload.py                    # Creates and uploads test.txt
    python examples/test_file_upload.py myfile.pdf        # Uploads myfile.pdf
    python examples/test_file_upload.py docs/report.docx  # Uploads docs/report.docx
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import asyncio
import tempfile
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.file_upload import FileUploadService
from database.connection import init_db, SessionLocal
from config.settings import settings
from fastapi import UploadFile
from io import BytesIO


class MockUploadFile:
    """Mock UploadFile for testing purposes"""
    
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.content = content
        self.size = len(content)
        self.content_type = "application/octet-stream"
    
    async def read(self) -> bytes:
        return self.content
    
    async def seek(self, offset: int):
        pass
    
    async def close(self):
        pass


def create_test_file() -> tuple[str, bytes]:
    """Create a simple test file"""
    content = """# Test File for File Upload Service

This is a test file created automatically by the file upload test script.

File Information:
- Created for testing purposes
- Contains sample text content
- Should be processed by the file upload service

Test Data:
- Department: Engineering
- Project: File Upload Testing
- Tags: test, automation, sample

Content:
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

End of test file.
"""
    
    filename = "test_file.txt"
    return filename, content.encode('utf-8')


async def test_file_upload(file_path: str = None):
    """Test file upload functionality"""
    
    print("🚀 Starting File Upload Test")
    print("=" * 50)
    
    # Initialize database
    print("📋 Initializing database...")
    init_db()
    
    # Create upload service
    upload_service = FileUploadService()
    
    # Prepare file for upload
    if file_path and os.path.exists(file_path):
        # Use provided file
        print(f"📁 Using provided file: {file_path}")
        filename = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            content = f.read()
    else:
        # Create test file
        if file_path:
            print(f"⚠️  File not found: {file_path}")
            print("📝 Creating test file instead...")
        else:
            print("📝 No file provided, creating test file...")
        
        filename, content = create_test_file()
    
    # Create mock upload file
    mock_file = MockUploadFile(filename, content)
    
    print(f"📄 File: {filename}")
    print(f"📊 Size: {len(content):,} bytes")
    print(f"🏷️  Type: {mock_file.content_type}")
    
    # Test upload
    print("\n🔄 Starting upload process...")
    
    try:
        with SessionLocal() as db:
            result = await upload_service.upload_file(
                file=mock_file,
                db=db,
                department="Engineering",
                project="File Upload Testing",
                tags=["test", "automation", "example"]
            )
        
        print("✅ Upload successful!")
        print("\n📋 Upload Results:")
        print(f"   File ID: {result['file_id']}")
        print(f"   Original Name: {result['original_filename']}")
        print(f"   Storage Path: {result['storage_path']}")
        print(f"   File Size: {result['file_size']:,} bytes")
        print(f"   File Type: {result['file_type']}")
        print(f"   MIME Type: {result['mime_type']}")
        print(f"   Hash: {result['file_hash'][:16]}...")
        print(f"   Department: {result['department']}")
        print(f"   Project: {result['project']}")
        print(f"   Tags: {', '.join(result['tags'])}")
        
        # Show storage location
        storage_path = Path(result['storage_path'])
        print(f"\n📂 File stored at: {storage_path.absolute()}")
        
        if storage_path.exists():
            print("✅ File confirmed in storage!")
            print(f"   Actual size: {storage_path.stat().st_size:,} bytes")
        else:
            print("❌ File not found in storage!")
        
        # Show directory structure
        print(f"\n🗂️  Storage directory structure:")
        storage_base = Path(settings.storage_path)
        if storage_base.exists():
            for root, dirs, files in os.walk(storage_base):
                level = root.replace(str(storage_base), '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main function"""
    file_path = None
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    # Run the async test
    try:
        success = asyncio.run(test_file_upload(file_path))
        if success:
            print("\n🎉 Test completed successfully!")
            print("\nTo view your uploaded files, check the storage directory:")
            print(f"   {Path(settings.storage_path).absolute()}")
        else:
            print("\n💥 Test failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 