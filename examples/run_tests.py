#!/usr/bin/env python3

import subprocess
import sys
import os

def run_tests():
    """Run the Milvus database tests"""
    
    test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests")
    
    print("🧪 Running Milvus Database Tests")
    print("=" * 40)
    
    # Test files to run
    test_files = [
        "test_milvus_database.py",
        "test_pydantic_milvus.py"
    ]
    
    for test_file in test_files:
        test_path = os.path.join(test_dir, test_file)
        
        if os.path.exists(test_path):
            print(f"\n🔍 Running {test_file}...")
            print("-" * 30)
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
                
                if result.returncode == 0:
                    print(f"✅ {test_file} passed!")
                else:
                    print(f"❌ {test_file} failed!")
                    
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
        else:
            print(f"❌ Test file not found: {test_path}")
    
    print("\n" + "=" * 40)
    print("🏁 Test run complete!")

if __name__ == "__main__":
    run_tests() 