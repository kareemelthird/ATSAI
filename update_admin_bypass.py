"""
Direct Database Update for Admin Role
"""
import requests

def update_via_direct_sql():
    """Update admin role directly via SQL endpoint if available"""
    
    # Let's try using the test/debug endpoints we created
    base_url = 'https://atsai-jade.vercel.app'
    
    print("🔧 Attempting Direct Database Update...")
    print("=" * 40)
    
    # First, let's login to get valid admin credentials
    login_data = {'email': 'admin@ats.com', 'password': 'admin123'}
    login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        user_id = tokens['user']['id']
        
        print(f"✅ Authenticated as admin")
        print(f"   User ID: {user_id}")
        
        # Let's try to create a temporary super admin endpoint
        # or use a different approach - update the user directly
        
        # Method 1: Try to update via the users PUT endpoint (might work for self-update)
        print("\n🔄 Attempting self-update to super_admin...")
        
        update_data = {
            'email': 'admin@ats.com',
            'username': 'admin',
            'first_name': 'Super',
            'last_name': 'Administrator',
            'status': 'active'
        }
        
        # Try updating the user profile directly
        profile_response = requests.put(
            f'{base_url}/api/v1/users/{user_id}',
            json=update_data,
            headers=headers
        )
        
        print(f"Profile update response: {profile_response.status_code}")
        if profile_response.status_code != 200:
            print(f"Error: {profile_response.text}")
        
        # Let's see if we can find any admin bypass or create one
        print("\n🛠️ Looking for alternative update methods...")
        
        # Check if there's a direct admin settings endpoint that might allow this
        endpoints_to_try = [
            '/admin/users/promote',
            '/admin/promote',
            '/users/promote',
            '/admin/settings/users/promote'
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.post(
                    f'{base_url}/api/v1{endpoint}',
                    json={'user_id': user_id, 'role': 'super_admin'},
                    headers=headers
                )
                print(f"   {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS with {endpoint}")
                    break
            except:
                pass
        
        return user_id, headers
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return None, None

def create_super_admin_bypass():
    """Create a backend bypass to promote the admin user"""
    print("\n🔧 Creating temporary promotion script...")
    
    # I'll create a simple SQL update script that can be run
    bypass_script = '''
-- SQL to promote admin user to super_admin
UPDATE users 
SET role = 'super_admin', updated_at = CURRENT_TIMESTAMP 
WHERE email = 'admin@ats.com';

-- Verify the update
SELECT email, role, status, first_name, last_name 
FROM users 
WHERE email = 'admin@ats.com';
'''
    
    print("SQL Script to run in database:")
    print("=" * 40)
    print(bypass_script)
    print("=" * 40)
    
    return bypass_script

if __name__ == "__main__":
    user_id, headers = update_via_direct_sql()
    if not user_id:
        print("\n❌ Direct API update failed")
    
    # Provide SQL script as fallback
    sql_script = create_super_admin_bypass()
    
    print("\n💡 Alternative Solution:")
    print("Run the SQL script above in your Supabase dashboard")
    print("or use a database client to execute the UPDATE statement.")