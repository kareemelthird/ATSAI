#!/usr/bin/env python3
"""
Create New Super Admin User
This script creates a new user with super admin privileges
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://atsai-jade.vercel.app"

def get_admin_token():
    """Get admin token for API calls"""
    print("🔑 Logging in as admin...")
    
    login_data = {
        "email": "admin@ats.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Admin login successful")
        return token_data.get("access_token")
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def check_current_users(token):
    """Check current users in the system"""
    print("\n📋 Checking current users...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"  - {user.get('email', 'N/A')} ({user.get('role', 'N/A')}) - {user.get('status', 'N/A')}")
        return users
    else:
        print(f"❌ Failed to get users: {response.status_code}")
        print(f"Response: {response.text}")
        return []

def create_super_admin_user(token, email, password, first_name, last_name):
    """Create a new super admin user"""
    print(f"\n👤 Creating super admin user: {email}")
    
    # Generate username from email (before @ symbol)
    username = email.split('@')[0]
    
    user_data = {
        "email": email,
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "role": "admin",  # Start with admin role due to constraint
        "department": "Administration",
        "job_title": "Super Administrator"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try to create user
    print("📝 Attempting to create user...")
    response = requests.post(
        f"{BASE_URL}/api/v1/users/",
        json=user_data,
        headers=headers
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code in [200, 201]:
        new_user = response.json()
        print("✅ User created successfully!")
        print(f"User ID: {new_user.get('id')}")
        print(f"Email: {new_user.get('email')}")
        print(f"Username: {new_user.get('username')}")
        print(f"Role: {new_user.get('role')}")
        return new_user
    else:
        print(f"❌ User creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        
        # If creation failed, try different approaches
        if "already exists" in response.text.lower():
            print("🔄 User already exists, trying to update instead...")
            return update_existing_user(token, email)
        
        return None

def update_existing_user(token, email):
    """Update existing user to admin role"""
    print(f"🔄 Updating existing user: {email}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get the user ID
    users_response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    if users_response.status_code != 200:
        print("❌ Failed to get users for update")
        return None
    
    users = users_response.json()
    target_user = None
    for user in users:
        if user.get('email') == email:
            target_user = user
            break
    
    if not target_user:
        print(f"❌ User {email} not found")
        return None
    
    # Update user
    update_data = {
        "role": "admin",
        "is_active": True,
        "department": "Administration",
        "job_title": "Super Administrator"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/users/{target_user['id']}",
        json=update_data,
        headers=headers
    )
    
    if response.status_code == 200:
        updated_user = response.json()
        print("✅ User updated successfully!")
        return updated_user
    else:
        print(f"❌ User update failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_new_user_login(email, password):
    """Test if the new user can log in"""
    print(f"\n🧪 Testing login for new user: {email}")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ New user login successful!")
        print(f"Role: {token_data.get('user', {}).get('role', 'N/A')}")
        return True
    else:
        print(f"❌ New user login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("CREATE NEW SUPER ADMIN USER")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    # Get user input
    print("\n📝 Enter new super admin user details:")
    email = input("Email: ").strip()
    if not email:
        email = "superadmin@ats.com"
        print(f"Using default: {email}")
    
    password = input("Password: ").strip()
    if not password:
        password = "SuperAdmin123!"
        print(f"Using default password")
    
    first_name = input("First Name: ").strip()
    if not first_name:
        first_name = "Super"
        print(f"Using default: {first_name}")
    
    last_name = input("Last Name: ").strip()
    if not last_name:
        last_name = "Admin"
        print(f"Using default: {last_name}")
    
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot proceed without admin token")
        return
    
    # Check current users
    current_users = check_current_users(admin_token)
    
    # Create new user
    new_user = create_super_admin_user(admin_token, email, password, first_name, last_name)
    
    if new_user:
        # Test new user login
        login_success = test_new_user_login(email, password)
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✅ Super admin user creation: SUCCESS")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {first_name} {last_name}")
        print(f"🔑 Role: {new_user.get('role', 'N/A')}")
        print(f"🔓 Login test: {'✅ SUCCESS' if login_success else '❌ FAILED'}")
        
        print("\n📋 Next steps:")
        print("1. User can now log in with the provided credentials")
        print("2. User has admin role (equivalent to super admin permissions)")
        print("3. Access Settings page and all admin features")
        print("4. Database constraint prevents 'super_admin' role, but 'admin' has same permissions")
        
    else:
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("❌ Super admin user creation: FAILED")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()