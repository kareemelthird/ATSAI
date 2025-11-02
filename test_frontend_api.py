"""
Test Frontend API Calls Directly
"""
import requests
import json

def test_frontend_api_calls():
    """Test what the frontend should be receiving"""
    base_url = 'https://atsai-jade.vercel.app'
    
    print("🔍 Testing Frontend API Calls...")
    print("=" * 50)
    
    # Step 1: Login
    print("1. Login...")
    login_data = {'email': 'admin@ats.com', 'password': 'admin123'}
    login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        
        print("   ✅ Login successful")
        print(f"   Token user role: {tokens['user']['role']}")
        
        # Step 2: Fetch users (what the Users page does)
        print("\n2. Fetch users (Users page API call)...")
        users_response = requests.get(f'{base_url}/api/v1/users/', headers=headers)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            print(f"   ✅ Users fetched successfully")
            print(f"   Total users: {len(users_data)}")
            
            # Find admin user
            admin_user = next((u for u in users_data if u['email'] == 'admin@ats.com'), None)
            if admin_user:
                print(f"   Admin user found:")
                print(f"     Email: {admin_user['email']}")
                print(f"     Role: {admin_user['role']}")
                print(f"     Status: {admin_user['status']}")
                print(f"     First Name: {admin_user.get('first_name', 'N/A')}")
                print(f"     Last Name: {admin_user.get('last_name', 'N/A')}")
                
                # Show how it would display in UI
                role_display = admin_user['role'].replace('_', ' ').upper()
                print(f"     UI Display: {role_display}")
            else:
                print("   ❌ Admin user not found")
        else:
            print(f"   ❌ Users fetch failed: {users_response.status_code}")
            print(f"   Error: {users_response.text}")
            
        # Step 3: Check settings access
        print("\n3. Settings access...")
        settings_response = requests.get(f'{base_url}/api/v1/settings/', headers=headers)
        admin_settings_response = requests.get(f'{base_url}/api/v1/admin/settings/all', headers=headers)
        
        print(f"   Settings: {settings_response.status_code}")
        print(f"   Admin Settings: {admin_settings_response.status_code}")
        
        if settings_response.status_code == 200:
            print("   ✅ Settings accessible")
        else:
            print(f"   ❌ Settings error: {settings_response.text[:100]}")
            
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    test_frontend_api_calls()