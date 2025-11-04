"""
Check if the production database migration has been applied
"""
import requests

def check_migration_status():
    """Check if the custom instructions migration has been applied"""
    print("🔍 Checking Production Database Migration Status")
    print("=" * 55)
    
    base_url = "https://atsai-jade.vercel.app"
    
    # Test 1: Check health endpoint
    print("1️⃣ Backend Health Check...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Backend is healthy and responding")
        else:
            print(f"   ❌ Backend issue: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot reach backend: {e}")
        return
    
    # Test 2: Try login to see if 500 error is fixed
    print("\n2️⃣ Testing Login Endpoint...")
    try:
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
            timeout=10
        )
        
        if login_response.status_code == 500:
            print("   ❌ 500 Error - Migration NOT applied yet")
            print("   📋 The custom instruction fields are missing from the database")
        elif login_response.status_code == 401:
            print("   ✅ Login endpoint working - Returns 401 (expected for wrong credentials)")
            print("   🎉 Migration appears to be applied successfully!")
        else:
            print(f"   ⚠️  Unexpected status: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")
    
    # Test 3: Check if we can access any authenticated endpoints
    print("\n3️⃣ Testing Custom Instructions Endpoint...")
    try:
        # This should return 401/403 (not 500) if migration is applied
        custom_response = requests.get(
            f"{base_url}/api/v1/users/me/custom-instructions",
            timeout=10
        )
        
        if custom_response.status_code == 500:
            print("   ❌ Custom instructions endpoint returns 500 - Migration needed")
        elif custom_response.status_code in [401, 403]:
            print("   ✅ Custom instructions endpoint exists - Migration successful")
        else:
            print(f"   ⚠️  Status: {custom_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Custom instructions test failed: {e}")
    
    print("\n" + "=" * 55)
    print("📋 Migration Status Summary:")
    print("If you see 500 errors above: Run the SQL migration script")
    print("If you see 401/403 errors: Migration successful, features ready!")

if __name__ == "__main__":
    check_migration_status()