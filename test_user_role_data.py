"""
Check User Role Data Across Endpoints
"""
import requests
import json

def check_user_role_data():
    """Check the user role data across different endpoints"""
    base_url = 'https://atsai-jade.vercel.app'
    
    print("🔍 Checking User Role Data...")
    print("=" * 50)
    
    # Login
    login_data = {'email': 'admin@ats.com', 'password': 'admin123'}
    login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        
        print("1. Login Response User Data:")
        user_data = tokens["user"]
        print(f"   Email: {user_data['email']}")
        print(f"   Role: {user_data['role']}")
        print(f"   Status: {user_data['status']}")
        print(f"   First Name: {user_data.get('first_name', 'N/A')}")
        print(f"   Last Name: {user_data.get('last_name', 'N/A')}")
        print()
        
        # Check /auth/me endpoint
        print("2. Auth/Me Endpoint:")
        me_response = requests.get(f'{base_url}/api/v1/auth/me', headers=headers)
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"   Email: {me_data['email']}")
            print(f"   Role: {me_data['role']}")
            print(f"   Status: {me_data['status']}")
            print(f"   First Name: {me_data.get('first_name', 'N/A')}")
            print(f"   Last Name: {me_data.get('last_name', 'N/A')}")
        else:
            print(f"   Error: {me_response.status_code} - {me_response.text}")
        print()
        
        # Check users endpoint
        print("3. Users Endpoint (admin@ats.com):")
        users_response = requests.get(f'{base_url}/api/v1/users/', headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            admin_user = next((u for u in users if u['email'] == 'admin@ats.com'), None)
            if admin_user:
                print(f"   Email: {admin_user['email']}")
                print(f"   Role: {admin_user['role']}")
                print(f"   Status: {admin_user['status']}")
                print(f"   First Name: {admin_user.get('first_name', 'N/A')}")
                print(f"   Last Name: {admin_user.get('last_name', 'N/A')}")
                print(f"   ID: {admin_user['id']}")
            else:
                print("   Admin user not found in users list")
                print(f"   Total users found: {len(users)}")
        else:
            print(f"   Error: {users_response.status_code} - {users_response.text}")
        print()
        
        # Test settings access
        print("4. Settings Access Test:")
        settings_response = requests.get(f'{base_url}/api/v1/settings/', headers=headers)
        print(f"   Settings endpoint: {settings_response.status_code}")
        if settings_response.status_code != 200:
            print(f"   Error: {settings_response.text[:200]}")
        
        admin_settings_response = requests.get(f'{base_url}/api/v1/admin/settings/all', headers=headers)
        print(f"   Admin settings: {admin_settings_response.status_code}")
        if admin_settings_response.status_code != 200:
            print(f"   Error: {admin_settings_response.text[:200]}")
        
    else:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")

if __name__ == "__main__":
    check_user_role_data()