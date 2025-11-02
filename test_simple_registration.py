#!/usr/bin/env python3
"""
Simple test to register a new user and see what role they get
"""
import requests
import uuid

def test_simple_registration():
    base_url = "https://atsai-jade.vercel.app"
    
    print("👤 Testing Simple User Registration")
    print("=" * 40)
    
    # Generate unique email to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"testuser{unique_id}@ats.com"
    
    register_data = {
        "email": test_email,
        "username": f"testuser{unique_id}",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print(f"📝 Registering new user: {test_email}")
    
    # Try registration
    register_response = requests.post(f"{base_url}/api/v1/auth/register", json=register_data)
    
    print(f"Registration Status: {register_response.status_code}")
    
    if register_response.status_code in [200, 201]:
        print(f"✅ Registration successful!")
        result = register_response.json()
        print(f"Response: {result}")
        
        # Test login with new user
        login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
            "email": test_email,
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            user_data = login_response.json().get('user', {})
            print(f"\n👤 New user details:")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   Status: {user_data.get('status')}")
            
            # Test if this user can access any admin endpoints
            token = login_response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"\n🧪 Testing endpoint access...")
            test_endpoints = [
                ('/auth/me', 'Profile'),
                ('/settings/', 'Settings'),
                ('/users/', 'Users'),
            ]
            
            for endpoint, name in test_endpoints:
                response = requests.get(f"{base_url}/api/v1{endpoint}", headers=headers)
                status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
                print(f"   {status} {name}")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    else:
        print(f"❌ Registration failed: {register_response.text}")
        
    print(f"\n💡 Key insight:")
    print(f"   If registration works and gives 'user' role, we know:")
    print(f"   1. User creation works")
    print(f"   2. Role system is functional") 
    print(f"   3. Issue is with role updates, not creation")

if __name__ == "__main__":
    test_simple_registration()