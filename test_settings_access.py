"""
Test Settings Access for Admin User
"""
import requests

def test_settings_access():
    """Test settings access for admin user"""
    base_url = 'https://atsai-jade.vercel.app'
    
    print("🔍 Testing Settings Access...")
    print("=" * 40)
    
    # Login
    login_data = {'email': 'admin@ats.com', 'password': 'admin123'}
    login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        
        print(f"✅ Login successful")
        print(f"   User: {tokens['user']['email']}")
        print(f"   Role: {tokens['user']['role']}")
        print(f"   Status: {tokens['user']['status']}")
        
        # Test different settings endpoints
        settings_endpoints = [
            '/settings/',
            '/settings/public/project-info',
            '/admin/settings/all',
            '/admin/settings/ai',
            '/admin/settings/system',
        ]
        
        print(f"\n🔐 Testing Settings Endpoints:")
        for endpoint in settings_endpoints:
            try:
                response = requests.get(f'{base_url}/api/v1{endpoint}', headers=headers)
                status_icon = "✅" if response.status_code == 200 else "❌" if response.status_code in [401, 403] else "⚠️"
                print(f"   {endpoint}: {response.status_code} {status_icon}")
                
                if response.status_code not in [200, 404]:
                    print(f"      Error: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   {endpoint}: ERROR - {e}")
        
        # Check if the issue is with the authentication context
        print(f"\n🔍 User Authentication Details:")
        me_response = requests.get(f'{base_url}/api/v1/auth/me', headers=headers)
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"   Current user role: {me_data['role']}")
            print(f"   Is Admin (backend): {me_data['role'] in ['admin', 'super_admin']}")
        
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    test_settings_access()