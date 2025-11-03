#!/usr/bin/env python3

import requests
import json

def compare_settings_endpoints():
    """Compare the two settings endpoints"""
    
    print("🔧 Comparing settings endpoints...")
    print("-" * 60)
    
    # Test authentication
    auth_data = {"email": "admin@ats.com", "password": "admin123"}
    
    auth_response = requests.post(
        "https://atsai-jade.vercel.app/api/v1/auth/login",
        json=auth_data,
        headers={"Content-Type": "application/json"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.text}")
        return
        
    token = auth_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test both endpoints
    endpoints = [
        "/api/v1/ai/settings",           # Working endpoint (18 settings)
        "/api/v1/admin/settings/all"     # Broken endpoint (0 settings)
    ]
    
    for endpoint in endpoints:
        print(f"\n🔧 Testing {endpoint}...")
        try:
            response = requests.get(f"https://atsai-jade.vercel.app{endpoint}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if endpoint == "/api/v1/ai/settings":
                    # This should be an array
                    print(f"   Type: {type(data)}")
                    if isinstance(data, list):
                        print(f"   Count: {len(data)}")
                        if len(data) > 0:
                            print(f"   First item keys: {list(data[0].keys())}")
                            print(f"   Sample setting: {data[0]['setting_key']} = {data[0]['setting_value']}")
                
                elif endpoint == "/api/v1/admin/settings/all":
                    # This should be a dict with settings array
                    print(f"   Type: {type(data)}")
                    if isinstance(data, dict):
                        settings = data.get('settings', [])
                        print(f"   Settings count: {len(settings)}")
                        print(f"   Parsed values count: {len(data.get('parsed_values', {}))}")
                        
            else:
                print(f"   Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   Exception: {e}")

if __name__ == "__main__":
    compare_settings_endpoints()