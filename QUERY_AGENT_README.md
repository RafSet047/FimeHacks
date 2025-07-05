# QueryAgent Architecture

A simple and effective query agent that connects to both PostgreSQL and Milvus databases using a **Coordinator + Connectors** pattern.

## Architecture Overview

Instead of multiple specialized agents, we use:
- **One Main Agent** (`QueryAgent`) - Does all the reasoning with LLM
- **Two Connectors** - Handle different data access patterns
- **Query Router** - Determines which connectors to use
- **Prompt Templates** - Domain-specific prompt engineering

```
User Query → QueryAgent
              ↓
    [Query Analysis & Routing]
              ↓
    ┌─────────────────────────┐
    ↓                         ↓
PostgreSQL Connector    Milvus Connector
(Structured Data)      (Vector Search)
    ↓                         ↓
[SQL Queries]         [Document Retrieval]
    ↓                         ↓
    └─────────────────────────┘
              ↓
    [LLM Response Generation]
              ↓
         Final Response
```

## Key Features

### 1. **Intelligent Query Routing**
- Analyzes user queries to determine data sources needed
- Routes to PostgreSQL for structured data (counts, statistics, lists)
- Routes to Milvus for semantic search (documents, explanations)
- Can use both sources for comprehensive responses

### 2. **Database Connectors**
- **PostgreSQL Connector**: Handles structured university data
  - Student information, faculty records, courses
  - Research projects, equipment, forms
  - Statistical queries and aggregations
  
- **Milvus Connector**: Handles vector search and documents
  - Semantic document search
  - Tag-based filtering
  - Content similarity matching

### 3. **Contextual Response Generation**
- Builds rich context from multiple data sources
- Uses domain-specific prompts based on query type
- Combines structured and unstructured data in responses

## Usage

### Basic Usage

```python
from src.agents.query_agent import QueryAgent

# Initialize agent
agent = QueryAgent()

# Connect to databases
if agent.connect_databases():
    # Process queries
    response = agent.process_query("How many students are in Computer Science?")
    print(response)
    
    # Disconnect when done
    agent.disconnect_databases()
```

### Configuration

```python
# Custom configuration
config = {
    'postgres_config': {
        'host': 'localhost',
        'port': 5432,
        'database': 'university_db',
        'username': 'postgres',
        'password': 'your_password'
    },
    'milvus_config': {
        'host': 'localhost',
        'port': 19530
    },
    'default_collection': 'university_documents',
    'max_search_results': 10
}

agent = QueryAgent(config=config)
```

### Example Queries

The agent can handle various types of queries:

**Structured Data Queries:**
- "How many students are enrolled?"
- "List all faculty in Computer Science"
- "What's the average GPA?"
- "Show me research project statistics"

**Document Search Queries:**
- "Find documents about machine learning"
- "Search for policy documents"
- "What information do we have about Dr. Smith?"
- "Show me course materials for CS101"

**Combined Queries:**
- "Tell me about the Computer Science department" (uses both databases)
- "Find research projects and related documents"
- "Show me faculty information and their publications"

## Query Processing Flow

1. **Query Analysis**: Determines query type and needed data sources
2. **Data Gathering**: Collects relevant data from appropriate connectors
3. **Context Building**: Assembles structured and document data
4. **Response Generation**: Uses LLM with rich context to generate answer

## Query Types

The agent recognizes different query types for specialized handling:

- **Student Queries**: Student enrollment, GPA, records
- **Faculty Queries**: Faculty information, departments, research
- **Academic Queries**: Courses, curriculum, departments
- **Research Queries**: Projects, grants, publications
- **Facility Queries**: Equipment, buildings, resources
- **Administrative Queries**: Forms, policies, procedures

## Advantages of This Architecture

### 1. **Simplicity**
- Single agent with clear responsibilities
- No complex inter-agent communication
- Easy to debug and maintain

### 2. **Flexibility**
- Easy to add new data sources (just add connectors)
- Can modify reasoning without changing data access
- Simple to extend with new query types

### 3. **Efficiency**
- No agent coordination overhead
- Direct database connections
- Can query multiple sources in parallel

### 4. **Honesty**
- Architecture matches actual functionality
- Same LLM doing all reasoning
- Clear separation of data access vs. reasoning

## Running the Demo

```bash
# Run the demo script
python examples/demo_query_agent.py
```

Make sure you have:
- PostgreSQL running with university data
- Milvus database running
- Required environment variables set (GEMINI_API_KEY)

## Dependencies

- `psycopg2` - PostgreSQL adapter
- `pymilvus` - Milvus vector database client
- `google-generativeai` - Google Gemini API
- Standard Python libraries

## Why This Approach Works

This architecture is honest about what it does:
- **One brain** (LLM) doing the reasoning
- **Multiple tools** (connectors) for data access
- **Smart routing** to determine which tools to use
- **Rich context** building for better responses

It avoids the complexity of multi-agent systems while providing all the benefits of specialized data access and domain-aware responses. 