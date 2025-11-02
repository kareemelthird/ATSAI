"""
Test Frontend Integration - Simulate Browser Behavior
"""
import requests
import json

def test_frontend_browser_simulation():
    """Simulate what the browser is doing when accessing the frontend"""
    base_url = "https://atsai-jade.vercel.app"
    
    print("🔍 Testing Frontend Browser Simulation...")
    print("=" * 50)
    
    # Create a session to maintain cookies like a browser
    session = requests.Session()
    
    # Test 1: Get the frontend page
    print("\n1. Loading frontend page...")
    frontend_response = session.get(base_url)
    print(f"   Frontend status: {frontend_response.status_code}")
    print(f"   Content type: {frontend_response.headers.get('content-type', 'N/A')}")
    
    # Test 2: Login via API
    print("\n2. Logging in via API...")
    login_data = {
        'email': 'admin@ats.com',
        'password': 'admin123'
    }
    
    login_response = session.post(f"{base_url}/api/v1/auth/login", json=login_data)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        access_token = tokens['access_token']
        print(f"   ✅ Login successful")
        print(f"   User: {tokens['user']['email']} ({tokens['user']['role']})")
        
        # Test 3: Access protected endpoints with token
        print("\n3. Testing protected endpoints...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test users endpoint
        users_response = session.get(f"{base_url}/api/v1/users/", headers=headers)
        print(f"   Users endpoint: {users_response.status_code}")
        
        if users_response.status_code != 200:
            print(f"   Error: {users_response.text[:200]}")
        
        # Test auth/me endpoint
        me_response = session.get(f"{base_url}/api/v1/auth/me", headers=headers)
        print(f"   Auth/me endpoint: {me_response.status_code}")
        
        if me_response.status_code != 200:
            print(f"   Error: {me_response.text[:200]}")
        
        # Test settings endpoint
        settings_response = session.get(f"{base_url}/api/v1/settings/", headers=headers)
        print(f"   Settings endpoint: {settings_response.status_code}")
        
        if settings_response.status_code != 200:
            print(f"   Error: {settings_response.text[:200]}")
    else:
        print(f"   ❌ Login failed: {login_response.text}")
    
    # Test 4: Test a few specific problematic endpoints
    print("\n4. Testing problematic endpoints...")
    
    # Test without token (should get 401)
    no_auth_response = session.get(f"{base_url}/api/v1/users/")
    print(f"   Users without auth: {no_auth_response.status_code} (expected 401)")
    
    # Test with invalid token
    bad_headers = {'Authorization': 'Bearer invalid_token'}
    bad_auth_response = session.get(f"{base_url}/api/v1/users/", headers=bad_headers)
    print(f"   Users with bad token: {bad_auth_response.status_code} (expected 401)")
    
    print("\n" + "=" * 50)
    print("🎯 Frontend Browser Simulation Complete")

if __name__ == "__main__":
    test_frontend_browser_simulation()