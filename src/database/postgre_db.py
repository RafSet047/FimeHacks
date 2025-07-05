#!/usr/bin/env python3
"""
PostgreSQL Database Module for University Data

This module provides a simple interface for working with university data
in a PostgreSQL database.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "university_db"
    username: str = "postgres"
    password: str = "password"

class UniversityPostgreDB:
    """PostgreSQL database manager for university data"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            # First connect to default database to create our database
            conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database="postgres",
                user=self.config.username,
                password=self.config.password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if our database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.config.database,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.config.database}")
                logger.info(f"Created database: {self.config.database}")
            
            cursor.close()
            conn.close()
            
            # Now connect to our database
            self.connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            logger.info(f"Connected to database: {self.config.database}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def create_database(self) -> bool:
        """Create the database if it doesn't exist"""
        return self.connect()
    
    def initialize_schema(self) -> bool:
        """Initialize database schema with tables"""
        try:
            # Create tables
            tables = [
                """
                CREATE TABLE IF NOT EXISTS departments (
                    department_id VARCHAR(10) PRIMARY KEY,
                    department_name VARCHAR(100) NOT NULL,
                    department_code VARCHAR(10) UNIQUE NOT NULL,
                    college VARCHAR(100),
                    building VARCHAR(50),
                    faculty_count INTEGER DEFAULT 0,
                    annual_budget DECIMAL(12,2) DEFAULT 0,
                    research_active BOOLEAN DEFAULT TRUE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS faculty (
                    faculty_id VARCHAR(10) PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    department_id VARCHAR(10) REFERENCES departments(department_id),
                    position VARCHAR(100),
                    specialization TEXT,
                    tenure_status VARCHAR(20),
                    hire_date DATE,
                    salary DECIMAL(10,2)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_id VARCHAR(10) PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    major VARCHAR(100),
                    class_level VARCHAR(20),
                    gpa DECIMAL(3,2),
                    academic_standing VARCHAR(20),
                    enrollment_date DATE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS courses (
                    course_id VARCHAR(10) PRIMARY KEY,
                    course_code VARCHAR(20) UNIQUE NOT NULL,
                    course_name VARCHAR(200) NOT NULL,
                    department_id VARCHAR(10) REFERENCES departments(department_id),
                    credits INTEGER,
                    course_level VARCHAR(20),
                    instructor_name VARCHAR(100)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS equipment (
                    equipment_id VARCHAR(10) PRIMARY KEY,
                    equipment_name VARCHAR(200) NOT NULL,
                    department_id VARCHAR(10) REFERENCES departments(department_id),
                    category VARCHAR(100),
                    operational_status VARCHAR(20),
                    current_value DECIMAL(10,2),
                    acquisition_date DATE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS research_projects (
                    project_id VARCHAR(10) PRIMARY KEY,
                    project_title VARCHAR(300) NOT NULL,
                    pi_name VARCHAR(100),
                    department_id VARCHAR(10) REFERENCES departments(department_id),
                    project_status VARCHAR(20),
                    grant_amount DECIMAL(12,2),
                    research_area VARCHAR(200),
                    start_date DATE,
                    end_date DATE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS forms (
                    form_id VARCHAR(10) PRIMARY KEY,
                    form_name VARCHAR(200) NOT NULL,
                    form_code VARCHAR(20) UNIQUE,
                    form_type VARCHAR(50),
                    status VARCHAR(20),
                    completion_time_minutes INTEGER,
                    department_id VARCHAR(10) REFERENCES departments(department_id)
                )
                """
            ]
            
            for table_sql in tables:
                self.cursor.execute(table_sql)
            
            self.connection.commit()
            logger.info("Database schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            return False
    
    def load_csv_data(self) -> bool:
        """Load sample data from CSV files or create sample data"""
        try:
            # Create sample data
            sample_data = {
                'departments': [
                    ('DEPT001', 'Computer Science', 'CS', 'Engineering', 'Science Hall', 15, 2500000.00, True),
                    ('DEPT002', 'Mathematics', 'MATH', 'Arts & Sciences', 'Math Building', 12, 1800000.00, True),
                    ('DEPT003', 'Physics', 'PHYS', 'Arts & Sciences', 'Physics Lab', 10, 2200000.00, True)
                ],
                'faculty': [
                    ('FAC001', 'John', 'Smith', 'john.smith@university.edu', 'DEPT001', 'Professor', 'Machine Learning', 'Tenured', '2010-01-15', 85000.00),
                    ('FAC002', 'Sarah', 'Johnson', 'sarah.johnson@university.edu', 'DEPT001', 'Associate Professor', 'Database Systems', 'Tenure Track', '2015-03-20', 75000.00),
                    ('FAC003', 'Michael', 'Brown', 'michael.brown@university.edu', 'DEPT002', 'Professor', 'Applied Mathematics', 'Tenured', '2008-09-01', 90000.00)
                ],
                'students': [
                    ('STU001', 'Alice', 'Wilson', 'alice.wilson@student.edu', 'Computer Science', 'Senior', 3.85, 'Good Standing', '2020-08-15'),
                    ('STU002', 'Bob', 'Davis', 'bob.davis@student.edu', 'Computer Science', 'Junior', 3.45, 'Good Standing', '2021-01-10'),
                    ('STU003', 'Carol', 'Miller', 'carol.miller@student.edu', 'Mathematics', 'Senior', 3.92, 'Good Standing', '2020-08-15')
                ],
                'courses': [
                    ('CRS001', 'CS101', 'Introduction to Computer Science', 'DEPT001', 3, 'Undergraduate', 'Dr. John Smith'),
                    ('CRS002', 'CS201', 'Data Structures', 'DEPT001', 3, 'Undergraduate', 'Dr. Sarah Johnson'),
                    ('CRS003', 'MATH101', 'Calculus I', 'DEPT002', 4, 'Undergraduate', 'Dr. Michael Brown')
                ],
                'equipment': [
                    ('EQP001', 'High-Performance Computing Cluster', 'DEPT001', 'Computing', 'Operational', 500000.00, '2022-01-15'),
                    ('EQP002', 'Advanced Microscope', 'DEPT003', 'Laboratory', 'Operational', 150000.00, '2021-06-20'),
                    ('EQP003', '3D Printer', 'DEPT001', 'Manufacturing', 'Maintenance', 25000.00, '2023-03-10')
                ],
                'research_projects': [
                    ('RES001', 'Machine Learning for Healthcare', 'Dr. John Smith', 'DEPT001', 'Active', 500000.00, 'Machine Learning', '2023-01-01', '2025-12-31'),
                    ('RES002', 'Quantum Computing Applications', 'Dr. Sarah Johnson', 'DEPT001', 'Active', 750000.00, 'Quantum Computing', '2023-06-01', '2026-05-31'),
                    ('RES003', 'Mathematical Modeling of Climate Change', 'Dr. Michael Brown', 'DEPT002', 'Active', 300000.00, 'Applied Mathematics', '2023-03-01', '2025-02-28')
                ],
                'forms': [
                    ('FRM001', 'Course Registration Form', 'CRF001', 'Academic', 'Active', 15, 'DEPT001'),
                    ('FRM002', 'Research Grant Application', 'RGA001', 'Research', 'Active', 60, 'DEPT001'),
                    ('FRM003', 'Equipment Request Form', 'ERF001', 'Administrative', 'Active', 30, 'DEPT001')
                ]
            }
            
            # Insert sample data
            for table, data in sample_data.items():
                if table == 'departments':
                    self.cursor.executemany(
                        "INSERT INTO departments VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        data
                    )
                elif table == 'faculty':
                    self.cursor.executemany(
                        "INSERT INTO faculty VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        data
                    )
                elif table == 'students':
                    self.cursor.executemany(
                        "INSERT INTO students VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        data
                    )
                elif table == 'courses':
                    self.cursor.executemany(
                        "INSERT INTO courses VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        data
                    )
                elif table == 'equipment':
                    self.cursor.executemany(
                        "INSERT INTO equipment VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        data
                    )
                elif table == 'research_projects':
                    self.cursor.executemany(
                        "INSERT INTO research_projects VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        data
                    )
                elif table == 'forms':
                    self.cursor.executemany(
                        "INSERT INTO forms VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        data
                    )
            
            self.connection.commit()
            logger.info("Sample data loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load sample data: {e}")
            return False
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Get database summary statistics"""
        try:
            summary = {}
            
            # Count records in each table
            tables = ['departments', 'faculty', 'students', 'courses', 'equipment', 'research_projects', 'forms']
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()['count']
                summary[f'{table}_count'] = count
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get database summary: {e}")
            return {}
    
    def get_student_enrollment_stats(self) -> Dict[str, Any]:
        """Get student enrollment statistics"""
        try:
            stats = {}
            
            # Total students
            self.cursor.execute("SELECT COUNT(*) as total FROM students")
            stats['total_students'] = self.cursor.fetchone()['total']
            
            # Average GPA
            self.cursor.execute("SELECT AVG(gpa) as avg_gpa FROM students")
            stats['average_gpa'] = self.cursor.fetchone()['avg_gpa'] or 0.0
            
            # Students by major
            self.cursor.execute("SELECT major, COUNT(*) as count FROM students GROUP BY major")
            major_counts = self.cursor.fetchall()
            stats['students_by_major'] = {row['major']: row['count'] for row in major_counts}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get student stats: {e}")
            return {}
    
    def get_faculty_stats(self) -> Dict[str, Any]:
        """Get faculty statistics"""
        try:
            stats = {}
            
            # Total faculty
            self.cursor.execute("SELECT COUNT(*) as total FROM faculty")
            stats['total_faculty'] = self.cursor.fetchone()['total']
            
            # Average salary
            self.cursor.execute("SELECT AVG(salary) as avg_salary FROM faculty")
            stats['average_salary'] = self.cursor.fetchone()['avg_salary'] or 0.0
            
            # Faculty by department
            self.cursor.execute("""
                SELECT d.department_name, COUNT(f.faculty_id) as count 
                FROM departments d 
                LEFT JOIN faculty f ON d.department_id = f.department_id 
                GROUP BY d.department_id, d.department_name
            """)
            dept_counts = self.cursor.fetchall()
            stats['faculty_by_department'] = {row['department_name']: row['count'] for row in dept_counts}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get faculty stats: {e}")
            return {}
    
    def get_research_stats(self) -> Dict[str, Any]:
        """Get research statistics"""
        try:
            stats = {}
            
            # Total projects
            self.cursor.execute("SELECT COUNT(*) as total FROM research_projects")
            stats['total_projects'] = self.cursor.fetchone()['total']
            
            # Total funding
            self.cursor.execute("SELECT SUM(grant_amount) as total_funding FROM research_projects")
            stats['total_funding'] = self.cursor.fetchone()['total_funding'] or 0.0
            
            # Projects by status
            self.cursor.execute("SELECT project_status, COUNT(*) as count FROM research_projects GROUP BY project_status")
            status_counts = self.cursor.fetchall()
            stats['projects_by_status'] = {row['project_status']: row['count'] for row in status_counts}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get research stats: {e}")
            return {}
    
    def get_all_departments(self) -> List[Dict[str, Any]]:
        """Get all departments"""
        try:
            self.cursor.execute("SELECT * FROM departments ORDER BY department_name")
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get departments: {e}")
            return []
    
    def get_faculty_by_department(self, department_id: str) -> List[Dict[str, Any]]:
        """Get faculty by department"""
        try:
            self.cursor.execute("""
                SELECT f.*, d.department_name 
                FROM faculty f 
                JOIN departments d ON f.department_id = d.department_id 
                WHERE f.department_id = %s
            """, (department_id,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get faculty by department: {e}")
            return []
    
    def get_students_by_major(self, major: str) -> List[Dict[str, Any]]:
        """Get students by major"""
        try:
            self.cursor.execute("SELECT * FROM students WHERE major = %s", (major,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get students by major: {e}")
            return []
    
    def get_courses_by_department(self, department_id: str) -> List[Dict[str, Any]]:
        """Get courses by department"""
        try:
            self.cursor.execute("SELECT * FROM courses WHERE department_id = %s", (department_id,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get courses by department: {e}")
            return []
    
    def get_equipment_by_department(self, department_id: str) -> List[Dict[str, Any]]:
        """Get equipment by department"""
        try:
            self.cursor.execute("SELECT * FROM equipment WHERE department_id = %s", (department_id,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get equipment by department: {e}")
            return []
    
    def get_research_by_department(self, department_id: str) -> List[Dict[str, Any]]:
        """Get research projects by department"""
        try:
            self.cursor.execute("SELECT * FROM research_projects WHERE department_id = %s", (department_id,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get research by department: {e}")
            return []
    
    def get_forms_by_type(self, form_type: str) -> List[Dict[str, Any]]:
        """Get forms by type"""
        try:
            self.cursor.execute("SELECT * FROM forms WHERE form_type = %s", (form_type,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get forms by type: {e}")
            return []
    
    def search_students(self, search_term: str) -> List[Dict[str, Any]]:
        """Search students by name"""
        try:
            self.cursor.execute("""
                SELECT * FROM students 
                WHERE first_name ILIKE %s OR last_name ILIKE %s
            """, (f'%{search_term}%', f'%{search_term}%'))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to search students: {e}")
            return []
    
    def search_faculty(self, search_term: str) -> List[Dict[str, Any]]:
        """Search faculty by name"""
        try:
            self.cursor.execute("""
                SELECT f.*, d.department_name 
                FROM faculty f 
                JOIN departments d ON f.department_id = d.department_id 
                WHERE f.first_name ILIKE %s OR f.last_name ILIKE %s
            """, (f'%{search_term}%', f'%{search_term}%'))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to search faculty: {e}")
            return []
    
    def search_research_projects(self, search_term: str) -> List[Dict[str, Any]]:
        """Search research projects"""
        try:
            self.cursor.execute("""
                SELECT * FROM research_projects 
                WHERE project_title ILIKE %s OR research_area ILIKE %s
            """, (f'%{search_term}%', f'%{search_term}%'))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to search research projects: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

