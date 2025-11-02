#!/usr/bin/env python3
"""
Create a new super admin user
"""
import requests
import json

def create_super_admin():
    base_url = "https://atsai-jade.vercel.app"
    
    print("👑 Creating New Super Admin User")
    print("=" * 50)
    
    # First, login with current admin to get access
    print("🔐 Logging in as current admin...")
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Try to create a new super admin user
    new_user_data = {
        "email": "superadmin@ats.com",
        "username": "superadmin",
        "password": "superadmin123",
        "first_name": "Super",
        "last_name": "Administrator",
        "role": "super_admin",
        "status": "active"
    }
    
    print(f"\n👤 Creating super admin user...")
    print(f"   Email: {new_user_data['email']}")
    print(f"   Username: {new_user_data['username']}")
    print(f"   Role: {new_user_data['role']}")
    
    # Try different endpoints for user creation
    create_endpoints = [
        '/users/',
        '/users/create',
        '/auth/register',
        '/admin/users/',
        '/admin/users/create'
    ]
    
    created = False
    
    for endpoint in create_endpoints:
        print(f"\n🧪 Trying endpoint: {endpoint}")
        try:
            create_response = requests.post(
                f"{base_url}/api/v1{endpoint}",
                json=new_user_data,
                headers=headers
            )
            
            print(f"   Status: {create_response.status_code}")
            
            if create_response.status_code in [200, 201]:
                print(f"✅ SUCCESS! User created via {endpoint}")
                result = create_response.json()
                print(f"   User ID: {result.get('id')}")
                print(f"   Email: {result.get('email')}")
                print(f"   Role: {result.get('role')}")
                created = True
                break
            else:
                print(f"   ❌ Failed: {create_response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    if not created:
        print(f"\n⚠️ Could not create user via API. Trying alternative approach...")
        
        # Try to get existing users and modify one
        users_response = requests.get(f"{base_url}/api/v1/users/", headers=headers)
        
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"📋 Found {len(users)} existing users")
            
            # Try to promote the current admin to super_admin
            current_user = None
            for user in users:
                if user.get('email') == 'admin@ats.com':
                    current_user = user
                    break
            
            if current_user:
                print(f"\n🔄 Promoting current user to super_admin...")
                user_id = current_user.get('id')
                
                update_data = {"role": "super_admin"}
                update_response = requests.put(
                    f"{base_url}/api/v1/users/{user_id}",
                    json=update_data,
                    headers=headers
                )
                
                print(f"Update status: {update_response.status_code}")
                if update_response.status_code == 200:
                    print(f"✅ SUCCESS! Promoted admin@ats.com to super_admin")
                    return True
                else:
                    print(f"❌ Update failed: {update_response.text}")
        else:
            print(f"❌ Could not fetch users: {users_response.text}")
    
    # If we created a new user, test login
    if created:
        print(f"\n🧪 Testing new super admin login...")
        test_login = requests.post(f"{base_url}/api/v1/auth/login", json={
            "email": "superadmin@ats.com",
            "password": "superadmin123"
        })
        
        if test_login.status_code == 200:
            print(f"✅ New super admin can login successfully!")
            user_data = test_login.json().get('user', {})
            print(f"   Role: {user_data.get('role')}")
            print(f"   Status: {user_data.get('status')}")
        else:
            print(f"❌ New super admin login failed: {test_login.text}")
    
    print(f"\n🎯 NEXT STEPS:")
    if created:
        print(f"1. Log out from current session")
        print(f"2. Log in with: superadmin@ats.com / superadmin123")
        print(f"3. Go to Settings page - should work with super_admin role")
    else:
        print(f"1. Check if promotion worked - log out and back in as admin@ats.com")
        print(f"2. Role should now be 'super_admin' instead of 'admin'")
        print(f"3. Settings page should now be accessible")

if __name__ == "__main__":
    create_super_admin()