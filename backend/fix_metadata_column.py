"""
Fix metadata column name conflict in user_usage_history table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Create engine
engine = create_engine(str(settings.DATABASE_URL))

# SQL to rename column
sql = """
-- Check if column exists and rename it
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_usage_history' 
        AND column_name = 'metadata'
    ) THEN
        ALTER TABLE user_usage_history RENAME COLUMN metadata TO extra_data;
        RAISE NOTICE 'Column renamed from metadata to extra_data';
    ELSE
        RAISE NOTICE 'Column metadata does not exist, skipping';
    END IF;
END $$;
"""

print("Fixing metadata column name...")
try:
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ Column fixed successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
