# University PostgreSQL Database Implementation

This module provides a comprehensive PostgreSQL database implementation for managing university data, including automatic schema initialization, CSV data loading, and a rich set of query functions.

## Features

- **Automatic Database Creation**: Creates PostgreSQL database if it doesn't exist
- **Schema Management**: Initializes predefined database schema with proper relationships
- **CSV Data Loading**: Automatically loads data from CSV files with type conversion
- **Rich Query Interface**: Provides numerous query methods for different data types
- **Data Integrity**: Implements foreign key constraints and indexes for performance
- **Search Functions**: Full-text search capabilities across different entities
- **Statistics**: Built-in statistical analysis functions

## Database Schema

The database includes the following tables:

### Core Tables
- **departments**: University departments with budget, faculty count, and research info
- **buildings**: Campus buildings with capacity, maintenance, and facility details
- **faculty**: Faculty members with positions, salaries, and research activity
- **students**: Student records with academic and personal information
- **courses**: Course catalog with prerequisites, schedules, and enrollment
- **equipment**: Laboratory and academic equipment with maintenance tracking

### Extended Tables
- **research_projects**: Research projects with funding, timelines, and outcomes
- **forms**: Administrative forms with completion times and compliance requirements

## Installation

### Prerequisites

1. **PostgreSQL Installation**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   
   # macOS (using Homebrew)
   brew install postgresql
   
   # Start PostgreSQL service
   sudo systemctl start postgresql    # Linux
   brew services start postgresql     # macOS
   ```

2. **Python Dependencies**
   ```bash
   pip install -r requirements_postgres.txt
   ```

### Database Setup

1. **Create PostgreSQL User**
   ```sql
   sudo -u postgres psql
   CREATE USER your_username WITH PASSWORD 'your_password';
   ALTER USER your_username CREATEDB;
   GRANT ALL PRIVILEGES ON DATABASE university_db TO your_username;
   \q
   ```

2. **Update Configuration**
   
   Edit the database configuration in your code:
   ```python
   config = DatabaseConfig(
       host="localhost",
       port=5432,
       database="university_db",
       username="your_username",
       password="your_password"
   )
   ```

## Usage

### Quick Start

```python
from database.postgre_db import UniversityPostgreDB, DatabaseConfig

# Configure database connection
config = DatabaseConfig(
    host="localhost",
    port=5432,
    database="university_db",
    username="your_username",
    password="your_password"
)

# Initialize database
db = UniversityPostgreDB(config)

# Create database and schema
db.create_database()
db.initialize_schema()

# Load CSV data
db.load_csv_data()

# Query data
departments = db.get_all_departments()
students = db.get_students_by_major('Computer Science')

# Close connection
db.close()
```

### Running the Example

```bash
# Run the comprehensive example
python src/database/postgres_usage_example.py

