from typing import Dict, List, Optional, Any, Union
import logging
import json
import re
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.database.postgre_db import UniversityPostgreDB, DatabaseConfig
from src.database.milvus_db import MilvusVectorDatabase
from src.utils.logging import setup_logging

logger = setup_logging()

# Query Types Configuration
QUERY_TYPES_CONFIG = {
    "student_query": {
        "description": "Questions about students, enrollment, grades, academic records",
        "examples": [
            "How many students are enrolled in Computer Science?",
            "What's the average GPA of students?",
            "Show me students with high GPA",
            "Who are the students in the Mathematics department?"
        ],
        "data_sources": ["structured_data", "vector_search"],
        "postgresql_priority": True
    },
    "faculty_query": {
        "description": "Questions about faculty members, professors, instructors, teaching assignments",
        "examples": [
            "Who are the faculty members in Computer Science?",
            "Show me information about Dr. Smith",
            "What courses does Professor Johnson teach?",
            "List all tenured faculty"
        ],
        "data_sources": ["structured_data", "vector_search"],
        "postgresql_priority": True
    },
    "academic_query": {
        "description": "Questions about courses, curriculum, academic programs, departments",
        "examples": [
            "What courses are offered this semester?",
            "Show me the Computer Science curriculum",
            "What departments does the university have?",
            "Tell me about course CS101"
        ],
        "data_sources": ["structured_data", "vector_search"],
        "postgresql_priority": True
    },
    "research_query": {
        "description": "Questions about research projects, grants, publications, academic research",
        "examples": [
            "What research projects are currently active?",
            "Show me machine learning research",
            "What grants has the university received?",
            "Find research about artificial intelligence"
        ],
        "data_sources": ["structured_data", "vector_search"],
        "postgresql_priority": False
    },
    "facility_query": {
        "description": "Questions about equipment, buildings, facilities, resources",
        "examples": [
            "What equipment is available in the Computer Science lab?",
            "Show me the university facilities",
            "What resources are available for research?",
            "List all available equipment"
        ],
        "data_sources": ["structured_data"],
        "postgresql_priority": True
    },
    "administrative_query": {
        "description": "Questions about forms, policies, procedures, administrative processes",
        "examples": [
            "What forms do I need for course registration?",
            "Show me the university policies",
            "How do I apply for a transcript?",
            "What are the graduation requirements?"
        ],
        "data_sources": ["structured_data", "vector_search"],
        "postgresql_priority": False
    },
    "document_search": {
        "description": "Questions asking to find, search, or retrieve specific documents or information",
        "examples": [
            "Find documents about machine learning",
            "Search for policy documents",
            "Show me course materials for CS101",
            "What information do we have about neural networks?"
        ],
        "data_sources": ["vector_search"],
        "postgresql_priority": False
    },
    "statistical_query": {
        "description": "Questions asking for counts, statistics, summaries, or aggregated data",
        "examples": [
            "How many students are enrolled?",
            "What's the total number of faculty?",
            "Show me enrollment statistics",
            "What's the average research grant amount?"
        ],
        "data_sources": ["structured_data"],
        "postgresql_priority": True
    },
    "general_query": {
        "description": "General questions that don't fit specific categories or require broad information",
        "examples": [
            "Tell me about the university",
            "What can you help me with?",
            "Give me an overview of the Computer Science department",
            "What services does the university offer?"
        ],
        "data_sources": ["structured_data", "vector_search"],
        "postgresql_priority": False
    }
}

