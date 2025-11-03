#!/usr/bin/env python3

import requests
import json

def check_current_settings():
    """Check what settings currently exist and their values"""
    
    print("🔧 Checking current settings...")
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
    
    # Get all settings
    print("🔧 Current settings in database:")
    try:
        settings_response = requests.get(
            "https://atsai-jade.vercel.app/api/v1/settings/",
            headers=headers
        )
        
        if settings_response.status_code == 200:
            settings = settings_response.json()
            print(f"   Total settings: {len(settings)}")
            
            print(f"\n   All settings:")
            for i, setting in enumerate(settings, 1):
                key = setting.get('key', 'NO_KEY')
                value = setting.get('value', '')
                category = setting.get('category', 'unknown')
                
                # Show value status
                if value:
                    value_status = f"'{value[:30]}{'...' if len(value) > 30 else ''}'"
                else:
                    value_status = "EMPTY"
                
                print(f"   {i:2d}. {category:12s} | {key:30s} | {value_status}")
                
        else:
            print(f"   ❌ Failed to fetch settings: {settings_response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    check_current_settings()