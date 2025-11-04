"""
Add custom instruction fields to User table
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.db.database import engine, SessionLocal

def add_custom_instruction_fields():
    """Add custom instruction fields to the User table"""
    print("🔨 Adding custom instruction fields to User table...")
    
    db = SessionLocal()
    try:
        # Check if fields already exist
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('custom_chat_instructions', 'custom_cv_analysis_instructions', 'use_custom_instructions');
        """)
        
        existing_columns = db.execute(check_query).fetchall()
        existing_column_names = [col[0] for col in existing_columns]
        
        print(f"📋 Existing custom instruction columns: {existing_column_names}")
        
        # Add missing columns
        columns_to_add = [
            ("custom_chat_instructions", "TEXT"),
            ("custom_cv_analysis_instructions", "TEXT"),
            ("use_custom_instructions", "BOOLEAN DEFAULT FALSE")
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_column_names:
                alter_query = text(f"""
                    ALTER TABLE users 
                    ADD COLUMN {column_name} {column_type};
                """)
                
                try:
                    db.execute(alter_query)
                    db.commit()
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"❌ Error adding column {column_name}: {e}")
                    db.rollback()
            else:
                print(f"⚠️  Column {column_name} already exists")
        
        print("✅ Custom instruction fields setup completed!")
        
    except Exception as e:
        print(f"❌ Error setting up custom instruction fields: {e}")
        db.rollback()
    finally:
        db.close()

def add_missing_settings():
    """Add missing limit settings to SystemSettings"""
    print("\n🔨 Adding missing limit settings...")
    
    db = SessionLocal()
    try:
        # Define missing settings
        missing_settings = [
            ("usage_limits", "MAX_MESSAGES_PER_USER_DAILY", "100", "Maximum messages per user per day", True),
            ("usage_limits", "MAX_UPLOAD_SIZE_MB", "10", "Maximum upload size in MB", True),
            ("usage_limits", "MAX_UPLOADS_PER_USER_DAILY", "20", "Maximum uploads per user per day", True),
            ("ai", "ALLOW_USER_CUSTOM_INSTRUCTIONS", "true", "Allow users to set custom AI instructions", True),
        ]
        
        from app.db.models_users import SystemSettings
        
        for category, key, default_value, description, is_public in missing_settings:
            # Check if setting exists
            existing = db.query(SystemSettings).filter(SystemSettings.key == key).first()
            
            if not existing:
                new_setting = SystemSettings(
                    category=category,
                    key=key,
                    value=default_value,
                    description=description,
                    is_public=is_public,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_setting)
                print(f"✅ Added setting: {key} = {default_value}")
            else:
                print(f"⚠️  Setting {key} already exists")
        
        db.commit()
        print("✅ Missing settings added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding missing settings: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting custom instructions setup...")
    
    # Import datetime here to avoid issues
    from datetime import datetime
    
    # Add custom instruction fields to User table
    add_custom_instruction_fields()
    
    # Add missing settings
    add_missing_settings()
    
    print("\n🎉 Setup completed!")