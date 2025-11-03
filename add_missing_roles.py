#!/usr/bin/env python3
"""
Add Missing User Roles to Database
This script will update the database constraint to allow all defined roles
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://atsai-jade.vercel.app"

def create_users_with_different_roles():
    """Create test users with different roles to update database constraints"""
    print("=" * 60)
    print("CREATING USERS WITH DIFFERENT ROLES")
    print("=" * 60)
    
    # Login as admin first
    login_data = {
        "email": "admin@ats.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print("❌ Cannot login as admin")
        return
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Define roles to create
    roles_to_create = [
        {
            "role": "super_admin",
            "email": "superadmin@ats.com",
            "username": "superadmin",
            "first_name": "Super",
            "last_name": "Administrator",
            "description": "System Super Administrator"
        },
        {
            "role": "hr_manager", 
            "email": "hr@ats.com",
            "username": "hr_manager",
            "first_name": "HR",
            "last_name": "Manager",
            "description": "Human Resources Manager"
        },
        {
            "role": "recruiter",
            "email": "recruiter@ats.com", 
            "username": "recruiter",
            "first_name": "Senior",
            "last_name": "Recruiter",
            "description": "Senior Recruiter"
        },
        {
            "role": "viewer",
            "email": "viewer@ats.com",
            "username": "viewer",
            "first_name": "Read Only",
            "last_name": "User",
            "description": "Read-only user"
        }
    ]
    
    successful_roles = []
    failed_roles = []
    
    for role_data in roles_to_create:
        print(f"\n--- Creating {role_data['role']} user ---")
        
        user_data = {
            "email": role_data["email"],
            "password": "password123",  # 8+ characters
            "username": role_data["username"],
            "first_name": role_data["first_name"],
            "last_name": role_data["last_name"],
            "role": role_data["role"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/users/",
            json=user_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ {role_data['role']} user created successfully")
            successful_roles.append(role_data['role'])
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   ❌ Failed: {error_data}")
            failed_roles.append(role_data['role'])
    
    return successful_roles, failed_roles

def update_database_constraint():
    """Try to update database constraint through SQL if possible"""
    print("\n" + "=" * 60)
    print("DATABASE CONSTRAINT UPDATE NEEDED")
    print("=" * 60)
    
    print("The database currently has a CHECK constraint that only allows 'admin' role.")
    print("To fix this, we need to update the constraint to allow all roles:")
    print()
    print("Required SQL commands:")
    print("1. ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;")
    print("2. ALTER TABLE users ADD CONSTRAINT users_role_check")
    print("   CHECK (role IN ('super_admin', 'admin', 'hr_manager', 'recruiter', 'viewer'));")
    print()
    print("This needs to be executed directly on the Supabase database.")

def test_current_role_situation():
    """Test what roles currently work"""
    print("\n" + "=" * 60)
    print("CURRENT ROLE SITUATION")
    print("=" * 60)
    
    # Login as admin
    login_data = {
        "email": "admin@ats.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print("❌ Cannot login to test roles")
        return
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current users
    users_response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"✅ Current users in database:")
        for user in users:
            print(f"   {user.get('email', 'N/A')}: {user.get('role', 'N/A')} ({user.get('first_name', '')} {user.get('last_name', '')})")
        
        roles_in_use = set(user.get('role', 'unknown') for user in users)
        print(f"\n✅ Roles currently working: {sorted(roles_in_use)}")
    else:
        print(f"❌ Cannot fetch users: {users_response.status_code}")

def main():
    """Run role management tests"""
    print("USER ROLES DATABASE UPDATE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    # Test current situation
    test_current_role_situation()
    
    # Try to create users with different roles
    successful, failed = create_users_with_different_roles()
    
    # Show database constraint update info
    update_database_constraint()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if successful:
        print(f"✅ Successfully created roles: {successful}")
    if failed:
        print(f"❌ Failed to create roles: {failed}")
    
    print("\nNext steps:")
    print("1. Update database constraint to allow all roles")
    print("2. Update frontend role dropdown to show available options")
    print("3. Test role-based permissions")

if __name__ == "__main__":
    main()