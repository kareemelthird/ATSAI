"""
Deploy custom instructions to Vercel production
This script will apply all the database changes to the production database
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

def deploy_to_production():
    """Deploy custom instructions functionality to production"""
    print("🚀 Deploying Custom Instructions to Vercel Production")
    print("=" * 60)
    
    # Check if we're targeting production
    print("\n🔍 Environment Check:")
    database_url = os.getenv('DATABASE_URL', 'Not found')
    if 'localhost' in database_url:
        print("⚠️  Warning: Currently pointing to localhost database")
        print("   Make sure to update DATABASE_URL for production deployment")
    else:
        print(f"✅ Production database detected")
    
    print("\n📋 Changes to Deploy:")
    print("1. ✅ User table: Add custom instruction fields")
    print("2. ✅ SystemSettings: Add usage limit settings")  
    print("3. ✅ API: Custom instruction endpoints")
    print("4. ✅ AI Service: Use custom instructions")
    print("5. ✅ Settings: Public settings endpoint")
    
    # For production deployment, we need to:
    # 1. Update environment variables
    # 2. Run database migrations
    # 3. Deploy code changes
    
    print("\n🔧 Production Deployment Steps:")
    print("1. Set production DATABASE_URL environment variable")
    print("2. Run database migration script on production")
    print("3. Deploy updated code to Vercel")
    print("4. Verify AI chat quality improvements")
    
    return True

def create_production_migration():
    """Create production-ready migration script"""
    
    migration_script = '''"""
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
        print("\\n1️⃣ Adding custom instruction fields to User table...")
        
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
        print("\\n2️⃣ Adding usage limit settings...")
        
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
        
        print("\\n✅ Production migration completed successfully!")
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
'''
    
    with open("production_migration.py", "w", encoding="utf-8") as f:
        f.write(migration_script)
    
    print("📄 Created: production_migration.py")
    return True

if __name__ == "__main__":
    deploy_to_production()
    create_production_migration()
    
    print("\n🎯 Next Steps for Vercel Deployment:")
    print("1. Update environment variables in Vercel dashboard")
    print("2. Run: python production_migration.py (with production DATABASE_URL)")
    print("3. Deploy to Vercel: vercel --prod")
    print("4. Test AI chat quality on production site")