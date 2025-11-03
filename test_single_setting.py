#!/usr/bin/env python3

import requests
import json

def test_single_setting_update():
    """Test updating a single setting to understand the API format"""
    
    print("🔧 Testing single setting update...")
    print("-" * 50)
    
    # Login first
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
    
    # Test different payload formats
    test_payloads = [
        {"setting_value": "test_value", "is_active": True},
        {"value": "test_value", "is_active": True},
        {"setting_value": "test_value"},
        {"value": "test_value"}
    ]
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\n🔧 Test {i}: {payload}")
        try:
            response = requests.put(
                "https://atsai-jade.vercel.app/api/v1/settings/PROJECT_NAME",
                json=payload,
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   ✅ Success: {response.json()}")
                return  # Found working format
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_single_setting_update()