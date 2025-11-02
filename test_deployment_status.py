import requests
import time

def test_deployment():
    """Test the Vercel deployment status"""
    base_url = "https://atsai-jade.vercel.app"
    
    print("🔍 Testing ATS/AI Application Deployment...")
    print(f"📍 Base URL: {base_url}")
    print("=" * 50)
    
    # Test frontend
    try:
        print("1. Testing Frontend...")
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
        else:
            print(f"   ❌ Frontend returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend failed: {e}")
    
    # Test backend endpoints
    endpoints = [
        "/api/settings/system",
        "/api/v1/health", 
        "/api/auth/login",
        "/api/docs"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n2. Testing {endpoint}...")
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Endpoint working")
                try:
                    data = response.json()
                    print(f"   📄 Response preview: {str(data)[:100]}...")
                except:
                    print(f"   📄 Response length: {len(response.text)} chars")
            elif response.status_code == 404:
                print("   ⚠️  Endpoint not found")
            elif response.status_code == 422:
                print("   ⚠️  Validation error (expected for some endpoints)")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Deployment test completed!")

if __name__ == "__main__":
    test_deployment()