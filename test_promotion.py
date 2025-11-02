"""
Test the Promotion Endpoint
"""
import requests

def test_promotion_endpoint():
    """Test the new promotion endpoint"""
    base_url = 'https://atsai-jade.vercel.app'
    
    print("🚀 Testing Admin Promotion Endpoint...")
    print("=" * 40)
    
    # Login
    login_data = {'email': 'admin@ats.com', 'password': 'admin123'}
    login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        
        print(f"✅ Login successful")
        print(f"   Current role: {tokens['user']['role']}")
        
        # Test the promotion endpoint
        promote_response = requests.post(
            f'{base_url}/api/v1/admin/promote-to-super-admin',
            headers=headers
        )
        
        print(f"\n🔄 Promotion attempt: {promote_response.status_code}")
        
        if promote_response.status_code == 200:
            promo_data = promote_response.json()
            print("✅ Promotion successful!")
            print(f"   New role: {promo_data['user']['role']}")
            
            # Verify with fresh login
            print("\n🔍 Verifying with fresh auth check...")
            me_response = requests.get(f'{base_url}/api/v1/auth/me', headers=headers)
            if me_response.status_code == 200:
                me_data = me_response.json()
                print(f"   Verified role: {me_data['role']}")
                
                if me_data['role'] == 'super_admin':
                    print("🎉 SUCCESS! Admin promoted to Super Admin!")
                    
                    # Test settings access
                    print("\n🔐 Testing settings access...")
                    settings_response = requests.get(f'{base_url}/api/v1/settings/', headers=headers)
                    admin_settings_response = requests.get(f'{base_url}/api/v1/admin/settings/all', headers=headers)
                    
                    print(f"   Settings: {settings_response.status_code}")
                    print(f"   Admin Settings: {admin_settings_response.status_code}")
                    
                    if settings_response.status_code == 200 and admin_settings_response.status_code == 200:
                        print("✅ Full settings access confirmed!")
                    else:
                        print("⚠️ Settings access may have issues")
                
        else:
            print(f"❌ Promotion failed: {promote_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    test_promotion_endpoint()