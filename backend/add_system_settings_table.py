"""
Add system settings and user limits tables
Run this to add new tables for UI-based configuration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Create engine
engine = create_engine(str(settings.DATABASE_URL))

# SQL to create tables
sql = """
-- System Settings Table (for admin to control everything from UI)
CREATE TABLE IF NOT EXISTS system_ai_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) NOT NULL,  -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);

-- User Usage Limits Table
CREATE TABLE IF NOT EXISTS user_usage_limits (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    daily_ai_messages_limit INTEGER DEFAULT 50,
    daily_file_uploads_limit INTEGER DEFAULT 10,
    messages_used_today INTEGER DEFAULT 0,
    files_uploaded_today INTEGER DEFAULT 0,
    last_reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- User Usage History Table (track all usage)
CREATE TABLE IF NOT EXISTS user_usage_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,  -- 'ai_message', 'file_upload', 'resume_parse'
    used_personal_key BOOLEAN DEFAULT false,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extra_data JSONB
);

-- Insert default system settings
INSERT INTO system_ai_settings (setting_key, setting_value, setting_type, description) VALUES
    ('system_groq_api_key', '', 'string', 'System-wide Groq API key (fallback when users dont have personal key)'),
    ('system_ai_enabled', 'true', 'boolean', 'Enable/disable system AI key usage'),
    ('system_daily_message_limit', '100', 'number', 'Maximum AI messages per day using system key'),
    ('system_daily_upload_limit', '20', 'number', 'Maximum file uploads per day using system key'),
    ('default_user_message_limit', '50', 'number', 'Default daily AI message limit for new users'),
    ('default_user_upload_limit', '10', 'number', 'Default daily upload limit for new users'),
    ('require_personal_key', 'false', 'boolean', 'Force all users to use personal API keys'),
    ('ai_model_name', 'llama-3.3-70b-versatile', 'string', 'Default AI model to use'),
    ('system_messages_used_today', '0', 'number', 'Messages used today with system key'),
    ('system_uploads_used_today', '0', 'number', 'Uploads used today with system key'),
    ('last_system_reset_date', CURRENT_DATE::text, 'string', 'Last date system limits were reset')
ON CONFLICT (setting_key) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_usage_limits_user_id ON user_usage_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_user_usage_history_user_id ON user_usage_history(user_id);
CREATE INDEX IF NOT EXISTS idx_user_usage_history_timestamp ON user_usage_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_ai_settings_key ON system_ai_settings(setting_key);

-- Initialize usage limits for existing users
INSERT INTO user_usage_limits (user_id, daily_ai_messages_limit, daily_file_uploads_limit)
SELECT id, 50, 10 FROM users
ON CONFLICT (user_id) DO NOTHING;

COMMIT;
"""

print("Creating system settings and user limits tables...")
try:
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ Tables created successfully!")
    print("\n📋 Created tables:")
    print("  - system_ai_settings (admin controls)")
    print("  - user_usage_limits (per-user limits)")
    print("  - user_usage_history (usage tracking)")
    print("\n🎯 Next steps:")
    print("  1. Go to Admin Settings page")
    print("  2. Configure system API key and limits")
    print("  3. Set per-user limits as needed")
    print("  4. All changes apply immediately - no restart needed!")
except Exception as e:
    print(f"❌ Error: {e}")
