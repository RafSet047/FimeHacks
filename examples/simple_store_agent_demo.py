#!/usr/bin/env python3
"""
Simple demonstration of StoreAgent analyzing content and generating tags
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.store_agent import StoreAgent

def main():
    """Simple demo of StoreAgent content analysis functionality"""
    
    print("Simple StoreAgent Content Analysis Demo")
    print("=" * 50)
    
    # Initialize StoreAgent (no database dependencies)
    print("Initializing StoreAgent...")
    store_agent = StoreAgent(
        name="ContentAnalyzer",
        description="Analyzes content and generates tags"
    )
    
    print("✅ StoreAgent initialized successfully")
    print(f"Available tags: {store_agent.available_tags}")
    
    # Test with sample content
    test_contents = [
        "This is a research paper about machine learning algorithms in healthcare applications.",
        "Student registration form for Fall 2024 semester including course selection and payment information.",
        "Faculty meeting minutes discussing curriculum changes and administrative policies.",
        "Patient medical records showing blood test results and diagnostic imaging reports.",
        "University budget report for the academic year with financial projections."
    ]
    
    print(f"\nAnalyzing {len(test_contents)} sample texts...")
    print("-" * 60)
    
    for i, text in enumerate(test_contents, 1):
        print(f"\n--- Test {i} ---")
        print(f"Text: {text}")
        
        # Analyze content
        tags = store_agent.analyze_content(text)
        
        print(f"Generated Tags: {tags}")
        print(f"Number of tags: {len(tags)}")
        
        # Display agent status
        status = store_agent.get_status()
        print(f"Agent Status: {'Active' if status['is_active'] else 'Inactive'}")
        print(f"Error Count: {status['error_count']}")
    
    # Test with empty/invalid content
    print(f"\n--- Edge Cases ---")
    
    edge_cases = [
        "",  # Empty string
        "   ",  # Whitespace only
        "a",  # Very short text
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit." * 10  # Long text
    ]
    
    for i, text in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        tags = store_agent.analyze_content(text)
        print(f"Generated Tags: {tags}")
    
    # Display final agent status
    final_status = store_agent.get_status()
    print(f"\n--- Final Agent Status ---")
    print(f"Name: {final_status['name']}")
    print(f"Description: {final_status['description']}")
    print(f"Active: {final_status['is_active']}")
    print(f"Total Errors: {final_status['error_count']}")
    
    print("\n✅ Demo completed successfully!")

if __name__ == "__main__":
    main() 