class QueryAgent(BaseAgent):
    """
    Main Query Agent with connectors to PostgreSQL and Milvus databases
    Uses LLM reasoning to understand queries and route to appropriate data sources
    """
    
    def __init__(self, 
                 name: str = "QueryAgent",
                 description: str = "Main query agent with intelligent database connectors",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(name, description, config)
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize database connectors
        self.postgres_connector = None
        self.milvus_connector = None
        
        # Query types configuration
        self.query_types = QUERY_TYPES_CONFIG
        
        self.default_config = {
            'milvus_config': {
                'host': 'localhost',
                'port': 19530
            },
            'default_collection': 'university_documents',
            'max_search_results': 10
        }
        
        self.config = {**self.default_config, **self.config}
        
        # Initialize connectors
        self._initialize_connectors()
    
    def _initialize_connectors(self):
        """Initialize database connectors"""
        try:
            # Initialize PostgreSQL connector with smart configuration loading
            postgres_config = self._load_postgres_config()
            self.postgres_connector = UniversityPostgreDB(postgres_config)
            
            # Initialize Milvus connector
            milvus_config = self.config['milvus_config']
            self.milvus_connector = MilvusVectorDatabase(
                host=milvus_config['host'],
                port=milvus_config['port']
            )
            
            logger.info("Database connectors initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connectors: {e}")
            self.handle_error(e, "connector_initialization")
    
    def _load_postgres_config(self) -> DatabaseConfig:
        """Load PostgreSQL configuration from file or use defaults"""
        import sys
        import os
        
        # Try to load configuration from file, otherwise use defaults
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from database_config import DATABASE_CONFIG
            config = DatabaseConfig(
                host=DATABASE_CONFIG["host"],
                port=DATABASE_CONFIG["port"],
                database=DATABASE_CONFIG["database"],
                username=DATABASE_CONFIG["username"],
                password=DATABASE_CONFIG["password"]
            )
            logger.info("Using configuration from database_config.py")
        except ImportError:
            # Use default configuration
            config = DatabaseConfig(
                host="localhost",          # PostgreSQL server host
                port=5432,                # Default PostgreSQL port
                database="fimehacks_db",   # Database name
                username="fimehacks_user", # Your PostgreSQL username
                password="fimehacks_password" # Your PostgreSQL password
            )
            logger.info("Using default configuration")
            logger.info("💡 Run 'python setup_postgres.py' to create a custom configuration")
        
        return config
    
    def connect_databases(self) -> bool:
        """Connect to both databases"""
        try:
            postgres_connected = False
            milvus_connected = False
            
            # Try connecting to PostgreSQL
            try:
                postgres_connected = self.postgres_connector.connect()
                if postgres_connected:
                    logger.info("✓ Connected to PostgreSQL successfully")
                else:
                    logger.warning("✗ Failed to connect to PostgreSQL")
            except Exception as e:
                logger.error(f"✗ PostgreSQL connection error: {e}")
                
            # Try connecting to Milvus
            try:
                milvus_connected = self.milvus_connector.connect()
                if milvus_connected:
                    logger.info("✓ Connected to Milvus successfully")
                else:
                    logger.warning("✗ Failed to connect to Milvus")
            except Exception as e:
                logger.error(f"✗ Milvus connection error: {e}")
            
            if postgres_connected and milvus_connected:
                logger.info("Successfully connected to both databases")
                return True
            elif postgres_connected or milvus_connected:
                logger.warning("Partial connection established - some features may be limited")
                return postgres_connected or milvus_connected  # Allow partial functionality
            else:
                logger.error("Failed to connect to any database")
                return False
                
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def process_query(self, user_query: str) -> str:
        """
        Main query processing method using LLM reasoning
        
        Args:
            user_query: The user's natural language query
            
        Returns:
            Generated response based on retrieved data
        """
        try:
            logger.info(f"Processing query: {user_query}")
            
            # 1. Use LLM to analyze query and create execution plan
            query_plan = self._analyze_query_with_llm(user_query)
            print("\tQuery Plan: ", query_plan)
            
            # 2. Gather data based on LLM's analysis
            context_data = self._gather_context_data(user_query, query_plan)
            print("\tContext Data: ", context_data)
            
            # 3. Generate response using LLM with gathered context
            response = self._generate_response(user_query, context_data, query_plan)
            
            logger.info("Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            self.handle_error(e, "query_processing")
            return "I apologize, but I encountered an error processing your query. Please try again."
    
    def _analyze_query_with_llm(self, query: str) -> Dict[str, Any]:
        """Use LLM to analyze the query and determine execution plan"""
        try:
            # Build analysis prompt
            analysis_prompt = self._build_analysis_prompt(query)
            
            # Get LLM analysis
            response = self.llm.generate_content(analysis_prompt)
            
            if hasattr(response, 'text'):
                analysis_text = response.text
            else:
                analysis_text = str(response)
            
            # Parse the LLM's analysis
            query_plan = self._parse_llm_analysis(analysis_text)
            
            logger.info(f"LLM Query Analysis: {query_plan}")
            return query_plan
            
        except Exception as e:
            logger.error(f"Error in LLM query analysis: {e}")
            # Fallback to default plan
            return {
                'query_type': 'general_query',
                'needs_structured_data': True,
                'needs_vector_search': True,
                'specific_entities': [],
                'search_intent': query,
                'confidence': 0.5
            }
    
    def _build_analysis_prompt(self, query: str) -> str:
        """Build prompt for LLM query analysis"""
        query_types_desc = "\n".join([
            f"- {qtype}: {config['description']}"
            for qtype, config in self.query_types.items()
        ])
        
        prompt = f"""
You are a query analysis expert. Analyze the following user query and determine:
1. What type of query it is
2. What data sources are needed
3. Any specific entities or search terms mentioned
4. The user's intent

Query Types Available:
{query_types_desc}

User Query: "{query}"

Please respond in the following JSON format:
{{
    "query_type": "one of the query types above",
    "needs_structured_data": true/false,
    "needs_vector_search": true/false,
    "specific_entities": ["list of specific names, terms, or entities mentioned"],
    "search_intent": "what the user is trying to find or accomplish",
    "confidence": 0.0-1.0
}}

Focus on understanding the user's intent and what data would best answer their question.
"""
        return prompt
    
    def _parse_llm_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse LLM analysis response"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                analysis = json.loads(json_str)
                
                # Validate and set defaults
                query_type = analysis.get('query_type', 'general_query')
                if query_type not in self.query_types:
                    query_type = 'general_query'
                
                return {
                    'query_type': query_type,
                    'needs_structured_data': analysis.get('needs_structured_data', True),
                    'needs_vector_search': analysis.get('needs_vector_search', True),
                    'specific_entities': analysis.get('specific_entities', []),
                    'search_intent': analysis.get('search_intent', ''),
                    'confidence': analysis.get('confidence', 0.5)
                }
            else:
                # If no JSON found, try to parse key information
                analysis_lower = analysis_text.lower()
                
                # Determine query type based on content
                query_type = 'general_query'
                for qtype, config in self.query_types.items():
                    if any(keyword in analysis_lower for keyword in config['description'].lower().split()):
                        query_type = qtype
                        break
                
                return {
                    'query_type': query_type,
                    'needs_structured_data': 'structured' in analysis_lower or 'database' in analysis_lower,
                    'needs_vector_search': 'document' in analysis_lower or 'search' in analysis_lower,
                    'specific_entities': [],
                    'search_intent': analysis_text[:100],
                    'confidence': 0.3
                }
                
        except Exception as e:
            logger.error(f"Error parsing LLM analysis: {e}")
            return {
                'query_type': 'general_query',
                'needs_structured_data': True,
                'needs_vector_search': True,
                'specific_entities': [],
                'search_intent': '',
                'confidence': 0.2
            }
    
    def _gather_context_data(self, query: str, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Gather context data based on LLM analysis"""
        context_data = {}
        
        # Gather structured data if needed and PostgreSQL is connected
        if query_plan['needs_structured_data'] and self.postgres_connector and hasattr(self.postgres_connector, 'connection') and self.postgres_connector.connection:
            context_data['structured_data'] = self._query_structured_data(query, query_plan)
        elif query_plan['needs_structured_data']:
            logger.warning("Structured data requested but PostgreSQL not connected")
        
        # Gather vector search results if needed and Milvus is connected
        if query_plan['needs_vector_search'] and self.milvus_connector and self.milvus_connector.is_connected:
            context_data['documents'] = self._query_vector_data(query, query_plan)
        elif query_plan['needs_vector_search']:
            logger.warning("Vector search requested but Milvus not connected")
        
        return context_data
    
        """Query PostgreSQL for structured data based on query plan"""
        try:
            logger.info("=== STARTING STRUCTURED DATA QUERY ===")
            logger.info(f"Original query: {query}")
            logger.info(f"Query plan: {query_plan}")
            
            structured_data = {}
            query_type = query_plan['query_type']
            specific_entities = query_plan.get('specific_entities', [])
            search_intent = query_plan.get('search_intent', '').lower()
            
            logger.info(f"📊 Query type identified: {query_type}")
            logger.info(f"🔍 Specific entities: {specific_entities}")
            logger.info(f"🎯 Search intent: {search_intent}")
            
            # Step 1: Get basic statistics for most queries
            logger.info("--- STEP 1: Getting database summary ---")
            try:
                structured_data['database_summary'] = self.postgres_connector.get_database_summary()
                logger.info(f"✓ Database summary retrieved: {structured_data['database_summary']}")
            except Exception as e:
                logger.error(f"✗ Failed to get database summary: {e}")
                structured_data['database_summary'] = None
            
            # Step 2: Query type-specific data
            logger.info("--- STEP 2: Processing query type-specific data ---")
            
            # Student queries
            student_condition = query_type == 'student_query' or 'student' in search_intent
            logger.info(f"🎓 Student query check: query_type={query_type == 'student_query'}, search_intent_match={'student' in search_intent}, final={student_condition}")
            
            if student_condition:
                logger.info("🎓 Processing student query...")
                try:
                    structured_data['student_stats'] = self.postgres_connector.get_student_enrollment_stats()
                    logger.info(f"✓ Student stats retrieved: {structured_data['student_stats']}")
                except Exception as e:
                    logger.error(f"✗ Failed to get student stats: {e}")
                    structured_data['student_stats'] = None
                
                try:
                    structured_data['students'] = self.postgres_connector.get_students_by_major('Computer Science')[:5]
                    logger.info(f"✓ Student data retrieved: {len(structured_data['students']) if structured_data['students'] else 0} students")
                except Exception as e:
                    logger.error(f"✗ Failed to get student data: {e}")
                    structured_data['students'] = []
            
            # Faculty queries
            faculty_condition = query_type == 'faculty_query' or 'faculty' in search_intent
            logger.info(f"👨‍🏫 Faculty query check: query_type={query_type == 'faculty_query'}, search_intent_match={'faculty' in search_intent}, final={faculty_condition}")
            
            if faculty_condition:
                logger.info("👨‍🏫 Processing faculty query...")
                try:
                    structured_data['faculty_stats'] = self.postgres_connector.get_faculty_stats()
                    logger.info(f"✓ Faculty stats retrieved: {structured_data['faculty_stats']}")
                except Exception as e:
                    logger.error(f"✗ Failed to get faculty stats: {e}")
                    structured_data['faculty_stats'] = None
                
                try:
                    structured_data['faculty'] = self.postgres_connector.get_faculty_by_department('DEPT001')
                    logger.info(f"✓ Faculty data retrieved: {len(structured_data['faculty']) if structured_data['faculty'] else 0} faculty members")
                except Exception as e:
                    logger.error(f"✗ Failed to get faculty data: {e}")
                    structured_data['faculty'] = []
            
            # Research queries
            research_condition = query_type == 'research_query' or 'research' in search_intent
            logger.info(f"🔬 Research query check: query_type={query_type == 'research_query'}, search_intent_match={'research' in search_intent}, final={research_condition}")
            
            if research_condition:
                logger.info("🔬 Processing research query...")
                try:
                    structured_data['research_stats'] = self.postgres_connector.get_research_stats()
                    logger.info(f"✓ Research stats retrieved: {structured_data['research_stats']}")
                except Exception as e:
                    logger.error(f"✗ Failed to get research stats: {e}")
                    structured_data['research_stats'] = None
                
                try:
                    structured_data['research_projects'] = self.postgres_connector.get_research_by_department('DEPT001')
                    logger.info(f"✓ Research projects retrieved: {len(structured_data['research_projects']) if structured_data['research_projects'] else 0} projects")
                except Exception as e:
                    logger.error(f"✗ Failed to get research projects: {e}")
                    structured_data['research_projects'] = []
            
            # Academic queries
            academic_keywords = ['course', 'curriculum', 'department']
            academic_condition = query_type == 'academic_query' or any(word in search_intent for word in academic_keywords)
            logger.info(f"📚 Academic query check: query_type={query_type == 'academic_query'}, search_intent_matches={[word for word in academic_keywords if word in search_intent]}, final={academic_condition}")
            
            if academic_condition:
                logger.info("📚 Processing academic query...")
                try:
                    structured_data['courses'] = self.postgres_connector.get_courses_by_department('DEPT001')
                    logger.info(f"✓ Courses retrieved: {len(structured_data['courses']) if structured_data['courses'] else 0} courses")
                except Exception as e:
                    logger.error(f"✗ Failed to get courses: {e}")
                    structured_data['courses'] = []
                
                try:
                    structured_data['departments'] = self.postgres_connector.get_all_departments()
                    logger.info(f"✓ Departments retrieved: {len(structured_data['departments']) if structured_data['departments'] else 0} departments")
                except Exception as e:
                    logger.error(f"✗ Failed to get departments: {e}")
                    structured_data['departments'] = []
            
            # Facility queries
            facility_condition = query_type == 'facility_query' or 'equipment' in search_intent
            logger.info(f"🏢 Facility query check: query_type={query_type == 'facility_query'}, search_intent_match={'equipment' in search_intent}, final={facility_condition}")
            
            if facility_condition:
                logger.info("🏢 Processing facility query...")
                try:
                    structured_data['equipment'] = self.postgres_connector.get_equipment_by_department('DEPT001')
                    logger.info(f"✓ Equipment retrieved: {len(structured_data['equipment']) if structured_data['equipment'] else 0} equipment items")
                except Exception as e:
                    logger.error(f"✗ Failed to get equipment: {e}")
                    structured_data['equipment'] = []
            
            # Administrative queries
            administrative_condition = query_type == 'administrative_query' or 'form' in search_intent
            logger.info(f"📋 Administrative query check: query_type={query_type == 'administrative_query'}, search_intent_match={'form' in search_intent}, final={administrative_condition}")
            
            if administrative_condition:
                logger.info("📋 Processing administrative query...")
                try:
                    structured_data['forms'] = self.postgres_connector.get_forms_by_type('Academic')
                    logger.info(f"✓ Forms retrieved: {len(structured_data['forms']) if structured_data['forms'] else 0} forms")
                except Exception as e:
                    logger.error(f"✗ Failed to get forms: {e}")
                    structured_data['forms'] = []
            
            # Step 3: Search for specific entities mentioned by the LLM
            logger.info("--- STEP 3: Processing specific entities ---")
            
            if specific_entities:
                logger.info(f"🔍 Found {len(specific_entities)} specific entities to search for: {specific_entities}")
                structured_data['entity_search_results'] = {}
                
                for i, entity in enumerate(specific_entities, 1):
                    logger.info(f"🔍 Processing entity {i}/{len(specific_entities)}: '{entity}'")
                    
                    # Search students
                    try:
                        student_results = self.postgres_connector.search_students(entity)
                        structured_data['entity_search_results'][f'students_{entity}'] = student_results
                        logger.info(f"  ✓ Student search for '{entity}': {len(student_results) if student_results else 0} results")
                    except Exception as e:
                        logger.error(f"  ✗ Student search for '{entity}' failed: {e}")
                        structured_data['entity_search_results'][f'students_{entity}'] = []
                    
                    # Search faculty
                    try:
                        faculty_results = self.postgres_connector.search_faculty(entity)
                        structured_data['entity_search_results'][f'faculty_{entity}'] = faculty_results
                        logger.info(f"  ✓ Faculty search for '{entity}': {len(faculty_results) if faculty_results else 0} results")
                    except Exception as e:
                        logger.error(f"  ✗ Faculty search for '{entity}' failed: {e}")
                        structured_data['entity_search_results'][f'faculty_{entity}'] = []
                    
                    # Search research projects
                    try:
                        research_results = self.postgres_connector.search_research_projects(entity)
                        structured_data['entity_search_results'][f'research_{entity}'] = research_results
                        logger.info(f"  ✓ Research search for '{entity}': {len(research_results) if research_results else 0} results")
                    except Exception as e:
                        logger.error(f"  ✗ Research search for '{entity}' failed: {e}")
                        structured_data['entity_search_results'][f'research_{entity}'] = []
            else:
                logger.info("🔍 No specific entities to search for")
            
            # Step 4: Final summary
            logger.info("--- STEP 4: Final summary ---")
            total_data_keys = len(structured_data)
            logger.info(f"📊 Total data sections retrieved: {total_data_keys}")
            
            for key, value in structured_data.items():
                if isinstance(value, dict):
                    logger.info(f"  📁 {key}: {len(value)} subsections")
                elif isinstance(value, list):
                    logger.info(f"  📁 {key}: {len(value)} items")
                else:
                    logger.info(f"  📁 {key}: {type(value).__name__}")
            
            logger.info("=== STRUCTURED DATA QUERY COMPLETED ===")
            return structured_data
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR in structured data query: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {}
    
    def _query_vector_data(self, query: str, query_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query Milvus for vector search results based on query plan"""
        try:
            collection_name = self.config['default_collection']
            
            # Get stored documents
            documents = self.milvus_connector.get_stored_documents(
                collection_name, 
                limit=self.config['max_search_results']
            )
            
            if not documents:
                logger.info("No documents found in vector database")
                return []
            
            # Use LLM-identified entities and search intent for better matching
            search_terms = query_plan.get('specific_entities', [])
            search_intent = query_plan.get('search_intent', query).lower()
            
            # Score documents based on relevance
            scored_documents = []
            for doc in documents:
                content = doc.get('content', '').lower()
                tags = doc.get('tags', [])
                
                # Calculate relevance score
                score = 0
                
                # Score based on specific entities
                for entity in search_terms:
                    if entity.lower() in content:
                        score += 3
                    if entity.lower() in ' '.join(tags).lower():
                        score += 2
                
                # Score based on search intent keywords
                intent_words = search_intent.split()
                for word in intent_words:
                    if len(word) > 3:  # Skip small words
                        if word in content:
                            score += 1
                        if word in ' '.join(tags).lower():
                            score += 1
                
                if score > 0:
                    doc['relevance_score'] = score
                    scored_documents.append(doc)
            
            # Sort by relevance score
            scored_documents.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return scored_documents[:self.config['max_search_results']]
            
        except Exception as e:
            logger.error(f"Error querying vector data: {e}")
            return []
    
    def _generate_response(self, query: str, context_data: Dict[str, Any], query_plan: Dict[str, Any]) -> str:
        """Generate response using LLM with gathered context"""
        try:
            # Build prompt based on query plan and available data
            prompt = self._build_response_prompt(query, context_data, query_plan)
            
            # Generate response
            response = self.llm.generate_content(prompt)
            
            if hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error generating a response. Please try again."
    
    def _build_response_prompt(self, query: str, context_data: Dict[str, Any], query_plan: Dict[str, Any]) -> str:
        """Build prompt for response generation"""
        prompt_parts = []
        
        # System prompt with query context
        query_type_config = self.query_types.get(query_plan['query_type'], {})
        
        # Check database availability
        postgres_available = self.postgres_connector and hasattr(self.postgres_connector, 'connection') and self.postgres_connector.connection
        milvus_available = self.milvus_connector and self.milvus_connector.is_connected
        
        availability_note = ""
        if not postgres_available and not milvus_available:
            availability_note = "\n⚠️  Note: Both databases are currently unavailable. Limited information available."
        elif not postgres_available:
            availability_note = "\n⚠️  Note: Structured database (PostgreSQL) is unavailable. Statistical and detailed records may be limited."
        elif not milvus_available:
            availability_note = "\n⚠️  Note: Document database (Milvus) is unavailable. Document search and semantic information may be limited."
        
        prompt_parts.append(f"""You are a helpful university assistant. The user asked a {query_plan['query_type'].replace('_', ' ')} question.

Query Analysis:
- Intent: {query_plan.get('search_intent', 'General inquiry')}
- Confidence: {query_plan.get('confidence', 0.5)}
- Specific entities mentioned: {query_plan.get('specific_entities', [])}

Instructions:
- Answer the user's question accurately using the provided data
- If specific entities were mentioned, focus on those
- Be comprehensive but concise
- If you don't have enough information, say so clearly
- Format your response in a clear, organized manner{availability_note}""")
        
        # Add structured data context if available
        if 'structured_data' in context_data and context_data['structured_data']:
            prompt_parts.append("\n--- STRUCTURED DATA FROM DATABASE ---")
            structured_data = context_data['structured_data']
            
            for key, value in structured_data.items():
                if value:
                    prompt_parts.append(f"{key.replace('_', ' ').title()}: {json.dumps(value, indent=2, default=str)}")
        
        # Add document context if available
        if 'documents' in context_data and context_data['documents']:
            prompt_parts.append("\n--- RELEVANT DOCUMENTS ---")
            for i, doc in enumerate(context_data['documents'][:3]):  # Top 3 documents
                prompt_parts.append(f"Document {i+1} (Relevance: {doc.get('relevance_score', 0)}):")
                prompt_parts.append(f"Content: {doc.get('content', '')[:400]}...")
                prompt_parts.append(f"Tags: {doc.get('tags', [])}")
                prompt_parts.append(f"Department: {doc.get('department', 'Unknown')}")
                prompt_parts.append("")
        
        # Add user query
        prompt_parts.append(f"\n--- USER QUESTION ---")
        prompt_parts.append(f"Question: {query}")
        prompt_parts.append(f"\nPlease provide a comprehensive answer based on the available data:")
        
        return "\n".join(prompt_parts)
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get status of database connections"""
        postgres_connected = self.postgres_connector and hasattr(self.postgres_connector, 'connection') and self.postgres_connector.connection
        milvus_connected = self.milvus_connector and self.milvus_connector.is_connected
        
        return {
            'postgres_connected': postgres_connected,
            'milvus_connected': milvus_connected,
            'postgres_config_source': 'database_config.py' if postgres_connected else 'default/failed',
            'agent_active': self.is_active,
            'error_count': self.error_count,
            'query_types_configured': len(self.query_types),
            'functionality_status': {
                'structured_queries': postgres_connected,
                'document_search': milvus_connected,
                'full_functionality': postgres_connected and milvus_connected
            }
        }
    
    def get_supported_query_types(self) -> Dict[str, Any]:
        """Get information about supported query types"""
        return {
            query_type: {
                'description': config['description'],
                'examples': config['examples'],
                'data_sources': config['data_sources']
            }
            for query_type, config in self.query_types.items()
        }
    
    def disconnect_databases(self):
        """Disconnect from databases"""
        try:
            if self.postgres_connector:
                self.postgres_connector.close()
            if self.milvus_connector:
                self.milvus_connector.disconnect()
            logger.info("Disconnected from databases")
        except Exception as e:
            logger.error(f"Error disconnecting from databases: {e}")
