"""
Add personal AI API key columns to users table
"""

from sqlalchemy import create_engine, text
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ats_db")

def add_user_ai_columns():
    """Add personal_groq_api_key and use_personal_ai_key columns to users table"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if columns already exist
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('personal_groq_api_key', 'use_personal_ai_key')
        """)
        
        result = conn.execute(check_query)
        existing_columns = [row[0] for row in result]
        
        # Add personal_groq_api_key column if it doesn't exist
        if 'personal_groq_api_key' not in existing_columns:
            print("Adding personal_groq_api_key column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN personal_groq_api_key VARCHAR(255)
            """))
            conn.commit()
            print("✅ Added personal_groq_api_key column")
        else:
            print("⚠️  personal_groq_api_key column already exists")
        
        # Add use_personal_ai_key column if it doesn't exist
        if 'use_personal_ai_key' not in existing_columns:
            print("Adding use_personal_ai_key column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN use_personal_ai_key BOOLEAN DEFAULT FALSE
            """))
            conn.commit()
            print("✅ Added use_personal_ai_key column")
        else:
            print("⚠️  use_personal_ai_key column already exists")
        
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    try:
        add_user_ai_columns()
    except Exception as e:
        print(f"❌ Error: {e}")
