#!/usr/bin/env python3

import requests
import json
import sys

def test_settings_all_endpoint():
    """Test specifically the /admin/settings/all endpoint"""
    
    print("🔧 Testing /admin/settings/all endpoint...")
    print("-" * 60)
    
    # Test authentication first
    auth_data = {
        "email": "admin@ats.com", 
        "password": "admin123"
    }
    
    print("🔧 1. Testing authentication...")
    try:
        auth_response = requests.post(
            "https://atsai-jade.vercel.app/api/v1/auth/login",
            json=auth_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Auth Status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            auth_result = auth_response.json()
            token = auth_result.get("access_token")
            user_info = auth_result.get("user", {})
            print(f"   User Role: {user_info.get('role')}")
        else:
            print(f"   Auth Error: {auth_response.text}")
            return
            
    except Exception as e:
        print(f"   Auth Exception: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test /admin/settings/all endpoint in detail
    print(f"\n🔧 2. Testing /admin/settings/all...")
    try:
        response = requests.get(
            "https://atsai-jade.vercel.app/api/v1/admin/settings/all",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response type: {type(data)}")
            print(f"   Response content:")
            print(json.dumps(data, indent=2))
            
            if isinstance(data, dict):
                print(f"\n   Response keys: {list(data.keys())}")
                if 'settings' in data:
                    settings = data['settings']
                    print(f"   Settings array length: {len(settings)}")
                    if len(settings) == 0:
                        print("   ❌ PROBLEM: Settings array is empty!")
                    else:
                        print(f"   First setting: {settings[0]}")
                        
        else:
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_settings_all_endpoint()