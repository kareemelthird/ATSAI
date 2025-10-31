"""
Migration script to fix the certifications.issuing_organization column
Make it nullable to match the model definition
"""

from app.db.database import engine
from sqlalchemy import text

def main():
    print("Fixing certifications.issuing_organization column...")
    
    with engine.connect() as conn:
        # Make issuing_organization nullable
        conn.execute(text(
            "ALTER TABLE certifications ALTER COLUMN issuing_organization DROP NOT NULL"
        ))
        conn.commit()
        
    print("✓ Successfully made issuing_organization nullable")
    print("  The column now matches the model definition")

if __name__ == "__main__":
    main()
