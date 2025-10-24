"""
Script to create the ATS database
Run this script once to create the database if k3admin user has sufficient privileges
"""
import psycopg
from psycopg import sql

# Database connection parameters
DB_USER = "k3admin"
DB_PASSWORD = "KH@123456"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ats_db"

def create_database():
    """Create the ats_db database if it doesn't exist"""
    # First, connect to the default 'postgres' database
    conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD.replace('@', '%40')}@{DB_HOST}:{DB_PORT}/postgres"
    
    try:
        # Connect with autocommit mode to create database
        conn = psycopg.connect(conn_string, autocommit=True)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{DB_NAME}' already exists.")
        else:
            # Create the database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))
            )
            print(f"✓ Database '{DB_NAME}' created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg.errors.InsufficientPrivilege:
        print(f"\n✗ Error: User '{DB_USER}' does not have permission to create databases.")
        print("\nPlease ask your database administrator to:")
        print(f"  1. Grant CREATEDB privilege: ALTER USER {DB_USER} CREATEDB;")
        print(f"  OR")
        print(f"  2. Create the database manually: CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
        return False
        
    except Exception as e:
        print(f"\n✗ Error creating database: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ATS Database Setup")
    print("=" * 60)
    
    success = create_database()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Database setup completed!")
        print("=" * 60)
        print("\nYou can now start the backend server:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
    else:
        print("\n" + "=" * 60)
        print("Database setup failed - manual intervention required")
        print("=" * 60)
