#!/usr/bin/env python3

import requests
import json

def initialize_default_settings():
    """Use the initialize endpoint to create default settings"""
    
    print("🔧 Initializing default settings...")
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
    
    # Use the initialize endpoint
    print("🔧 Calling /settings/initialize endpoint...")
    try:
        response = requests.post(
            "https://atsai-jade.vercel.app/api/v1/settings/initialize",
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✅ Response: {data}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Now check if settings are populated
    print("\n🔧 Checking settings after initialization...")
    try:
        settings_response = requests.get(
            "https://atsai-jade.vercel.app/api/v1/settings/",
            headers=headers
        )
        
        if settings_response.status_code == 200:
            settings = settings_response.json()
            print(f"   ✅ Settings count: {len(settings)}")
            print(f"   Sample settings:")
            for setting in settings[:3]:
                print(f"      - {setting['key']}: {setting['value'][:50]}...")
        else:
            print(f"   ❌ Failed to fetch settings: {settings_response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception checking settings: {e}")

if __name__ == "__main__":
    initialize_default_settings()