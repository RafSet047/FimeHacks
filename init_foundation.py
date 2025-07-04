#!/usr/bin/env python3
"""
Foundation initialization and validation script for SuperIntelligence AI System
This script validates that Phase 1 foundation setup is working correctly.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🚀 SuperIntelligence AI System - Foundation Validation")
    print("=" * 60)
    
    try:
        # Test 1: Configuration loading
        print("\n1. Testing configuration loading...")
        from src.config.settings import settings
        print(f"   ✅ Settings loaded successfully")
        print(f"   - App Name: {settings.app_name}")
        print(f"   - Database URL: {settings.database_url}")
        print(f"   - Storage Path: {settings.storage_path}")
        
        # Test 2: Directory creation
        print("\n2. Creating required directories...")
        settings.create_directories()
        print(f"   ✅ Storage directory created: {settings.storage_path}")
        print(f"   ✅ Log directory created: {os.path.dirname(settings.log_file)}")
        print(f"   ✅ ChromaDB directory created: {settings.chroma_persist_directory}")
        
        # Test 3: Database connection
        print("\n3. Testing database connection...")
        from src.database.connection import init_db
        init_db()
        print("   ✅ Database initialized successfully")
        
        # Test 4: Model imports
        print("\n4. Testing model imports...")
        from src.models import File, Content, SearchIndex
        print("   ✅ All models imported successfully")
        
        # Test 5: CRUD operations
        print("\n5. Testing CRUD operations...")
        from src.database.connection import get_db
        from src.database.crud import file_crud
        
        # Create a test file record
        db = next(get_db())
        test_file_data = {
            "filename": "test_file.txt",
            "original_filename": "test_file.txt",
            "file_path": "/tmp/test_file.txt",
            "file_size": 1024,
            "file_type": "txt",
            "mime_type": "text/plain"
        }
        
        test_file = file_crud.create_file(db, test_file_data)
        print(f"   ✅ Test file created: {test_file.filename}")
        
        # Retrieve the file
        retrieved_file = file_crud.get_file_by_id(db, test_file.file_id)
        print(f"   ✅ Test file retrieved: {retrieved_file.filename}")
        
        # Clean up test file
        file_crud.delete_file(db, test_file.file_id)
        print("   ✅ Test file deleted successfully")
        
        db.close()
        
        # Test 6: Logging system
        print("\n6. Testing logging system...")
        from src.utils.logging import logger
        logger.info("Foundation validation test log entry")
        print("   ✅ Logging system working")
        
        print("\n🎉 Foundation validation completed successfully!")
        print("✅ All Phase 1 components are working correctly")
        print("\nNext steps:")
        print("- Run 'python src/main.py' to start the FastAPI server")
        print("- Visit http://localhost:8000 to see the API")
        print("- Visit http://localhost:8000/docs for API documentation")
        
    except Exception as e:
        print(f"\n❌ Foundation validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 