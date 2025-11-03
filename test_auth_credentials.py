#!/usr/bin/env python3

import requests
import json

def test_auth_credentials():
    """Test different authentication credentials"""
    
    print("🔧 Testing different authentication credentials...")
    print("-" * 60)
    
    # Test different credentials
    credentials_to_test = [
        {"email": "kareemelthird@gmail.com", "password": "Admin123!"},
        {"email": "kareemelthird@gmail.com", "password": "temp123"},
        {"email": "kareemelthird@gmail.com", "password": "123456"},
        {"email": "admin@ats.com", "password": "admin123"},
        {"email": "admin@example.com", "password": "admin123"},
        {"email": "test@admin.com", "password": "admin123"}
    ]
    
    for i, creds in enumerate(credentials_to_test, 1):
        print(f"\n🔧 {i}. Testing {creds['email']} / {creds['password']}")
        try:
            auth_response = requests.post(
                "https://atsai-jade.vercel.app/api/v1/auth/login",
                json=creds,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {auth_response.status_code}")
            
            if auth_response.status_code == 200:
                auth_result = auth_response.json()
                user_info = auth_result.get("user", {})
                print(f"   ✅ SUCCESS!")
                print(f"   User Role: {user_info.get('role')}")
                print(f"   User Name: {user_info.get('full_name')}")
                print(f"   User ID: {user_info.get('id')}")
                return creds, auth_result.get("access_token")
            else:
                error_msg = auth_response.text[:100]
                print(f"   ❌ Failed: {error_msg}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n🔧 No valid credentials found!")
    return None, None

if __name__ == "__main__":
    creds, token = test_auth_credentials()
    if token:
        print(f"\n🔧 Valid credentials: {creds}")
        print(f"🔧 Token: {token[:20]}...")
    else:
        print("\n🔧 Unable to authenticate with any credentials")