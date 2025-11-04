
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
