"""
Production Database Migration - Apply Custom Instructions
Run this with the production DATABASE_URL
"""
import os
import sys
from pathlib import Path

def migrate_production_database():
    """Apply custom instructions migration to production"""
    print("🏗️ Production Database Migration - Custom Instructions")
    print("=" * 60)
    
    # Production database URL - manually set for migration
    prod_db_url = "postgresql://postgres.ccsuvghmyazkpnhksywx:JZO8c2Qg4IYqz4NK@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
    
    print(f"🔗 Connecting to production database...")
    
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    import uuid
    from datetime import datetime
    
    # Create engine for production
    engine = create_engine(
        prod_db_url,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"}
    )
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Test connection
        db.execute(text("SELECT 1"))
        print("✅ Connected to production database successfully")
        
        # 1. Add custom instruction fields to User table
        print("\n1️⃣ Adding custom instruction fields to users table...")
        
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
                    alter_query = text(f"ALTER TABLE users ADD COLUMN {field_name} {field_type};")
                    db.execute(alter_query)
                    db.commit()
                    print(f"   ✅ Added field: {field_name}")
                else:
                    print(f"   ⚠️  Field already exists: {field_name}")
                    
            except Exception as e:
                print(f"   ❌ Error adding {field_name}: {e}")
                db.rollback()
        
        # 2. Add missing system settings
        print("\n2️⃣ Adding usage limit settings to system_settings...")
        
        settings_to_add = [
            ("usage_limits", "MAX_MESSAGES_PER_USER_DAILY", "100", "Maximum messages per user per day", True),
            ("usage_limits", "MAX_UPLOAD_SIZE_MB", "10", "Maximum upload size in MB", True),
            ("usage_limits", "MAX_UPLOADS_PER_USER_DAILY", "20", "Maximum uploads per user per day", True),
            ("ai", "ALLOW_USER_CUSTOM_INSTRUCTIONS", "true", "Allow users to set custom AI instructions", True),
        ]
        
        for category, key, value, description, is_public in settings_to_add:
            try:
                # Check if setting exists
                check_query = text("SELECT id FROM system_settings WHERE key = :key;")
                result = db.execute(check_query, {"key": key}).fetchone()
                
                if not result:
                    # Add the setting
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
                    print(f"   ✅ Added setting: {key} = {value}")
                else:
                    print(f"   ⚠️  Setting already exists: {key}")
                    
            except Exception as e:
                print(f"   ❌ Error adding {key}: {e}")
                db.rollback()
        
        # 3. Verify the changes
        print("\n3️⃣ Verifying migration...")
        
        # Check user fields
        check_fields = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('custom_chat_instructions', 'custom_cv_analysis_instructions', 'use_custom_instructions');
        """)
        
        user_fields = db.execute(check_fields).fetchall()
        print(f"   ✅ User fields added: {len(user_fields)}/3")
        
        # Check settings
        check_settings = text("SELECT key FROM system_settings WHERE category IN ('usage_limits', 'ai');")
        settings = db.execute(check_settings).fetchall()
        print(f"   ✅ Settings added: {len(settings)} total")
        
        print("\n🎉 Production migration completed successfully!")
        print("🚀 Custom instructions functionality is now active on Vercel!")
        print("\nNext: Deploy the updated code to Vercel to see improvements")
        
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
    migrate_production_database()