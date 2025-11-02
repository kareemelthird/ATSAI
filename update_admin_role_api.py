"""
Update Admin Role via API
"""
import requests
import json

def update_admin_role_via_api():
    """Update admin role to super_admin via API"""
    base_url = 'https://atsai-jade.vercel.app'
    
    print("🔧 Updating Admin Role via API...")
    print("=" * 40)
    
    # Step 1: Login as admin
    print("1. Logging in as admin...")
    login_data = {'email': 'admin@ats.com', 'password': 'admin123'}
    login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        user_id = tokens['user']['id']
        
        print(f"   ✅ Login successful")
        print(f"   Current role: {tokens['user']['role']}")
        print(f"   User ID: {user_id}")
        
        # Step 2: Update role to super_admin
        print("\n2. Updating role to super_admin...")
        update_data = {'role': 'super_admin'}
        update_response = requests.put(
            f'{base_url}/api/v1/users/{user_id}/role', 
            json=update_data,
            headers=headers
        )
        
        if update_response.status_code == 200:
            print("   ✅ Role updated successfully!")
            
            # Step 3: Verify the change
            print("\n3. Verifying role change...")
            me_response = requests.get(f'{base_url}/api/v1/auth/me', headers=headers)
            if me_response.status_code == 200:
                me_data = me_response.json()
                print(f"   New role: {me_data['role']}")
                if me_data['role'] == 'super_admin':
                    print("   ✅ Role change confirmed!")
                else:
                    print(f"   ⚠️ Role might not have updated yet: {me_data['role']}")
            else:
                print(f"   ❌ Verification failed: {me_response.status_code}")
                
        else:
            print(f"   ❌ Role update failed: {update_response.status_code}")
            print(f"   Error: {update_response.text}")
            
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(f"   Error: {login_response.text}")

if __name__ == "__main__":
    update_admin_role_via_api()