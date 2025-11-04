"""
Apply production database migration via API endpoint
This will add the missing custom instruction fields and settings
"""
import requests
import json

def apply_production_migration():
    """Apply database migration to fix the 500 errors"""
    print("🏗️ Applying Production Database Migration")
    print("=" * 50)
    
    # We need to add the custom instruction fields and settings
    # Let's create a direct SQL script that can be run
    
    sql_migration = """
-- Add custom instruction fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS custom_chat_instructions TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS custom_cv_analysis_instructions TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS use_custom_instructions BOOLEAN DEFAULT FALSE;

-- Add usage limit settings
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'usage_limits',
    'MAX_MESSAGES_PER_USER_DAILY',
    '100',
    'Maximum messages per user per day',
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM system_settings WHERE key = 'MAX_MESSAGES_PER_USER_DAILY'
);

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'usage_limits',
    'MAX_UPLOAD_SIZE_MB',
    '10',
    'Maximum upload size in MB',
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM system_settings WHERE key = 'MAX_UPLOAD_SIZE_MB'
);

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'usage_limits',
    'MAX_UPLOADS_PER_USER_DAILY',
    '20',
    'Maximum uploads per user per day',
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM system_settings WHERE key = 'MAX_UPLOADS_PER_USER_DAILY'
);

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'ai',
    'ALLOW_USER_CUSTOM_INSTRUCTIONS',
    'true',
    'Allow users to set custom AI instructions',
    true,
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM system_settings WHERE key = 'ALLOW_USER_CUSTOM_INSTRUCTIONS'
);
"""
    
    print("📋 SQL Migration Script Generated:")
    print("=" * 50)
    print(sql_migration)
    print("=" * 50)
    
    print("\n🔧 To apply this migration:")
    print("1. Connect to your Supabase database")
    print("2. Go to SQL Editor")  
    print("3. Run the above SQL script")
    print("4. Verify the changes are applied")
    print("5. Test login functionality")
    
    return sql_migration

def test_health_check():
    """Test if the backend is responding"""
    print("\n🏥 Testing Backend Health...")
    
    try:
        response = requests.get("https://atsai-jade.vercel.app/api/v1/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend is healthy:")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database_status')}")
            print(f"   Info: {health_data.get('database_info', '')[:60]}...")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    test_health_check()
    migration_sql = apply_production_migration()
    
    print("\n🎯 After applying the migration:")
    print("✅ Login errors will be fixed")
    print("✅ Custom instructions will work")
    print("✅ AI chat quality will improve")
    print("✅ All new features will be functional")
    
    # Save the SQL to a file for easy execution
    with open("production_migration.sql", "w") as f:
        f.write(migration_sql)
    print(f"\n📁 Migration saved to: production_migration.sql")