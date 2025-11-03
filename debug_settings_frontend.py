#!/usr/bin/env python3
"""
Debug Settings Frontend Rendering Issue
Specific test to understand why Settings page shows loading despite API working
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://atsai-jade.vercel.app"

def test_settings_step_by_step():
    """Test each step of the Settings page process"""
    print("=" * 60)
    print("STEP-BY-STEP SETTINGS DEBUG")
    print("=" * 60)
    
    # 1. Login and get token
    print("Step 1: Login")
    login_data = {
        "email": "kareemelthird@gmail.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token_data = response.json()
    token = token_data.get("access_token")
    user_info = token_data.get("user", {})
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Login successful: {user_info.get('email')}")
    print(f"   Role: {user_info.get('role')}")
    print(f"   Token length: {len(token) if token else 0}")
    
    # 2. Test direct Settings API
    print("\nStep 2: Direct Settings API call")
    settings_response = requests.get(f"{BASE_URL}/api/v1/settings/", headers=headers)
    
    print(f"   Status: {settings_response.status_code}")
    print(f"   Content-Type: {settings_response.headers.get('content-type', 'N/A')}")
    
    if settings_response.status_code == 200:
        try:
            settings = settings_response.json()
            print(f"   ✅ Settings count: {len(settings)}")
            
            # Check categories
            categories = {}
            for setting in settings:
                cat = setting.get('category', 'unknown')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(setting.get('key'))
            
            print(f"   📂 Categories: {list(categories.keys())}")
            for cat, keys in categories.items():
                print(f"      {cat}: {len(keys)} settings")
            
            # Check specific settings that frontend might expect
            expected_settings = ['AI_PROVIDER', 'DATABASE_URL', 'GROQ_API_KEY']
            found_settings = [s.get('key') for s in settings]
            
            print(f"\n   🔍 Expected settings check:")
            for expected in expected_settings:
                status = "✅" if expected in found_settings else "❌"
                print(f"      {status} {expected}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON decode error: {e}")
            print(f"   Raw response: {settings_response.text[:200]}...")
            return False
    else:
        print(f"   ❌ API failed: {settings_response.text}")
        return False

def check_frontend_expectations():
    """Check what the frontend might be expecting"""
    print("\n" + "=" * 60)
    print("FRONTEND EXPECTATIONS CHECK")
    print("=" * 60)
    
    print("The frontend Settings component expects:")
    print("1. ✅ API endpoint: /api/v1/settings/")
    print("2. ✅ Authorization header: Bearer token")
    print("3. ✅ Response format: Array of setting objects")
    print("4. ✅ Setting object structure:")
    print("   - key: string")
    print("   - value: string") 
    print("   - category: string")
    print("   - label: string")
    print("   - description: string")
    print("   - data_type: string")
    print("   - requires_restart: boolean")
    
    print("\nPossible frontend issues:")
    print("1. 🔍 fetchSettings() not completing properly")
    print("2. 🔍 setSettings() not updating state")
    print("3. 🔍 filteredSettings logic filtering out all settings")
    print("4. 🔍 Loading state not updating to false")
    print("5. 🔍 Error state blocking display")
    print("6. 🔍 React component not re-rendering")

def test_frontend_simulation():
    """Simulate what the frontend does"""
    print("\n" + "=" * 60)  
    print("FRONTEND SIMULATION")
    print("=" * 60)
    
    # Login
    login_data = {
        "email": "kareemelthird@gmail.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get settings
    settings_response = requests.get(f"{BASE_URL}/api/v1/settings/", headers=headers)
    
    if settings_response.status_code != 200:
        print("❌ Settings API failed")
        return
    
    settings = settings_response.json()
    print(f"📥 Retrieved {len(settings)} settings")
    
    # Simulate frontend filtering for 'ai_provider' category (default)
    active_category = 'ai_provider'
    filtered_settings = []
    
    for setting in settings:
        if setting.get('category') == active_category:
            # Check AI provider filtering logic
            if setting.get('category') == 'ai_provider':
                # Always show AI_PROVIDER and USE_MOCK_AI
                if setting.get('key') in ['AI_PROVIDER', 'USE_MOCK_AI']:
                    filtered_settings.append(setting)
                    continue
                
                # Always show instruction fields
                if setting.get('key') in ['resume_analysis_instructions', 'chat_system_instructions']:
                    filtered_settings.append(setting)
                    continue
                
                # Provider-specific filtering (assuming groq as default)
                current_provider = 'groq'  # Default
                
                if setting.get('key', '').find('GROQ') != -1 and current_provider == 'groq':
                    filtered_settings.append(setting)
                elif setting.get('key', '').find('DEEPSEEK') != -1 and current_provider == 'deepseek':
                    filtered_settings.append(setting)
                elif setting.get('key', '').find('OPENROUTER') != -1 and current_provider == 'openrouter':
                    filtered_settings.append(setting)
                elif not any(provider in setting.get('key', '') for provider in ['GROQ', 'DEEPSEEK', 'OPENROUTER']):
                    # Include settings that don't have provider-specific names
                    filtered_settings.append(setting)
    
    print(f"🔽 Filtered to {len(filtered_settings)} settings for '{active_category}' category")
    
    if len(filtered_settings) == 0:
        print("❌ PROBLEM FOUND: No settings pass the filtering logic!")
        print("   This would show 'No settings found in this category'")
    else:
        print("✅ Filtered settings:")
        for setting in filtered_settings:
            print(f"   - {setting.get('key')}: {setting.get('label')}")

def main():
    """Run comprehensive Settings debug"""
    print("SETTINGS FRONTEND DEBUG")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    
    # Test step by step
    api_success = test_settings_step_by_step()
    
    # Check frontend expectations
    check_frontend_expectations()
    
    # Simulate frontend logic
    test_frontend_simulation()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if api_success:
        print("✅ Backend API is working correctly")
        print("❌ Issue is in frontend JavaScript logic")
        print()
        print("Next steps:")
        print("1. Open browser DevTools Console on Settings page")
        print("2. Look for these debug logs:")
        print("   - '🚀 fetchSettings() CALLED - START'")
        print("   - '✅ Settings response: 200'")
        print("   - '⏳ Loading state: false'")
        print("   - '📝 Total settings: 18'")
        print("   - '🎯 Filtered settings: X'")
        print()
        print("3. If filtered settings = 0, the filtering logic is the problem")
        print("4. If loading state = true, the setLoading(false) isn't working")
        print("5. If no logs appear, fetchSettings() isn't being called")
    else:
        print("❌ Backend API has issues - fix those first")

if __name__ == "__main__":
    main()