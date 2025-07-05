"""
PostgreSQL Database Implementation for University Data

This module provides comprehensive PostgreSQL database functionality for university data management,
including schema initialization, data loading from CSV files, and basic database operations.
"""

import os
import csv
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration parameters"""
    host: str = "localhost"
    port: int = 5432
    database: str = "university_db"
    username: str = "postgres"
    password: str = "password"
    
    def get_connection_string(self) -> str:
        """Generate connection string for PostgreSQL"""
        return f"host={self.host} port={self.port} dbname={self.database} user={self.username} password={self.password}"
    
    def get_admin_connection_string(self) -> str:
        """Generate admin connection string (without database name for initial setup)"""
        return f"host={self.host} port={self.port} user={self.username} password={self.password}"


class UniversityPostgreDB:
    """PostgreSQL database manager for university data"""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database manager with configuration"""
        self.config = config
        self.connection = None
        self.cursor = None
        
        # Define table schemas
        self.table_schemas = {
            'departments': """
                CREATE TABLE IF NOT EXISTS departments (
                    department_id VARCHAR(20) PRIMARY KEY,
                    department_name VARCHAR(100) NOT NULL,
                    department_code VARCHAR(10) NOT NULL,
                    college VARCHAR(50),
                    building VARCHAR(50),
                    floor INTEGER,
                    phone_extension VARCHAR(10),
                    email VARCHAR(100),
                    department_head VARCHAR(100),
                    annual_budget DECIMAL(12,2),
                    faculty_count INTEGER,
                    staff_count INTEGER,
                    student_capacity INTEGER,
                    specialization_area VARCHAR(100),
                    operating_hours VARCHAR(20),
                    research_active BOOLEAN,
                    accreditation_status VARCHAR(50),
                    last_review_date DATE,
                    student_satisfaction_score DECIMAL(3,1),
                    annual_enrollment INTEGER,
                    research_budget DECIMAL(12,2),
                    graduate_programs BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            'buildings': """
                CREATE TABLE IF NOT EXISTS buildings (
                    building_id VARCHAR(20) PRIMARY KEY,
                    building_name VARCHAR(100) NOT NULL,
                    building_type VARCHAR(50),
                    floors INTEGER,
                    construction_year INTEGER,
                    renovation_year INTEGER,
                    total_rooms INTEGER,
                    department_id VARCHAR(20),
                    capacity INTEGER,
                    square_footage INTEGER,
                    accessibility_compliant BOOLEAN,
                    wifi_available BOOLEAN,
                    hvac_system VARCHAR(50),
                    security_level VARCHAR(20),
                    parking_spaces INTEGER,
                    maintenance_cost_annual DECIMAL(12,2),
                    energy_efficiency_rating VARCHAR(10),
                    room_types TEXT,
                    special_features TEXT,
                    usage_hours VARCHAR(20),
                    fire_safety_rating VARCHAR(5),
                    last_inspection_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id)
                )
            """,
            
            'faculty': """
                CREATE TABLE IF NOT EXISTS faculty (
                    faculty_id VARCHAR(20) PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    middle_name VARCHAR(50),
                    position VARCHAR(50),
                    department_id VARCHAR(20),
                    hire_date DATE,
                    birth_date DATE,
                    gender VARCHAR(10),
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    address TEXT,
                    emergency_contact_name VARCHAR(100),
                    emergency_contact_phone VARCHAR(20),
                    annual_salary DECIMAL(12,2),
                    teaching_load VARCHAR(20),
                    education_level VARCHAR(20),
                    specialization VARCHAR(100),
                    tenure_status VARCHAR(20),
                    office_location VARCHAR(50),
                    research_active BOOLEAN,
                    publications_count INTEGER,
                    grants_received DECIMAL(12,2),
                    last_performance_review DATE,
                    performance_rating DECIMAL(3,1),
                    sabbatical_eligible BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id)
                )
            """,
            
            'students': """
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(20) PRIMARY KEY,
                    student_number VARCHAR(20) UNIQUE NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    middle_name VARCHAR(50),
                    date_of_birth DATE,
                    age INTEGER,
                    gender VARCHAR(10),
                    ssn_last4 VARCHAR(4),
                    phone_primary VARCHAR(20),
                    phone_secondary VARCHAR(20),
                    email VARCHAR(100),
                    address_street VARCHAR(100),
                    address_city VARCHAR(50),
                    address_state VARCHAR(5),
                    address_zip VARCHAR(10),
                    emergency_contact_name VARCHAR(100),
                    emergency_contact_relationship VARCHAR(50),
                    emergency_contact_phone VARCHAR(20),
                    major VARCHAR(100),
                    minor VARCHAR(100),
                    class_level VARCHAR(20),
                    enrollment_status VARCHAR(20),
                    gpa DECIMAL(3,2),
                    total_credits INTEGER,
                    credits_current_semester INTEGER,
                    scholarship_amount DECIMAL(12,2),
                    financial_aid_status VARCHAR(50),
                    advisor_id VARCHAR(20),
                    registration_date DATE,
                    expected_graduation DATE,
                    academic_standing VARCHAR(50),
                    residence_hall VARCHAR(50),
                    meal_plan VARCHAR(20),
                    tuition_balance DECIMAL(12,2),
                    academic_probation BOOLEAN,
                    honors_program BOOLEAN,
                    student_activities TEXT,
                    work_study BOOLEAN,
                    internship_status VARCHAR(20),
                    health_insurance BOOLEAN,
                    disability_services BOOLEAN,
                    career_services_visits INTEGER,
                    library_fines DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (advisor_id) REFERENCES faculty(faculty_id)
                )
            """,
            
            'courses': """
                CREATE TABLE IF NOT EXISTS courses (
                    course_id VARCHAR(20) PRIMARY KEY,
                    course_name VARCHAR(100) NOT NULL,
                    course_code VARCHAR(20) NOT NULL,
                    department_id VARCHAR(20),
                    credits INTEGER,
                    course_level VARCHAR(20),
                    semester VARCHAR(20),
                    instructor_id VARCHAR(20),
                    enrollment_limit INTEGER,
                    current_enrollment INTEGER,
                    tuition_per_credit DECIMAL(8,2),
                    prerequisites TEXT,
                    corequisites TEXT,
                    course_description TEXT,
                    meeting_days VARCHAR(20),
                    meeting_time VARCHAR(20),
                    location VARCHAR(50),
                    textbook_required BOOLEAN,
                    lab_required BOOLEAN,
                    field_work_required BOOLEAN,
                    assessment_methods TEXT,
                    grading_scale VARCHAR(50),
                    course_objectives TEXT,
                    accreditation_requirement VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id),
                    FOREIGN KEY (instructor_id) REFERENCES faculty(faculty_id)
                )
            """,
            
            'equipment': """
                CREATE TABLE IF NOT EXISTS equipment (
                    equipment_id VARCHAR(20) PRIMARY KEY,
                    equipment_name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    subcategory VARCHAR(50),
                    manufacturer VARCHAR(100),
                    model_number VARCHAR(50),
                    serial_number VARCHAR(50),
                    purchase_date DATE,
                    warranty_expiry DATE,
                    acquisition_cost DECIMAL(12,2),
                    current_value DECIMAL(12,2),
                    depreciation_rate DECIMAL(3,2),
                    location VARCHAR(100),
                    department_id VARCHAR(20),
                    building_id VARCHAR(20),
                    operational_status VARCHAR(20),
                    last_maintenance_date DATE,
                    next_maintenance_date DATE,
                    maintenance_frequency VARCHAR(20),
                    vendor_contact VARCHAR(100),
                    vendor_phone VARCHAR(20),
                    calibration_required BOOLEAN,
                    calibration_date DATE,
                    usage_hours_total INTEGER,
                    usage_hours_monthly INTEGER,
                    installation_date DATE,
                    training_required BOOLEAN,
                    replacement_due_date DATE,
                    grant_funded BOOLEAN,
                    research_usage BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id),
                    FOREIGN KEY (building_id) REFERENCES buildings(building_id)
                )
            """,
            
            'research_projects': """
                CREATE TABLE IF NOT EXISTS research_projects (
                    project_id VARCHAR(20) PRIMARY KEY,
                    project_title VARCHAR(200) NOT NULL,
                    project_code VARCHAR(50),
                    department_id VARCHAR(20),
                    principal_investigator VARCHAR(20),
                    co_investigators TEXT,
                    funding_agency VARCHAR(100),
                    grant_amount DECIMAL(12,2),
                    start_date DATE,
                    end_date DATE,
                    project_status VARCHAR(20),
                    research_area VARCHAR(100),
                    methodology VARCHAR(100),
                    equipment_required TEXT,
                    participants_needed INTEGER,
                    irb_approval BOOLEAN,
                    publication_count INTEGER,
                    conference_presentations INTEGER,
                    student_researchers INTEGER,
                    budget_spent DECIMAL(12,2),
                    overhead_rate DECIMAL(4,2),
                    collaboration_type VARCHAR(50),
                    expected_outcomes TEXT,
                    deliverables TEXT,
                    risk_level VARCHAR(20),
                    compliance_requirements TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id),
                    FOREIGN KEY (principal_investigator) REFERENCES faculty(faculty_id)
                )
            """,
            
            'forms': """
                CREATE TABLE IF NOT EXISTS forms (
                    form_id VARCHAR(20) PRIMARY KEY,
                    form_name VARCHAR(100) NOT NULL,
                    form_type VARCHAR(50),
                    department_id VARCHAR(20),
                    form_code VARCHAR(50),
                    version VARCHAR(10),
                    status VARCHAR(20),
                    required_fields TEXT,
                    completion_time_minutes INTEGER,
                    digital_format BOOLEAN,
                    paper_format BOOLEAN,
                    multilingual_support VARCHAR(100),
                    last_updated DATE,
                    created_by_employee_id VARCHAR(20),
                    approval_required BOOLEAN,
                    retention_period_years INTEGER,
                    compliance_standards TEXT,
                    usage_frequency_monthly INTEGER,
                    form_description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id),
                    FOREIGN KEY (created_by_employee_id) REFERENCES faculty(faculty_id)
                )
            """
        }
        
        # CSV file mappings
        self.csv_mappings = {
            'departments': 'healthcare_data/university_departments.csv',
            'buildings': 'healthcare_data/university_buildings.csv',
            'faculty': 'healthcare_data/university_faculty.csv',
            'students': 'healthcare_data/university_students.csv',
            'courses': 'healthcare_data/university_courses.csv',
            'equipment': 'healthcare_data/university_equipment.csv',
            'research_projects': 'healthcare_data/university_research.csv',
            'forms': 'healthcare_data/university_forms.csv'
        }
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(self.config.get_connection_string())
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connection established successfully")
            return True
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed")
    
    def create_database(self) -> bool:
        """Create the university database if it doesn't exist"""
        try:
            # Connect to PostgreSQL server (not specific database)
            conn = psycopg2.connect(self.config.get_admin_connection_string())
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.config.database,))
            if cursor.fetchone():
                logger.info(f"Database {self.config.database} already exists")
            else:
                # Create database
                cursor.execute(f"CREATE DATABASE {self.config.database}")
                logger.info(f"Database {self.config.database} created successfully")
            
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Failed to create database: {e}")
            return False
    
    def initialize_schema(self) -> bool:
        """Initialize database schema with all tables"""
        try:
            if not self.connect():
                return False
            
            # Create tables in order (respecting foreign key dependencies)
            table_order = ['departments', 'buildings', 'faculty', 'students', 'courses', 'equipment', 'research_projects', 'forms']
            
            for table_name in table_order:
                if table_name in self.table_schemas:
                    self.cursor.execute(self.table_schemas[table_name])
                    logger.info(f"Created table: {table_name}")
            
            # Create indexes for better performance
            self.create_indexes()
            
            self.connection.commit()
            logger.info("Database schema initialized successfully")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize schema: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def create_indexes(self) -> None:
        """Create indexes for better query performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_faculty_department ON faculty(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_students_advisor ON students(advisor_id)",
            "CREATE INDEX IF NOT EXISTS idx_courses_department ON courses(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_courses_instructor ON courses(instructor_id)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_department ON equipment(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_building ON equipment(building_id)",
            "CREATE INDEX IF NOT EXISTS idx_research_department ON research_projects(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_research_pi ON research_projects(principal_investigator)",
            "CREATE INDEX IF NOT EXISTS idx_forms_department ON forms(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_forms_creator ON forms(created_by_employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_students_email ON students(email)",
            "CREATE INDEX IF NOT EXISTS idx_faculty_email ON faculty(email)",
            "CREATE INDEX IF NOT EXISTS idx_students_major ON students(major)",
            "CREATE INDEX IF NOT EXISTS idx_faculty_position ON faculty(position)",
            "CREATE INDEX IF NOT EXISTS idx_courses_level ON courses(course_level)",
            "CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(operational_status)",
            "CREATE INDEX IF NOT EXISTS idx_research_status ON research_projects(project_status)",
            "CREATE INDEX IF NOT EXISTS idx_forms_type ON forms(form_type)"
        ]
        
        for index_sql in indexes:
            self.cursor.execute(index_sql)
    
    def parse_csv_value(self, value: str, field_type: str) -> Any:
        """Parse CSV value according to field type"""
        if not value or value.strip() == '':
            return None
        
        value = value.strip()
        
        if field_type == 'boolean':
            return value.lower() in ('yes', 'true', '1', 'y')
        elif field_type == 'integer':
            try:
                return int(value)
            except ValueError:
                return None
        elif field_type == 'decimal':
            try:
                return float(value)
            except ValueError:
                return None
        elif field_type == 'date':
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return None
        else:
            return value
    
    def load_csv_data(self, base_path: str = "FimeHacks") -> bool:
        """Load data from CSV files into database tables"""
        try:
            if not self.connect():
                return False
            
            # Clear existing data
            self.clear_all_tables()
            
            # Load data in order (respecting foreign key dependencies)
            load_order = ['departments', 'buildings', 'faculty', 'students', 'courses', 'equipment', 'research_projects', 'forms']
            
            for table_name in load_order:
                csv_file = os.path.join(base_path, self.csv_mappings[table_name])
                if os.path.exists(csv_file):
                    self.load_table_from_csv(table_name, csv_file)
                else:
                    logger.warning(f"CSV file not found: {csv_file}")
            
            self.connection.commit()
            logger.info("All CSV data loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load CSV data: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def load_table_from_csv(self, table_name: str, csv_file: str) -> None:
        """Load data from a specific CSV file into a table"""
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            
            if not rows:
                logger.warning(f"No data found in {csv_file}")
                return
            
            # Get column names from CSV
            columns = list(rows[0].keys())
            
            # Create INSERT query
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insert data
            for row in rows:
                values = []
                for column in columns:
                    value = row[column]
                    # Basic type conversion based on common patterns
                    if column.endswith('_date') or column in ['hire_date', 'birth_date', 'purchase_date', 'warranty_expiry']:
                        value = self.parse_csv_value(value, 'date')
                    elif column.endswith('_amount') or column.endswith('_cost') or column.endswith('_salary') or column.endswith('_budget'):
                        value = self.parse_csv_value(value, 'decimal')
                    elif column.endswith('_count') or column.endswith('_limit') or column == 'age' or column == 'credits':
                        value = self.parse_csv_value(value, 'integer')
                    elif column.endswith('_active') or column.endswith('_required') or column.endswith('_eligible'):
                        value = self.parse_csv_value(value, 'boolean')
                    elif value == '':
                        value = None
                    
                    values.append(value)
                
                try:
                    self.cursor.execute(insert_query, values)
                except psycopg2.Error as e:
                    logger.warning(f"Failed to insert row in {table_name}: {e}")
                    continue
            
            logger.info(f"Loaded {len(rows)} rows into {table_name}")
    
    def clear_all_tables(self) -> None:
        """Clear all tables in reverse order of dependencies"""
        clear_order = ['forms', 'research_projects', 'equipment', 'courses', 'students', 'faculty', 'buildings', 'departments']
        
        for table_name in clear_order:
            self.cursor.execute(f"DELETE FROM {table_name}")
            logger.info(f"Cleared table: {table_name}")
    
    # Database query methods
    def get_all_departments(self) -> List[Dict]:
        """Get all departments"""
        self.cursor.execute("SELECT * FROM departments ORDER BY department_name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_department_by_id(self, department_id: str) -> Optional[Dict]:
        """Get department by ID"""
        self.cursor.execute("SELECT * FROM departments WHERE department_id = %s", (department_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_faculty_by_department(self, department_id: str) -> List[Dict]:
        """Get faculty members by department"""
        self.cursor.execute("""
            SELECT f.*, d.department_name 
            FROM faculty f 
            JOIN departments d ON f.department_id = d.department_id 
            WHERE f.department_id = %s 
            ORDER BY f.last_name, f.first_name
        """, (department_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_students_by_major(self, major: str) -> List[Dict]:
        """Get students by major"""
        self.cursor.execute("""
            SELECT * FROM students 
            WHERE major ILIKE %s 
            ORDER BY last_name, first_name
        """, (f"%{major}%",))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_courses_by_department(self, department_id: str) -> List[Dict]:
        """Get courses by department"""
        self.cursor.execute("""
            SELECT c.*, f.first_name || ' ' || f.last_name as instructor_name 
            FROM courses c 
            LEFT JOIN faculty f ON c.instructor_id = f.faculty_id 
            WHERE c.department_id = %s 
            ORDER BY c.course_code
        """, (department_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_equipment_by_department(self, department_id: str) -> List[Dict]:
        """Get equipment by department"""
        self.cursor.execute("""
            SELECT e.*, d.department_name, b.building_name 
            FROM equipment e 
            JOIN departments d ON e.department_id = d.department_id 
            LEFT JOIN buildings b ON e.building_id = b.building_id 
            WHERE e.department_id = %s 
            ORDER BY e.equipment_name
        """, (department_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_research_by_department(self, department_id: str) -> List[Dict]:
        """Get research projects by department"""
        self.cursor.execute("""
            SELECT r.*, d.department_name, 
                   f.first_name || ' ' || f.last_name as pi_name 
            FROM research_projects r 
            JOIN departments d ON r.department_id = d.department_id 
            LEFT JOIN faculty f ON r.principal_investigator = f.faculty_id 
            WHERE r.department_id = %s 
            ORDER BY r.start_date DESC
        """, (department_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_forms_by_type(self, form_type: str) -> List[Dict]:
        """Get forms by type"""
        self.cursor.execute("""
            SELECT f.*, d.department_name 
            FROM forms f 
            LEFT JOIN departments d ON f.department_id = d.department_id 
            WHERE f.form_type = %s 
            ORDER BY f.form_name
        """, (form_type,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_student_enrollment_stats(self) -> Dict:
        """Get student enrollment statistics"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_students,
                COUNT(CASE WHEN enrollment_status = 'Full-Time' THEN 1 END) as full_time,
                COUNT(CASE WHEN enrollment_status = 'Part-Time' THEN 1 END) as part_time,
                AVG(gpa) as average_gpa,
                COUNT(CASE WHEN academic_probation = true THEN 1 END) as on_probation
            FROM students
        """)
        return dict(self.cursor.fetchone())
    
    def get_faculty_stats(self) -> Dict:
        """Get faculty statistics"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_faculty,
                COUNT(CASE WHEN tenure_status = 'Tenured' THEN 1 END) as tenured,
                COUNT(CASE WHEN tenure_status = 'Tenure-Track' THEN 1 END) as tenure_track,
                AVG(annual_salary) as average_salary,
                COUNT(CASE WHEN research_active = true THEN 1 END) as research_active
            FROM faculty
        """)
        return dict(self.cursor.fetchone())
    
    def get_research_stats(self) -> Dict:
        """Get research statistics"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_projects,
                COUNT(CASE WHEN project_status = 'Active' THEN 1 END) as active_projects,
                SUM(grant_amount) as total_funding,
                AVG(grant_amount) as average_funding,
                COUNT(CASE WHEN irb_approval = true THEN 1 END) as irb_approved
            FROM research_projects
        """)
        return dict(self.cursor.fetchone())
    
    def search_students(self, query: str) -> List[Dict]:
        """Search students by name or email"""
        self.cursor.execute("""
            SELECT * FROM students 
            WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s
            ORDER BY last_name, first_name
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_faculty(self, query: str) -> List[Dict]:
        """Search faculty by name or email"""
        self.cursor.execute("""
            SELECT f.*, d.department_name 
            FROM faculty f 
            JOIN departments d ON f.department_id = d.department_id 
            WHERE f.first_name ILIKE %s OR f.last_name ILIKE %s OR f.email ILIKE %s
            ORDER BY f.last_name, f.first_name
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_research_projects(self, query: str) -> List[Dict]:
        """Search research projects by title or research area"""
        self.cursor.execute("""
            SELECT r.*, d.department_name, 
                   f.first_name || ' ' || f.last_name as pi_name 
            FROM research_projects r 
            JOIN departments d ON r.department_id = d.department_id 
            LEFT JOIN faculty f ON r.principal_investigator = f.faculty_id 
            WHERE r.project_title ILIKE %s OR r.research_area ILIKE %s
            ORDER BY r.start_date DESC
        """, (f"%{query}%", f"%{query}%"))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_database_summary(self) -> Dict:
        """Get summary statistics for the entire database"""
        summary = {}
        
        tables = ['departments', 'faculty', 'students', 'courses', 'equipment', 'buildings', 'research_projects', 'forms']
        
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            summary[f"{table}_count"] = self.cursor.fetchone()[0]
        
        return summary
    
    def close(self) -> None:
        """Close database connection"""
        self.disconnect()


def main():
    """Main function to demonstrate database usage"""
    # Initialize database configuration
    config = DatabaseConfig(
        host="localhost",
        port=5432,
        database="university_db",
        username="postgres",
        password="password"
    )
    
    # Create database instance
    db = UniversityPostgreDB(config)
    
    try:
        # Create database if it doesn't exist
        print("Creating database...")
        db.create_database()
        
        # Initialize schema
        print("Initializing schema...")
        db.initialize_schema()
        
        # Load data from CSV files
        print("Loading CSV data...")
        db.load_csv_data()
        
        # Test some queries
        print("\n=== Database Summary ===")
        summary = db.get_database_summary()
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        print("\n=== Student Enrollment Stats ===")
        stats = db.get_student_enrollment_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        print("\n=== Faculty Stats ===")
        faculty_stats = db.get_faculty_stats()
        for key, value in faculty_stats.items():
            print(f"{key}: {value}")
        
        print("\n=== Research Stats ===")
        research_stats = db.get_research_stats()
        for key, value in research_stats.items():
            print(f"{key}: {value}")
        
        print("\n=== Sample Departments ===")
        departments = db.get_all_departments()[:5]  # Show first 5
        for dept in departments:
            print(f"{dept['department_code']}: {dept['department_name']}")
        
        print("\nDatabase initialization and data loading completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
