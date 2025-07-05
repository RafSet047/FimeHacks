# PostgreSQL Setup for FimeHacks

This guide helps you set up PostgreSQL for the FimeHacks project.

## Quick Setup

### 1. Automated Setup (Recommended)

Run the automated setup script:

```bash
cd FimeHacks
python setup_postgres.py
```

This script will:
- Install PostgreSQL on your system
- Create a database user and database
- Install Python dependencies
- Test the connection

### 2. Manual Setup

If the automated setup doesn't work, follow these manual steps:

#### Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Create Database User

Connect to PostgreSQL as the postgres user:

```bash
sudo -u postgres psql
```

Run these commands:

```sql
CREATE USER fimehacks_user WITH PASSWORD 'fimehacks_password';
ALTER USER fimehacks_user CREATEDB;
CREATE DATABASE fimehacks_db OWNER fimehacks_user;
GRANT ALL PRIVILEGES ON DATABASE fimehacks_db TO fimehacks_user;
\q
```

#### Install Python Dependencies

```bash
pip install -r requirements_postgres.txt
```

## Configuration

The project uses these default database settings:

- **Host**: localhost
- **Port**: 5432
- **Database**: fimehacks_db
- **Username**: fimehacks_user
- **Password**: fimehacks_password

You can customize these settings by:

1. Running `python setup_postgres.py` to create a `database_config.py` file
2. Editing the `database_config.py` file with your preferred settings

## Testing the Setup

Run the PostgreSQL example:

```bash
python examples/postgres_usage_example.py
```

This will:
- Create the database schema
- Load sample data
- Run various queries
- Display statistics

## Troubleshooting

### "role 'postgres' does not exist"

This means PostgreSQL is not installed or the default user doesn't exist.

**Solution:**
1. Install PostgreSQL using the instructions above
2. Create the postgres user if needed:
   ```bash
   sudo -u postgres createuser --superuser postgres
   ```

### Connection refused

PostgreSQL service is not running.

**Solution:**
```bash
# macOS
brew services start postgresql@14

# Ubuntu/Debian
sudo systemctl start postgresql

# CentOS/RHEL
sudo systemctl start postgresql
```

### Permission denied

Database user doesn't have proper permissions.

**Solution:**
```bash
sudo -u postgres psql
```

Then run:
```sql
ALTER USER fimehacks_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE fimehacks_db TO fimehacks_user;
```

## Database Schema

The PostgreSQL database includes these tables:

- **departments**: University departments
- **faculty**: Faculty members
- **students**: Student records
- **courses**: Course information
- **equipment**: Department equipment
- **research_projects**: Research projects
- **forms**: Administrative forms

## Sample Data

The example loads sample data including:
- 3 departments (Computer Science, Mathematics, Physics)
- Faculty members with various positions
- Students with different majors
- Courses and equipment
- Research projects

## Next Steps

After successful setup:

1. Explore the database using the example script
2. Modify the schema in `src/database/postgre_db.py` if needed
3. Add your own data or connect to existing CSV files
4. Integrate with other parts of the FimeHacks project

## Support

If you encounter issues:

1. Check the PostgreSQL logs:
   ```bash
   # macOS
   tail -f /usr/local/var/log/postgres.log
   
   # Linux
   sudo tail -f /var/log/postgresql/postgresql-*.log
   ```

2. Verify PostgreSQL is running:
   ```bash
   pg_isready
   ```

3. Test connection manually:
   ```bash
   psql -h localhost -U fimehacks_user -d fimehacks_db
   ``` 