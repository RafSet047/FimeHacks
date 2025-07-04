# Simple Milvus Workflow Demo

This example demonstrates a complete end-to-end workflow from file creation to Milvus vector database operations.

## What This Demo Does

1. **📁 Creates Sample Files**: Generates realistic healthcare and university text files
2. **⚙️ Processes with TextWorkflow**: Uses the text workflow to extract content, generate embeddings, and create structured metadata
3. **💾 Stores in Milvus**: Converts workflow output to Pydantic DocumentMetadata and stores in Milvus vector database
4. **🔍 Performs All Search Types**: Demonstrates vector search, metadata search, and hybrid search capabilities
5. **📊 Shows Statistics**: Displays collection statistics and results

## Sample Files Created

### Healthcare File (`healthcare_protocol.txt`)
```
EMERGENCY CARDIAC PROTOCOL - St. Mary's Hospital

Patient Assessment Guidelines:
- Check vital signs immediately upon arrival
- Obtain ECG within 10 minutes for chest pain complaints
- Administer oxygen if SpO2 < 94%
- Establish IV access for medication administration

Treatment Protocol:
1. Assess airway, breathing, circulation
2. Administer aspirin 325mg if no contraindications
...
```

### University File (`cs101_syllabus.txt`)
```
COMPUTER SCIENCE 101 - Introduction to Programming

Course Syllabus - Spring 2024

Instructor: Prof. Sarah Chen
Office Hours: Tuesday/Thursday 2-4 PM
Email: s.chen@university.edu

Course Objectives:
Students will learn fundamental programming concepts including:
- Variables and data types
- Control structures (loops, conditionals)
...
```

## How to Run

```bash
# From the project root directory
python examples/simple_milvus_workflow_demo.py
```

## Expected Output

```
🚀 SIMPLE MILVUS WORKFLOW DEMO
==================================================

📁 Creating sample files...
✅ Created files in: /tmp/...

🗄️  Initializing Milvus database...
✅ Connected to Milvus Lite
✅ Collections created

⚙️  Processing files with TextWorkflow...

📄 Processing file: healthcare_protocol.txt
✅ Processing successful in 0.00s
   Word count: 108
   Keywords: protocol, cardiology, emergency, cardiac, obtain...
   Embeddings: 2 chunks generated

📄 Processing file: cs101_syllabus.txt
✅ Processing successful in 0.00s
   Word count: 119
   Keywords: programming, course, introduction, chen, will...
   Embeddings: 2 chunks generated

💾 Storing data in Milvus...
✅ Documents stored successfully
   Healthcare doc ID: 201002f8...
   University doc ID: e654daf4...

🔍 PERFORMING SEARCHES
==================================================

1. 🎯 Vector Similarity Search:
   Result 1: healthcare - emergency_medicine (similarity: 1.000)
   Result 2: university - computer_science (similarity: 0.785)

2. 🏥 Metadata Search - Healthcare Documents:
   Result 1: Demo Healthcare Document

3. 🎓 Metadata Search - University Documents:
   Result 1: Demo University Document

4. 🔗 Hybrid Search - Vector + Metadata Filter:
   Result 1: healthcare - internal (score: 1.000)
   Result 2: university - internal (score: 0.785)

5. 📊 Collection Statistics:
   Total documents: 4
   Collection: documents
   Vector dimension: 1536

🎉 Demo completed successfully!
🧹 Cleaned up temporary files
```

## Technical Details

### Components Used

1. **TextWorkflow**: Processes text files to extract content, keywords, and generate embeddings
2. **MilvusVectorDatabase**: Handles vector storage and similarity search
3. **Pydantic Models**: Type-safe configuration and metadata structures
4. **FileMetadata**: Rich metadata structure for file classification

### Search Types Demonstrated

1. **Vector Similarity Search**: Finds documents similar to a query vector
2. **Metadata Search**: Filters documents by organizational metadata (healthcare vs university)
3. **Hybrid Search**: Combines vector similarity with metadata filtering
4. **Collection Statistics**: Shows database metrics

### Metadata Structure

The demo creates rich metadata including:
- Organizational info (department, role, access level)
- Content details (title, author, keywords, tags)
- Processing metadata (API used, confidence, duration)
- Domain-specific data (healthcare protocols, university courses)
- Compliance info (HIPAA for healthcare, FERPA for university)

## Prerequisites

- Python 3.8+
- Milvus Lite (automatically installed with `pip install milvus-lite`)
- All project dependencies (`pip install -r requirements.txt`)

## Files Structure

```
examples/
├── simple_milvus_workflow_demo.py  # Main demo script
└── README_simple_workflow.md       # This documentation

src/
├── services/workflows/text_workflow.py  # Text processing workflow
├── database/milvus_db.py                # Milvus database interface
├── database/config.py                   # Pydantic configuration models
└── models/metadata.py                   # File metadata structures
```

## Key Learning Points

1. **End-to-end Workflow**: See how files go from raw text to searchable vector database
2. **Metadata Richness**: Understand how rich metadata enables powerful filtering
3. **Search Flexibility**: Learn different search strategies for different use cases
4. **Type Safety**: See Pydantic models in action for configuration and validation
5. **Production Ready**: Uses Milvus Lite for local development and testing

## Next Steps

- Modify the sample content to test with your own data
- Experiment with different metadata structures
- Try different embedding models (currently uses simple hash-based embeddings)
- Explore more complex search queries and filters
- Scale up to full Milvus deployment for production use 