-- Update User Roles Migration
-- Updates existing users from 'viewer' to 'user' role and sets proper default

-- Update existing users with 'viewer' role to 'user' role
UPDATE users 
SET role = 'user' 
WHERE role = 'viewer';

-- Update any users with NULL role to 'user'
UPDATE users 
SET role = 'user' 
WHERE role IS NULL;

-- Ensure proper role values (in case of invalid data)
UPDATE users 
SET role = 'user' 
WHERE role NOT IN ('super_admin', 'admin', 'hr_manager', 'recruiter', 'user', 'viewer');

-- Set status to 'active' for any pending users (assuming they were approved)
-- Comment out this line if you want to keep pending status
-- UPDATE users SET status = 'active' WHERE status = 'pending';

-- Display updated users
SELECT email, role, status, created_at 
FROM users 
ORDER BY created_at DESC;