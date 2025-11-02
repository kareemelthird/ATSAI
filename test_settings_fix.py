#!/usr/bin/env python3
"""
Test the fixed Settings page functionality
"""
import requests

def test_settings_page_fix():
    base_url = "https://atsai-jade.vercel.app"
    
    print("🔧 Testing Fixed Settings Page")
    print("=" * 40)
    
    # Login
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test settings endpoint
    print("\n📋 Testing settings endpoint...")
    settings_response = requests.get(f"{base_url}/api/v1/settings", headers=headers)
    
    print(f"Settings Status: {settings_response.status_code}")
    
    if settings_response.status_code == 200:
        settings = settings_response.json()
        print(f"✅ Settings loaded: {len(settings)} settings found")
        
        # Group by category
        categories = {}
        for setting in settings:
            cat = setting.get('category', 'unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(setting)
        
        print(f"\n📂 Categories found: {list(categories.keys())}")
        
        # Show AI-related settings
        if 'ai_provider' in categories:
            print(f"\n🤖 AI Provider Settings ({len(categories['ai_provider'])}):")
            for setting in categories['ai_provider']:
                print(f"   - {setting.get('key')}: {setting.get('label')}")
                print(f"     Value: {setting.get('value', 'Empty')[:50]}...")
        
        # Show instruction settings
        instruction_settings = [s for s in settings if 'instruction' in s.get('key', '').lower()]
        print(f"\n📝 AI Instruction Settings ({len(instruction_settings)}):")
        for setting in instruction_settings:
            print(f"   - {setting.get('key')}: {setting.get('label')}")
            print(f"     Description: {setting.get('description', 'No description')}")
            print(f"     Data Type: {setting.get('data_type', 'unknown')}")
            print(f"     Value Length: {len(setting.get('value', ''))} characters")
        
        return True
    else:
        print(f"❌ Settings failed: {settings_response.text}")
        return False

if __name__ == "__main__":
    test_settings_page_fix()