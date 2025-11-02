#!/usr/bin/env python3
"""
Test Settings Page Authentication Fix
Tests the enhanced Settings page with auth refresh functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://atsai-jade.vercel.app"
FRONTEND_URL = "https://atsai-jade.vercel.app"

def test_backend_settings_api():
    """Test the backend settings API directly"""
    print("=" * 60)
    print("TESTING BACKEND SETTINGS API")
    print("=" * 60)
    
    # Login first
    login_data = {
        "email": "admin@ats.com",
        "password": "admin123"
    }
    
    print("1. Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    print(f"✅ Login successful, token received")
    
    # Test settings endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("\n2. Testing settings endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/settings/", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        settings = response.json()
        print(f"✅ Settings API working - Got {len(settings)} settings")
        for setting in settings[:3]:  # Show first 3
            print(f"  - {setting.get('category', 'N/A')}.{setting.get('key', 'N/A')}: {setting.get('value', 'N/A')}")
        return access_token
    else:
        print(f"❌ Settings API failed: {response.text}")
        return None

def test_frontend_settings_page():
    """Test the frontend settings page"""
    print("\n" + "=" * 60)
    print("FRONTEND SETTINGS PAGE INSTRUCTIONS")
    print("=" * 60)
    
    print("1. Open your browser and go to:")
    print(f"   {FRONTEND_URL}/admin/settings")
    
    print("\n2. Check if the page loads properly:")
    print("   - Should show a 'Refresh Auth' button (green)")
    print("   - Should show a 'Debug API' button (purple)")
    print("   - Should show a 'Restart Server' button (orange)")
    
    print("\n3. If the page shows 'Loading...':")
    print("   a) Click the 'Refresh Auth' button")
    print("   b) Wait for the refresh to complete")
    print("   c) The page should reload and show settings")
    
    print("\n4. If still loading after auth refresh:")
    print("   a) Click the 'Debug API' button")
    print("   b) Check the browser console for API test results")
    print("   c) The debug should show successful API call")
    
    print("\n5. Expected behavior after fix:")
    print("   - Settings should load and display")
    print("   - You should see categories like 'ai', 'database', 'email'")
    print("   - No infinite loading state")
    
    print("\n6. If you see errors, please share:")
    print("   - Browser console logs")
    print("   - Network tab in DevTools")
    print("   - Any error messages displayed")

def test_auth_flow():
    """Test the complete authentication flow"""
    print("\n" + "=" * 60)
    print("TESTING AUTHENTICATION FLOW")
    print("=" * 60)
    
    # Test token refresh
    login_data = {
        "email": "admin@ats.com", 
        "password": "admin123"
    }
    
    print("1. Testing login...")
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful")
        print(f"   Access token: {token_data.get('access_token', 'N/A')[:20]}...")
        print(f"   Refresh token: {token_data.get('refresh_token', 'N/A')[:20]}...")
        print(f"   User role: {token_data.get('user', {}).get('role', 'N/A')}")
        
        # Test token validation
        headers = {"Authorization": f"Bearer {token_data.get('access_token')}"}
        
        print("\n2. Testing token validation...")
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Token validation successful")
            print(f"   User: {user_data.get('email', 'N/A')}")
            print(f"   Role: {user_data.get('role', 'N/A')}")
            print(f"   Is active: {user_data.get('is_active', 'N/A')}")
        else:
            print(f"❌ Token validation failed: {response.status_code}")
    else:
        print(f"❌ Login failed: {response.status_code}")

def main():
    """Run all tests"""
    print("SETTINGS PAGE AUTHENTICATION FIX TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {FRONTEND_URL}")
    
    # Test backend API
    token = test_backend_settings_api()
    
    # Test auth flow
    test_auth_flow()
    
    # Provide frontend instructions
    test_frontend_settings_page()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if token:
        print("✅ Backend Settings API: WORKING")
        print("✅ Authentication: WORKING")
        print("⚠️  Frontend: Please test manually using instructions above")
        print("\nThe issue appears to be frontend-specific.")
        print("The auth refresh and debug buttons should resolve it.")
    else:
        print("❌ Backend Settings API: FAILED")
        print("❌ Need to investigate backend issues first")
    
    print(f"\nNext steps:")
    print("1. Test the frontend Settings page")
    print("2. Use the 'Refresh Auth' button if loading")
    print("3. Use the 'Debug API' button to test direct API calls")
    print("4. Report any remaining issues")

if __name__ == "__main__":
    main()