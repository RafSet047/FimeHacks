#!/usr/bin/env python3
"""
Test runner for new document extraction and Google API service tests
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all new tests"""
    
    test_files = [
        "test_document_extractor.py",
        "test_google_service.py", 
        "test_integration_document_google.py"
    ]
    
    print("🧪 Running new document extraction and Google API tests...")
    print("=" * 60)
    
    # Set environment variables for testing
    os.environ['GOOGLE_API_KEY'] = 'test_api_key_for_mocking'
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file}...")
        print("-" * 40)
        
        try:
            # Run pytest for each test file
            result = subprocess.run([
                sys.executable, 
                "-m", 
                "pytest", 
                test_file,
                "-v",  # verbose output
                "--tb=short",  # short traceback format
                "--color=yes"  # colored output
            ], 
            cwd=Path(__file__).parent,
            capture_output=False
            )
            
            if result.returncode == 0:
                print(f"✅ {test_file} - All tests passed!")
                total_passed += 1
            else:
                print(f"❌ {test_file} - Some tests failed!")
                total_failed += 1
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            total_failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY:")
    print(f"   ✅ Passed: {total_passed} test files")
    print(f"   ❌ Failed: {total_failed} test files")
    
    if total_failed == 0:
        print("🎉 All new tests passed successfully!")
        return True
    else:
        print("⚠️  Some tests failed. Check output above for details.")
        return False


def run_coverage():
    """Run tests with coverage report"""
    print("\n📊 Running tests with coverage...")
    print("=" * 60)
    
    test_files = [
        "test_document_extractor.py",
        "test_google_service.py", 
        "test_integration_document_google.py"
    ]
    
    try:
        result = subprocess.run([
            sys.executable, 
            "-m", 
            "pytest",
            "--cov=src.services.document_extractor",
            "--cov=src.services.external_apis.google_service",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "-v"
        ] + test_files,
        cwd=Path(__file__).parent,
        capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✅ Coverage report generated!")
            print("📂 HTML report available at: tests/htmlcov/index.html")
        else:
            print("\n❌ Coverage report generation failed!")
            
    except Exception as e:
        print(f"❌ Error generating coverage: {e}")


def run_specific_test(test_name: str):
    """Run a specific test file or test function"""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable,
            "-m",
            "pytest", 
            test_name,
            "-v",
            "--tb=long",
            "--color=yes"
        ],
        cwd=Path(__file__).parent,
        capture_output=False
        )
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running {test_name}: {e}")
        return False


def main():
    """Main function with command line argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run new document extraction and Google API tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--test", type=str, help="Run specific test file or function")
    parser.add_argument("--list", action="store_true", help="List available test files")
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 Available test files:")
        print("  - test_document_extractor.py")
        print("  - test_google_service.py")
        print("  - test_integration_document_google.py")
        return
    
    if args.test:
        success = run_specific_test(args.test)
        sys.exit(0 if success else 1)
    
    if args.coverage:
        run_coverage()
    else:
        success = run_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 