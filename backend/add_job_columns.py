"""
Add missing columns to jobs table
"""
from app.db.database import engine
from sqlalchemy import text

def add_job_columns():
    with engine.connect() as conn:
        # Add missing columns
        try:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS department VARCHAR(255)"))
            print("✓ Added department column")
        except Exception as e:
            print(f"✗ department: {e}")
        
        try:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS responsibilities TEXT"))
            print("✓ Added responsibilities column")
        except Exception as e:
            print(f"✗ responsibilities: {e}")
        
        try:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS benefits TEXT"))
            print("✓ Added benefits column")
        except Exception as e:
            print(f"✗ benefits: {e}")
        
        try:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50)"))
            print("✓ Added experience_level column")
        except Exception as e:
            print(f"✗ experience_level: {e}")
        
        try:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS number_of_positions INTEGER DEFAULT 1"))
            print("✓ Added number_of_positions column")
        except Exception as e:
            print(f"✗ number_of_positions: {e}")
        
        # Update defaults for existing columns
        try:
            conn.execute(text("ALTER TABLE jobs ALTER COLUMN employment_type SET DEFAULT 'Full-time'"))
            print("✓ Set default for employment_type")
        except Exception as e:
            print(f"✗ employment_type default: {e}")
        
        try:
            conn.execute(text("ALTER TABLE jobs ALTER COLUMN salary_currency SET DEFAULT 'USD'"))
            print("✓ Set default for salary_currency")
        except Exception as e:
            print(f"✗ salary_currency default: {e}")
        
        conn.commit()
        print("\n✅ Migration completed!")

if __name__ == "__main__":
    add_job_columns()
