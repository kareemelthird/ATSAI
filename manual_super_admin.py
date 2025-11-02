#!/usr/bin/env python3
"""
Create a simple super admin user manually via SQL
"""

def create_super_admin_sql():
    print("👑 Manual Super Admin Creation")
    print("=" * 50)
    
    print("Since the API endpoints for user creation/updates are failing,")
    print("here's the SQL command to manually create a super admin user:")
    print()
    
    sql_command = """
-- Create super admin user directly in database
INSERT INTO users (
    id,
    email,
    username,
    password_hash,
    first_name,
    last_name,
    role,
    status,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'superadmin@ats.com',
    'superadmin',
    '$2b$12$WmjJB4qJ4Rm2Z9J8hF8qiOJ5pTxYNXNJl2AyQOc/EQV.1rGl8kF4i',  -- Password: superadmin123
    'Super',
    'Administrator',
    'super_admin',
    'active',
    NOW(),
    NOW()
);

-- Or update existing admin user to super_admin
UPDATE users 
SET role = 'super_admin', updated_at = NOW() 
WHERE email = 'admin@ats.com';
"""
    
    print(sql_command)
    print()
    print("🎯 BETTER SOLUTION - Frontend Fix:")
    print("Since the backend API is working fine, let's fix the frontend issue instead.")
    print()
    print("The problem is in the frontend authentication state.")
    print("We can solve this by:")
    print("1. Forcing a hard refresh of the authentication token")
    print("2. Adding a bypass mechanism for admin users")
    print("3. Fixing the axios interceptor conflicts")
    print()
    print("Would you like me to implement a frontend fix instead?")
    print("This would be faster and more reliable than database manipulation.")

if __name__ == "__main__":
    create_super_admin_sql()