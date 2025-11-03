#!/usr/bin/env python3

import requests
import json

def test_settings_save_endpoint():
    """Test the settings save endpoint that UnifiedSettings uses"""
    
    print("🔧 Testing settings save functionality...")
    print("-" * 60)
    
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
    
    # Test the bulk-update endpoint that UnifiedSettings uses
    print("🔧 Testing /admin/settings/bulk-update endpoint...")
    
    # Simple test data
    test_data = [
        {"setting_key": "PROJECT_NAME", "setting_value": "ATS System Test"}
    ]
    
    try:
        response = requests.post(
            "https://atsai-jade.vercel.app/api/v1/admin/settings/bulk-update",
            json=test_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   ✅ Success: {response.json()}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Also test individual setting update 
    print("\n🔧 Testing individual setting update...")
    try:
        update_data = {
            "setting_value": "ATS System Individual Test",
            "is_active": True
        }
        
        response = requests.put(
            "https://atsai-jade.vercel.app/api/v1/settings/PROJECT_NAME",
            json=update_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   ✅ Success: {response.json()}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_settings_save_endpoint()