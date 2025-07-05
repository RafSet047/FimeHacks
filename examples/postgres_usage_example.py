#!/usr/bin/env python3
"""
PostgreSQL Database Usage Example

This script demonstrates how to use the UniversityPostgreDB class
to set up and work with the university database.
"""

import os
import sys
from pprint import pprint

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.postgre_db import UniversityPostgreDB, DatabaseConfig


def main():
    """Demonstrate PostgreSQL database usage"""
    
    print("=== University PostgreSQL Database Usage Example ===\n")
    
    # 1. Configure database connection
    print("1. Configuring database connection...")
    
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
        print(f"   Using configuration from database_config.py")
    except ImportError:
        # Use default configuration
        config = DatabaseConfig(
            host="localhost",          # PostgreSQL server host
            port=5432,                # Default PostgreSQL port
            database="fimehacks_db",   # Database name
            username="fimehacks_user", # Your PostgreSQL username
            password="fimehacks_password" # Your PostgreSQL password
        )
        print(f"   Using default configuration")
        print(f"   💡 Run 'python setup_postgres.py' to create a custom configuration")
    
    # Initialize database manager
    db = UniversityPostgreDB(config)
    
    try:
        # 2. Create database and initialize schema
        print("2. Creating database and initializing schema...")
        
        # Create database if it doesn't exist
        if not db.create_database():
            print("Failed to create database")
            return
        
        # Initialize schema (create tables)
        if not db.initialize_schema():
            print("Failed to initialize schema")
            return
        
        print("✓ Database and schema created successfully")
        
        # 3. Load data from CSV files
        print("\n3. Loading data from CSV files...")
        
        # Load all CSV data
        if not db.load_csv_data():
            print("Failed to load CSV data")
            return
        
        print("✓ CSV data loaded successfully")
        
        # 4. Database summary
        print("\n4. Database Summary:")
        print("-" * 40)
        
        summary = db.get_database_summary()
        for key, value in summary.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        # 5. Student statistics
        print("\n5. Student Enrollment Statistics:")
        print("-" * 40)
        
        student_stats = db.get_student_enrollment_stats()
        for key, value in student_stats.items():
            if isinstance(value, float):
                print(f"{key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # 6. Faculty statistics
        print("\n6. Faculty Statistics:")
        print("-" * 40)
        
        faculty_stats = db.get_faculty_stats()
        for key, value in faculty_stats.items():
            if isinstance(value, float):
                print(f"{key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # 7. Research statistics
        print("\n7. Research Statistics:")
        print("-" * 40)
        
        research_stats = db.get_research_stats()
        for key, value in research_stats.items():
            if isinstance(value, float):
                print(f"{key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # 8. Sample department queries
        print("\n8. Sample Department Information:")
        print("-" * 40)
        
        departments = db.get_all_departments()[:3]  # Show first 3 departments
        for dept in departments:
            print(f"\n{dept['department_name']} ({dept['department_code']})")
            print(f"  College: {dept['college']}")
            print(f"  Building: {dept['building']}")
            print(f"  Faculty Count: {dept['faculty_count']}")
            print(f"  Annual Budget: ${dept['annual_budget']:,.2f}")
            print(f"  Research Active: {dept['research_active']}")
        
        # 9. Sample faculty queries
        print("\n9. Sample Faculty by Department:")
        print("-" * 40)
        
        # Get faculty from Computer Science department
        cs_faculty = db.get_faculty_by_department('DEPT001')
        print(f"Computer Science Faculty ({len(cs_faculty)} members):")
        for faculty in cs_faculty[:3]:  # Show first 3
            print(f"  - {faculty['first_name']} {faculty['last_name']}")
            print(f"    Position: {faculty['position']}")
            print(f"    Specialization: {faculty['specialization']}")
            print(f"    Tenure Status: {faculty['tenure_status']}")
        
        # 10. Sample student queries
        print("\n10. Sample Student Searches:")
        print("-" * 40)
        
        # Search students by major
        cs_students = db.get_students_by_major('Computer Science')
        print(f"Computer Science Students ({len(cs_students)} found):")
        for student in cs_students[:3]:  # Show first 3
            print(f"  - {student['first_name']} {student['last_name']}")
            print(f"    Class Level: {student['class_level']}")
            print(f"    GPA: {student['gpa']}")
            print(f"    Academic Standing: {student['academic_standing']}")
        
        # 11. Sample course queries
        print("\n11. Sample Courses by Department:")
        print("-" * 40)
        
        cs_courses = db.get_courses_by_department('DEPT001')
        print(f"Computer Science Courses ({len(cs_courses)} found):")
        for course in cs_courses[:3]:  # Show first 3
            print(f"  - {course['course_code']}: {course['course_name']}")
            print(f"    Credits: {course['credits']}")
            print(f"    Level: {course['course_level']}")
            print(f"    Instructor: {course['instructor_name']}")
        
        # 12. Sample equipment queries
        print("\n12. Sample Equipment by Department:")
        print("-" * 40)
        
        cs_equipment = db.get_equipment_by_department('DEPT001')
        print(f"Computer Science Equipment ({len(cs_equipment)} items):")
        for equipment in cs_equipment[:3]:  # Show first 3
            print(f"  - {equipment['equipment_name']}")
            print(f"    Category: {equipment['category']}")
            print(f"    Status: {equipment['operational_status']}")
            print(f"    Current Value: ${equipment['current_value']:,.2f}")
        
        # 13. Sample research queries
        print("\n13. Sample Research Projects:")
        print("-" * 40)
        
        cs_research = db.get_research_by_department('DEPT001')
        print(f"Computer Science Research ({len(cs_research)} projects):")
        for project in cs_research[:2]:  # Show first 2
            print(f"  - {project['project_title']}")
            print(f"    PI: {project['pi_name']}")
            print(f"    Status: {project['project_status']}")
            print(f"    Grant Amount: ${project['grant_amount']:,.2f}")
            print(f"    Research Area: {project['research_area']}")
        
        # 14. Sample form queries
        print("\n14. Sample Forms by Type:")
        print("-" * 40)
        
        academic_forms = db.get_forms_by_type('Academic')
        print(f"Academic Forms ({len(academic_forms)} found):")
        for form in academic_forms[:3]:  # Show first 3
            print(f"  - {form['form_name']}")
            print(f"    Code: {form['form_code']}")
            print(f"    Status: {form['status']}")
            print(f"    Completion Time: {form['completion_time_minutes']} minutes")
        
        # 15. Sample search functions
        print("\n15. Sample Search Functions:")
        print("-" * 40)
        
        # Search students by name
        students = db.search_students('John')
        print(f"Students named 'John' ({len(students)} found):")
        for student in students[:2]:  # Show first 2
            print(f"  - {student['first_name']} {student['last_name']}")
            print(f"    Email: {student['email']}")
            print(f"    Major: {student['major']}")
        
        # Search faculty by name
        faculty = db.search_faculty('Sarah')
        print(f"\nFaculty named 'Sarah' ({len(faculty)} found):")
        for fac in faculty[:2]:  # Show first 2
            print(f"  - {fac['first_name']} {fac['last_name']}")
            print(f"    Department: {fac['department_name']}")
            print(f"    Position: {fac['position']}")
        
        # Search research projects
        research = db.search_research_projects('Machine Learning')
        print(f"\nResearch projects with 'Machine Learning' ({len(research)} found):")
        for proj in research[:2]:  # Show first 2
            print(f"  - {proj['project_title']}")
            print(f"    PI: {proj['pi_name']}")
            print(f"    Funding: ${proj['grant_amount']:,.2f}")
        
        print("\n" + "=" * 60)
        print("✓ Database demonstration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during database operations: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Always close the database connection
        db.close()


def show_connection_help():
    """Show help for database connection setup"""
    print("\n=== Database Connection Setup Help ===")
    print("\nBefore running this example, make sure:")
    print("1. PostgreSQL is installed and running")
    print("2. You have created a PostgreSQL user with appropriate permissions")
    print("3. Update the database configuration in this script:")
    print("   - host: Your PostgreSQL server host (default: localhost)")
    print("   - port: Your PostgreSQL port (default: 5432)")
    print("   - username: Your PostgreSQL username")
    print("   - password: Your PostgreSQL password")
    print("\nExample PostgreSQL setup commands:")
    print("   sudo -u postgres psql")
    print("   CREATE USER your_username WITH PASSWORD 'your_password';")
    print("   ALTER USER your_username CREATEDB;")
    print("   \\q")
    print("\nInstall required packages:")
    print("   pip install -r requirements_postgres.txt")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_connection_help()
    else:
        main() 