# Get setup help
python src/database/postgres_usage_example.py --help
```

## Available Methods

### Database Management
- `create_database()`: Create database if it doesn't exist
- `initialize_schema()`: Create all tables and indexes
- `load_csv_data()`: Load data from CSV files
- `clear_all_tables()`: Clear all data from tables

### Department Queries
- `get_all_departments()`: Get all departments
- `get_department_by_id(department_id)`: Get specific department
- `get_faculty_by_department(department_id)`: Get faculty in department
- `get_courses_by_department(department_id)`: Get courses in department
- `get_equipment_by_department(department_id)`: Get equipment in department
- `get_research_by_department(department_id)`: Get research projects in department

### Student Queries
- `get_students_by_major(major)`: Get students by major
- `search_students(query)`: Search students by name or email
- `get_student_enrollment_stats()`: Get enrollment statistics

### Faculty Queries
- `search_faculty(query)`: Search faculty by name or email
- `get_faculty_stats()`: Get faculty statistics

### Course and Equipment Queries
- `get_courses_by_department(department_id)`: Get courses by department
- `get_equipment_by_department(department_id)`: Get equipment by department

### Research Queries
- `get_research_by_department(department_id)`: Get research projects
- `search_research_projects(query)`: Search research projects
- `get_research_stats()`: Get research statistics

### Form Queries
- `get_forms_by_type(form_type)`: Get forms by type

### Statistics
- `get_database_summary()`: Get record counts for all tables
- `get_student_enrollment_stats()`: Student enrollment statistics
- `get_faculty_stats()`: Faculty statistics
- `get_research_stats()`: Research project statistics

## Data Types and CSV Mapping

The system automatically maps CSV files to database tables:

| CSV File | Database Table | Description |
|----------|---------------|-------------|
| `university_departments.csv` | `departments` | Department information |
| `university_buildings.csv` | `buildings` | Campus buildings |
| `university_faculty.csv` | `faculty` | Faculty members |
| `university_students.csv` | `students` | Student records |
| `university_courses.csv` | `courses` | Course catalog |
| `university_equipment.csv` | `equipment` | Equipment inventory |
| `university_research.csv` | `research_projects` | Research projects |
| `university_forms.csv` | `forms` | Administrative forms |

## Database Relationships

```
departments
├── buildings (department_id)
├── faculty (department_id)
├── courses (department_id)
├── equipment (department_id)
├── research_projects (department_id)
└── forms (department_id)

faculty
├── students (advisor_id)
├── courses (instructor_id)
├── research_projects (principal_investigator)
└── forms (created_by_employee_id)

buildings
└── equipment (building_id)
```

## Performance Features

- **Indexes**: Automatically created on frequently queried columns
- **Connection Pooling**: Efficient connection management
- **Batch Operations**: Optimized bulk data loading
- **Query Optimization**: Efficient JOIN operations and subqueries

## Error Handling

The system includes comprehensive error handling:
- Database connection failures
- CSV parsing errors
- Data type conversion errors
- Foreign key constraint violations
- SQL execution errors

## Example Queries

### Get Department Statistics
```python
# Get all departments with their statistics
departments = db.get_all_departments()
for dept in departments:
    print(f"{dept['department_name']}: {dept['faculty_count']} faculty, ${dept['annual_budget']:,.2f} budget")
```

### Find High-Performing Students
```python
# Search for students with high GPA
students = db.search_students('John')
high_performers = [s for s in students if s['gpa'] and s['gpa'] > 3.8]
```

### Research Project Analysis
```python
# Get research projects with high funding
research_stats = db.get_research_stats()
print(f"Total research funding: ${research_stats['total_funding']:,.2f}")

# Find machine learning research
ml_projects = db.search_research_projects('Machine Learning')
```

### Equipment Maintenance Tracking
```python
# Get equipment needing maintenance
cs_equipment = db.get_equipment_by_department('DEPT001')
needs_maintenance = [e for e in cs_equipment if e['operational_status'] != 'Operational']
```

## Configuration Options

### Database Configuration
```python
config = DatabaseConfig(
    host="localhost",           # Database host
    port=5432,                 # Database port
    database="university_db",   # Database name
    username="postgres",        # Username
    password="password"         # Password
)
```

### CSV Loading Options
```python
# Load from custom path
db.load_csv_data(base_path="/path/to/csv/files")

# Load specific tables only
db.load_table_from_csv('departments', 'path/to/departments.csv')
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure PostgreSQL is running
   - Check host and port settings
   - Verify user credentials

2. **Permission Denied**
   - Grant appropriate database permissions
   - Check user creation commands

3. **CSV Loading Errors**
   - Verify CSV file paths
   - Check CSV format and encoding
   - Review data type conversions

4. **Foreign Key Violations**
   - Ensure data loading order (departments before faculty)
   - Check referential integrity in CSV data

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new features:
1. Update the schema in `table_schemas`
2. Add CSV mapping in `csv_mappings`
3. Create appropriate query methods
4. Add indexes for performance
5. Update documentation

## License

This implementation is part of the FimeHacks university database project. 