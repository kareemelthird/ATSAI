#!/usr/bin/env python3

import requests
import json
import sys

def test_unified_settings_api():
    """Test the /admin/settings/all API endpoint that UnifiedSettings uses"""
    
    print("🔧 Testing UnifiedSettings API endpoints...")
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
            print(f"   User Name: {user_info.get('full_name')}")
            print(f"   Token: {token[:20]}..." if token else "   No token")
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
    
    # Test the exact endpoints UnifiedSettings uses
    endpoints_to_test = [
        "/api/v1/admin/settings/all",
        "/api/v1/admin/stats/system", 
        "/api/v1/admin/users/usage",
        "/api/v1/admin/usage/history"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🔧 2. Testing {endpoint}...")
        try:
            response = requests.get(
                f"https://atsai-jade.vercel.app{endpoint}",
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if endpoint == "/admin/settings/all":
                    print(f"   Full response: {data}")
                    if isinstance(data, dict):
                        print(f"   Response keys: {list(data.keys())}")
                        if 'settings' in data:
                            settings = data['settings']
                            print(f"   Settings array length: {len(settings)}")
                            print(f"   Settings content: {settings}")
                        if 'parsed_values' in data:
                            print(f"   Parsed values keys: {list(data['parsed_values'].keys())}")
                    else:
                        print(f"   Data type: {type(data)}")
                        print(f"   Data content: {data}")
                elif endpoint == "/admin/stats/system":
                    print(f"   Stats keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                elif endpoint == "/admin/users/usage":
                    if isinstance(data, dict) and 'users' in data:
                        print(f"   Users count: {len(data['users'])}")
                    else:
                        print(f"   Usage data type: {type(data)}")
                elif endpoint == "/admin/usage/history":
                    print(f"   History data type: {type(data)}")
                    if isinstance(data, list):
                        print(f"   History records: {len(data)}")
            else:
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Exception: {e}")
    
    print("\n🔧 Summary:")
    print("   - UnifiedSettings uses /admin/settings/all (not /admin/settings)")
    print("   - Test completed")

if __name__ == "__main__":
    test_unified_settings_api()