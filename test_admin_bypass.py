#!/usr/bin/env python3
"""
Direct test of settings endpoint with admin role
"""
import requests

def test_admin_settings_access():
    base_url = "https://atsai-jade.vercel.app"
    
    print("🔐 Testing Admin Settings Access")
    print("=" * 40)
    
    # Login as admin
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    login_data = login_response.json()
    token = login_data.get("access_token")
    user_data = login_data.get("user", {})
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Login successful as: {user_data.get('email')}")
    print(f"🎭 Role: {user_data.get('role')}")
    print(f"📊 Status: {user_data.get('status')}")
    
    # Test the exact settings endpoint the frontend uses
    print(f"\n🧪 Testing settings endpoint...")
    
    try:
        settings_response = requests.get(
            f"{base_url}/api/v1/settings/",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {settings_response.status_code}")
        print(f"Headers: {dict(settings_response.headers)}")
        
        if settings_response.status_code == 200:
            settings = settings_response.json()
            print(f"✅ SUCCESS! Settings loaded: {len(settings)} items")
            
            # Show categories
            categories = set(s.get('category', 'unknown') for s in settings)
            print(f"📂 Categories: {sorted(list(categories))}")
            
            # Show first few settings
            print(f"📋 First 3 settings:")
            for i, setting in enumerate(settings[:3]):
                print(f"   {i+1}. {setting.get('key')}: {setting.get('label')}")
                
        elif settings_response.status_code == 403:
            print(f"❌ PERMISSION DENIED (403)")
            print(f"Response: {settings_response.text}")
            print(f"🚨 This confirms the role 'admin' is not allowed access")
            
        elif settings_response.status_code == 401:
            print(f"❌ AUTHENTICATION FAILED (401)")
            print(f"Response: {settings_response.text}")
            print(f"🚨 This suggests token issue, not role issue")
            
        else:
            print(f"❌ UNEXPECTED ERROR ({settings_response.status_code})")
            print(f"Response: {settings_response.text}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
    
    # Test if we can access other admin endpoints
    print(f"\n🔬 Testing other endpoints for comparison...")
    
    test_endpoints = [
        ('/auth/me', 'User Profile'),
        ('/users/', 'User Management'),
        ('/candidates/', 'Candidates List'),
        ('/settings/public/project-info', 'Public Settings'),
    ]
    
    for endpoint, name in test_endpoints:
        try:
            response = requests.get(f"{base_url}/api/v1{endpoint}", headers=headers, timeout=5)
            status = "✅" if response.status_code == 200 else f"❌ ({response.status_code})"
            print(f"   {status} {name}")
        except:
            print(f"   ❌ {name} - Request failed")

if __name__ == "__main__":
    test_admin_settings_access()