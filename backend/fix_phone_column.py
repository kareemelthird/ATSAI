"""
Migration script to increase phone column size
Allow for multiple phone numbers separated by / or other delimiters
"""

from app.db.database import engine
from sqlalchemy import text

def main():
    print("Fixing candidates.phone column size...")
    
    with engine.connect() as conn:
        # Increase phone column size from VARCHAR(20) to VARCHAR(50)
        print("  Increasing phone column from VARCHAR(20) to VARCHAR(50)...")
        conn.execute(text(
            "ALTER TABLE candidates ALTER COLUMN phone TYPE VARCHAR(50)"
        ))
        
        conn.commit()
        
    print("✓ Successfully increased phone column size to VARCHAR(50)")
    print("  Can now handle multiple phone numbers")

if __name__ == "__main__":
    main()
