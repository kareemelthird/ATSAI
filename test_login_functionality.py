import requests
import json

def test_login_functionality():
    """Test the login system with various credential formats"""
    base_url = "https://atsai-jade.vercel.app"
    login_url = f"{base_url}/api/v1/auth/login"
    
    print("🔍 Testing Login Functionality...")
    print("=" * 50)
    
    # Test different credential formats
    test_credentials = [
        {"email": "admin@ats.local", "password": "admin123"},
        {"email": "admin@example.com", "password": "admin123"},
        {"username": "admin@ats.local", "password": "admin123"},
        {"email": "admin", "password": "admin123"}
    ]
    
    for i, creds in enumerate(test_credentials, 1):
        print(f"\n{i}. Testing credentials: {creds}")
        try:
            response = requests.post(login_url, json=creds, headers={"Content-Type": "application/json"})
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                try:
                    error_detail = response.json()
                    print(f"   Validation Error: {error_detail}")
                except:
                    print(f"   Raw response: {response.text[:200]}")
            elif response.status_code == 200:
                print(f"   ✅ Login successful!")
                try:
                    data = response.json()
                    print(f"   Token received: {bool(data.get('access_token'))}")
                except:
                    print(f"   Response: {response.text[:100]}")
            elif response.status_code == 401:
                print(f"   ❌ Invalid credentials")
            elif response.status_code == 500:
                print(f"   ❌ Server error - likely database connection issue")
            else:
                print(f"   📄 Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Login test completed!")

if __name__ == "__main__":
    test_login_functionality()