"""
Vercel serverless function to apply database migration
Access via: https://your-app.vercel.app/api/migrate
"""

from fastapi import Request
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path

# Add backend to path for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent / "backend"
sys.path.append(str(backend_dir))

async def migrate_database(request: Request):
    """Apply custom instructions migration to production database"""
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        import uuid
        from datetime import datetime
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return JSONResponse({
                "success": False,
                "error": "DATABASE_URL not found in environment"
            }, status_code=500)
        
        # Create engine for production
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args={"sslmode": "require"} if "supabase.co" in database_url else {}
        )
        
        Session = sessionmaker(bind=engine)
        db = Session()
        
        results = []
        
        # 1. Add custom instruction fields to User table
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
                    results.append(f"✅ Added field: {field_name}")
                else:
                    results.append(f"⚠️ Field already exists: {field_name}")
                    
            except Exception as e:
                results.append(f"❌ Error adding {field_name}: {str(e)}")
                db.rollback()
        
        # 2. Add system settings
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
                    results.append(f"✅ Added setting: {key} = {value}")
                else:
                    results.append(f"⚠️ Setting already exists: {key}")
                    
            except Exception as e:
                results.append(f"❌ Error adding {key}: {str(e)}")
                db.rollback()
        
        db.close()
        
        return JSONResponse({
            "success": True,
            "message": "Migration completed successfully",
            "results": results
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": f"Migration failed: {str(e)}",
            "results": []
        }, status_code=500)

# For Vercel
app = migrate_database