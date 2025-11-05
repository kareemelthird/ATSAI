-- Add 'user' role to UserRole enum and update users
-- This migration adds the new 'user' role and updates default role

-- Step 1: Add 'user' to the UserRole enum
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'user';

-- Step 2: Update existing users with 'viewer' role to 'user' role (if any exist)
-- Note: Based on the migration output, there are no 'viewer' users currently
UPDATE users 
SET role = 'user' 
WHERE role = 'viewer';

-- Step 3: Update any users with NULL role to 'user'
UPDATE users 
SET role = 'user' 
WHERE role IS NULL;

-- Step 4: Display current users to verify
SELECT email, role, status, created_at 
FROM users 
ORDER BY created_at DESC;

-- Step 5: Verify the enum now includes 'user'
SELECT unnest(enum_range(NULL::userrole)) AS available_roles;