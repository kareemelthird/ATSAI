"""
Production Migration: Add Custom Instructions Support
Run this script against the production database
"""
import os
import sys
from pathlib import Path

# For production environment
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def migrate_production():
    """Apply custom instructions migration to production"""
    print("🏗️ Starting Production Migration...")
    
    # Use production database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found!")
        return False
    
    print(f"🔗 Connecting to: {database_url[:50]}...")
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Add custom instruction fields to User table
        print("\n1️⃣ Adding custom instruction fields to User table...")
        
        fields_to_add = [
            ("custom_chat_instructions", "TEXT"),
            ("custom_cv_analysis_instructions", "TEXT"), 
            ("use_custom_instructions", "BOOLEAN DEFAULT FALSE")
        ]
        
        for field_name, field_type in fields_to_add:
            try:
                # Check if field exists
                check_query = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = '{field_name}';
                """)
                
                result = db.execute(check_query).fetchone()
                
                if not result:
                    # Add the field
                    alter_query = text(f"""
                        ALTER TABLE users ADD COLUMN {field_name} {field_type};
                    """)
                    db.execute(alter_query)
                    db.commit()
                    print(f"   ✅ Added: {field_name}")
                else:
                    print(f"   ⚠️  Already exists: {field_name}")
                    
            except Exception as e:
                print(f"   ❌ Error adding {field_name}: {e}")
                db.rollback()
        
        # 2. Add missing system settings
        print("\n2️⃣ Adding usage limit settings...")
        
        settings_to_add = [
            ("usage_limits", "MAX_MESSAGES_PER_USER_DAILY", "100", "Maximum messages per user per day", True),
            ("usage_limits", "MAX_UPLOAD_SIZE_MB", "10", "Maximum upload size in MB", True),
            ("usage_limits", "MAX_UPLOADS_PER_USER_DAILY", "20", "Maximum uploads per user per day", True),
            ("ai", "ALLOW_USER_CUSTOM_INSTRUCTIONS", "true", "Allow users to set custom AI instructions", True),
        ]
        
        for category, key, value, description, is_public in settings_to_add:
            try:
                # Check if setting exists
                check_query = text("""
                    SELECT id FROM system_settings WHERE key = :key;
                """)
                result = db.execute(check_query, {"key": key}).fetchone()
                
                if not result:
                    # Add the setting
                    import uuid
                    from datetime import datetime
                    
                    insert_query = text("""
                        INSERT INTO system_settings 
                        (id, category, key, value, description, is_public, created_at, updated_at)
                        VALUES (:id, :category, :key, :value, :description, :is_public, :created_at, :updated_at);
                    """)
                    
                    db.execute(insert_query, {
                        "id": str(uuid.uuid4()),
                        "category": category,
                        "key": key,
                        "value": value,
                        "description": description,
                        "is_public": is_public,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    db.commit()
                    print(f"   ✅ Added: {key} = {value}")
                else:
                    print(f"   ⚠️  Already exists: {key}")
                    
            except Exception as e:
                print(f"   ❌ Error adding {key}: {e}")
                db.rollback()
        
        print("\n✅ Production migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    migrate_production()
