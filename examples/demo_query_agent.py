#!/usr/bin/env python3
"""
Demo script for the QueryAgent
Shows how to use the unified query agent with LLM-based query analysis
"""

import os
import sys
import time
import json

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.query_agent import QueryAgent

def print_supported_query_types(agent):
    """Print information about supported query types"""
    print("\n=== Supported Query Types ===")
    query_types = agent.get_supported_query_types()
    
    for query_type, info in query_types.items():
        print(f"\n{query_type.replace('_', ' ').title()}:")
        print(f"  Description: {info['description']}")
        print(f"  Data Sources: {', '.join(info['data_sources'])}")
        print(f"  Examples:")
        for example in info['examples'][:2]:  # Show first 2 examples
            print(f"    - {example}")

def main():
    print("=== QueryAgent with LLM Analysis Demo ===")
    
    # Initialize the query agent
    print("1. Initializing QueryAgent...")
    agent = QueryAgent()
    
    # Show supported query types
    print_supported_query_types(agent)
    
    # Connect to databases
    print("\n2. Connecting to databases...")
    connection_result = agent.connect_databases()
    
    # Check database status
    print("\n3. Checking database status...")
    status = agent.get_database_status()
    print(f"   - PostgreSQL connected: {status['postgres_connected']}")
    print(f"   - Milvus connected: {status['milvus_connected']}")
    print(f"   - PostgreSQL config source: {status['postgres_config_source']}")
    print(f"   - Agent active: {status['agent_active']}")
    print(f"   - Query types configured: {status['query_types_configured']}")
    
    # Show functionality status
    func_status = status['functionality_status']
    print("\n   Functionality Status:")
    print(f"   - Structured queries (PostgreSQL): {'✓' if func_status['structured_queries'] else '✗'}")
    print(f"   - Document search (Milvus): {'✓' if func_status['document_search'] else '✗'}")
    print(f"   - Full functionality: {'✓' if func_status['full_functionality'] else '✗'}")
    
    if not connection_result:
        print("\n⚠️  Warning: Some or all databases are not connected.")
        print("   The agent will continue with limited functionality.")
        print("   💡 Run 'python setup_postgres.py' to set up PostgreSQL configuration")
        print("   💡 Make sure both PostgreSQL and Milvus are running for full functionality")
        
        # Ask if user wants to continue
        user_input = input("\n   Continue with demo anyway? (y/n): ").lower()
        if user_input != 'y':
            return
    
    # Demo queries that showcase different types and LLM analysis
    demo_queries = [
        # Statistical queries
        "How many students are enrolled in Computer Science?",
        "What's the average GPA of all students?",
        
        # Faculty queries with specific entities
        "Tell me about Dr. Smith's research and teaching",
        "Who are the faculty members in the Computer Science department?",
        
        # Research queries
        "What machine learning research projects are currently active?",
        "Show me information about artificial intelligence research",
        
        # Document search queries
        "Find documents about neural networks",
        "Search for university policies and procedures",
        
        # Administrative queries
        "What forms do I need to register for courses?",
        
        # General queries
        "Give me an overview of the Computer Science department",
        
        # Complex queries that might need both databases
        "Show me faculty research projects and related publications"
    ]
    
    print("\n4. Testing LLM-based query analysis and responses...")
    print("=" * 80)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 60)
        
        try:
            # Process the query (this now uses LLM analysis)
            response = agent.process_query(query)
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"Error processing query: {e}")
        
        # Small delay between queries
        time.sleep(1)
        
        # Add separator between queries
        if i < len(demo_queries):
            print("\n" + "." * 40)
    
    # Show some examples of what the LLM analysis might look like
    print("\n5. Example of LLM Query Analysis (Internal Process):")
    print("-" * 60)
    print("For a query like 'Tell me about Dr. Smith's research':")
    print("The LLM would identify:")
    print("  - Query Type: faculty_query")
    print("  - Specific Entities: ['Dr. Smith']")
    print("  - Search Intent: Find faculty information and research projects")
    print("  - Data Sources Needed: structured_data, vector_search")
    print("  - Confidence: 0.9")
    
    # Disconnect
    print("\n6. Disconnecting from databases...")
    agent.disconnect_databases()
    print("✓ Disconnected successfully")
    
    print("\n=== Demo Complete ===")
    print("\nKey Improvements in this version:")
    print("- LLM-based query analysis (no more hard-coded keywords)")
    print("- Intelligent entity extraction from queries")
    print("- Context-aware response generation")
    print("- Configurable query types with examples")
    print("- Better integration between structured and document data")

if __name__ == "__main__":
    main() 