#!/usr/bin/env python3
"""
Debug Database Roles and Settings Issues
Investigate role constraints and settings loading problems
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://atsai-jade.vercel.app"

def test_user_roles():
    """Test user roles and permissions"""
    print("=" * 60)
    print("TESTING USER ROLES AND PERMISSIONS")
    print("=" * 60)
    
    # Test both users
    users = [
        {"email": "admin@ats.com", "password": "admin123", "name": "Original Admin"},
        {"email": "kareemelthird@gmail.com", "password": "admin123", "name": "New Admin"}
    ]
    
    for user in users:
        print(f"\n--- Testing {user['name']} ---")
        
        # Login
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login", 
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            user_info = token_data.get("user", {})
            
            print(f"✅ Login successful")
            print(f"   Email: {user_info.get('email', 'N/A')}")
            print(f"   Role: {user_info.get('role', 'N/A')}")
            print(f"   Username: {user_info.get('username', 'N/A')}")
            print(f"   Name: {user_info.get('first_name', 'N/A')} {user_info.get('last_name', 'N/A')}")
            
            # Test settings access
            headers = {"Authorization": f"Bearer {token}"}
            settings_response = requests.get(f"{BASE_URL}/api/v1/settings/", headers=headers)
            print(f"   Settings API: {settings_response.status_code} ({len(settings_response.json()) if settings_response.status_code == 200 else 'Failed'})")
            
            # Test users management access
            users_response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)
            print(f"   Users API: {users_response.status_code} ({len(users_response.json()) if users_response.status_code == 200 else 'Failed'})")
            
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")

def test_role_constraints():
    """Test database role constraints"""
    print("\n" + "=" * 60)
    print("TESTING ROLE CONSTRAINTS")
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
        print("❌ Cannot login to test role constraints")
        return
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create a user with different roles
    test_roles = ["viewer", "hr", "admin", "super_admin"]
    
    for role in test_roles:
        print(f"\n--- Testing role: {role} ---")
        
        user_data = {
            "email": f"test_{role}@example.com",
            "password": "testpassword123",  # 8+ characters
            "username": f"test_{role}",
            "first_name": "Test",
            "last_name": role.title(),
            "role": role
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/users/",
            json=user_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   Error: {error_data}")
        else:
            print(f"   ✅ User created successfully")
            # Clean up - delete the test user
            users_response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)
            if users_response.status_code == 200:
                users = users_response.json()
                test_user = next((u for u in users if u['email'] == user_data['email']), None)
                if test_user:
                    delete_response = requests.delete(f"{BASE_URL}/api/v1/users/{test_user['id']}", headers=headers)
                    print(f"   🗑️ Test user deleted: {delete_response.status_code}")

def check_database_schema():
    """Check available roles in database"""
    print("\n" + "=" * 60)
    print("CHECKING DATABASE SCHEMA")
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
        print("❌ Cannot login to check database schema")
        return
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all users to see what roles exist
    users_response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    
    if users_response.status_code == 200:
        users = users_response.json()
        roles = set(user.get('role', 'unknown') for user in users)
        print(f"✅ Current roles in database: {sorted(roles)}")
        
        for user in users:
            print(f"   {user.get('email', 'N/A')}: {user.get('role', 'N/A')}")
    else:
        print(f"❌ Cannot fetch users: {users_response.status_code}")

def main():
    """Run all diagnostic tests"""
    print("ROLE AND SETTINGS DIAGNOSTIC TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    test_user_roles()
    check_database_schema() 
    test_role_constraints()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    print("1. Database only allows specific roles (likely viewer, hr, admin)")
    print("2. 'super_admin' role may not be in allowed values")
    print("3. Frontend role dropdown should show available roles")
    print("4. Settings page loading issue is separate from role issue")
    print("5. Need to check frontend role options configuration")

if __name__ == "__main__":
    main()
