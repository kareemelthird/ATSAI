"""
Debug Role Update API Call
"""
import requests
import json

def debug_role_update():
    """Debug the exact API call for role update"""
    base_url = 'https://atsai-jade.vercel.app'
    
    print("🔍 Debugging Role Update API...")
    print("=" * 40)
    
    # Login
    login_data = {'email': 'admin@ats.com', 'password': 'admin123'}
    login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {
            'Authorization': f'Bearer {tokens["access_token"]}',
            'Content-Type': 'application/json'
        }
        user_id = tokens['user']['id']
        
        print(f"✅ Login successful")
        print(f"   User ID: {user_id}")
        print(f"   Current role: {tokens['user']['role']}")
        
        # Test different API call formats
        endpoints_to_test = [
            (f'/users/{user_id}/role', {'role': 'super_admin'}),
            (f'/users/{user_id}', {'role': 'super_admin'}),
            ('/users/me/role', {'role': 'super_admin'}),
        ]
        
        for endpoint, data in endpoints_to_test:
            print(f"\n🔄 Testing: PUT {endpoint}")
            print(f"   Data: {data}")
            
            try:
                response = requests.put(
                    f'{base_url}/api/v1{endpoint}',
                    json=data,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS!")
                    print(f"   Response: {response.json()}")
                    break
                else:
                    print(f"   Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   Error: {e}")
        
        # Also test the health of the users endpoint
        print(f"\n🔍 Testing users endpoint health...")
        users_response = requests.get(f'{base_url}/api/v1/users/', headers=headers)
        print(f"   Users list: {users_response.status_code}")
        
        if users_response.status_code == 200:
            users = users_response.json()
            admin_user = next((u for u in users if u['email'] == 'admin@ats.com'), None)
            if admin_user:
                print(f"   Current admin role: {admin_user['role']}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    debug_role_update()