"""
Add missing columns to applications table
"""
from app.db.database import engine
from sqlalchemy import text

def add_application_columns():
    with engine.connect() as conn:
        # Add missing columns
        try:
            conn.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS interview_date TIMESTAMP"))
            print("✓ Added interview_date column")
        except Exception as e:
            print(f"✗ interview_date: {e}")
        
        try:
            conn.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS offer_details TEXT"))
            print("✓ Added offer_details column")
        except Exception as e:
            print(f"✗ offer_details: {e}")
        
        try:
            conn.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS rejection_reason TEXT"))
            print("✓ Added rejection_reason column")
        except Exception as e:
            print(f"✗ rejection_reason: {e}")
        
        try:
            conn.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS match_score NUMERIC(5, 2)"))
            print("✓ Added match_score column")
        except Exception as e:
            print(f"✗ match_score: {e}")
        
        # Update status column length and default
        try:
            conn.execute(text("ALTER TABLE applications ALTER COLUMN status TYPE VARCHAR(50)"))
            print("✓ Updated status column type")
        except Exception as e:
            print(f"✗ status type: {e}")
        
        try:
            conn.execute(text("ALTER TABLE applications ALTER COLUMN status SET DEFAULT 'submitted'"))
            print("✓ Set default for status")
        except Exception as e:
            print(f"✗ status default: {e}")
        
        conn.commit()
        print("\n✅ Migration completed!")

if __name__ == "__main__":
    add_application_columns()
