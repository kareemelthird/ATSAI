"""
Script to create all database tables
Run this script after the database has been created
"""
from app.db.database import engine
from app.db import models

def create_tables():
    """Create all tables defined in the models"""
    try:
        print("=" * 60)
        print("Creating ATS Database Tables")
        print("=" * 60)
        
        models.Base.metadata.create_all(bind=engine)
        
        print("\n✓ All tables created successfully!")
        print("\nCreated tables:")
        for table_name in models.Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        print("\n" + "=" * 60)
        print("✓ Database tables setup completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error creating tables: {e}")
        print("\nPlease ensure:")
        print("  1. The database 'ats_db' exists")
        print("  2. User 'k3admin' has access to the database")
        print("  3. The connection string in .env is correct")

if __name__ == "__main__":
    create_tables()
