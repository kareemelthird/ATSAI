"""
Migration script to fix the education table
Make degree and field_of_study nullable to handle cases where AI cannot extract them
(e.g., short courses, certificates, workshops)
"""

from app.db.database import engine
from sqlalchemy import text

def main():
    print("Fixing education table constraints...")
    
    with engine.connect() as conn:
        # Make degree nullable (for short courses, workshops, etc.)
        print("  Making 'degree' column nullable...")
        conn.execute(text(
            "ALTER TABLE education ALTER COLUMN degree DROP NOT NULL"
        ))
        
        # Make field_of_study nullable (some institutions may not specify)
        print("  Making 'field_of_study' column nullable...")
        conn.execute(text(
            "ALTER TABLE education ALTER COLUMN field_of_study DROP NOT NULL"
        ))
        
        conn.commit()
        
    print("✓ Successfully made education columns nullable")
    print("  - degree: now nullable (handles short courses, workshops)")
    print("  - field_of_study: now nullable (handles unspecified fields)")

if __name__ == "__main__":
    main()
