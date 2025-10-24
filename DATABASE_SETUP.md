# Database Setup Instructions

## Current Situation
The user `k3admin` does not have permission to create databases in PostgreSQL.

## Solution Options

### Option 1: Ask Database Administrator (Recommended)
Ask your database administrator to run **ONE** of these commands:

#### A. Grant database creation privilege:
```sql
ALTER USER k3admin CREATEDB;
```
Then you can run:
```bash
cd C:\Users\karim.hassan\ATS\backend
..\.venv\Scripts\python.exe create_database.py
```

#### B. Create the database directly:
```sql
CREATE DATABASE ats_db OWNER k3admin;
```

### Option 2: Use Different Database Name
If you have access to an existing database, update the `.env` file:

```env
DATABASE_URL=postgresql+psycopg://k3admin:KH%40123456@localhost:5432/YOUR_EXISTING_DB
```

Replace `YOUR_EXISTING_DB` with a database you have access to.

### Option 3: Manual Creation via pgAdmin
1. Open pgAdmin
2. Connect to PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Database name: `ats_db`
5. Owner: `k3admin`
6. Click "Save"

## After Database is Created

Once the database exists, run this to create all tables:
```bash
cd C:\Users\karim.hassan\ATS\backend
..\.venv\Scripts\python.exe create_tables.py
```

## Start the Application

After tables are created:
```bash
cd C:\Users\karim.hassan\ATS\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: http://localhost:8000
API documentation at: http://localhost:8000/docs

## Current Database Credentials
- Host: localhost
- Port: 5432
- Database: ats_db
- User: k3admin
- Password: KH@123456
