"""
Add years_of_experience column to candidates table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine

def add_years_of_experience_column():
    """Add years_of_experience column to candidates table"""
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='candidates' 
                AND column_name='years_of_experience'
            """))
            
            if result.fetchone():
                print("✓ Column 'years_of_experience' already exists in candidates table")
                return
            
            # Add the column
            print("Adding 'years_of_experience' column to candidates table...")
            conn.execute(text("""
                ALTER TABLE candidates 
                ADD COLUMN years_of_experience INTEGER DEFAULT 0
            """))
            conn.commit()
            
            print("✅ Successfully added 'years_of_experience' column!")
            print("\nColumn details:")
            print("- Type: INTEGER")
            print("- Default: 0")
            print("- Nullable: Yes")
            
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("ADDING years_of_experience COLUMN TO CANDIDATES TABLE")
    print("=" * 60)
    add_years_of_experience_column()
    print("\nNEXT STEPS:")
    print("1. Restart the backend server")
    print("2. Upload a new resume to test")
    print("3. Check that career_level and years_of_experience are extracted")
