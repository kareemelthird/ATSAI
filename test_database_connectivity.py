import os
import requests
from urllib.parse import urlparse

def test_database_connectivity():
    """Test database connectivity and configuration"""
    print("🔍 Testing Database Connectivity...")
    print("=" * 50)
    
    # Test health endpoint for database status
    try:
        response = requests.get("https://atsai-jade.vercel.app/api/v1/health")
        health_data = response.json()
        print(f"Health Status: {health_data}")
        
        if health_data.get('database_status') == 'error':
            print("❌ Database connection is failing in production")
            print("🔍 This could be due to:")
            print("   1. Database URL configuration")
            print("   2. Connection pool settings")
            print("   3. SQLAlchemy version compatibility")
            print("   4. Supabase connection string format")
        else:
            print("✅ Database connection is working")
            
    except Exception as e:
        print(f"❌ Failed to test health endpoint: {e}")
    
    print("\n" + "=" * 50)
    
    # Test other database-dependent endpoints
    print("🔍 Testing database-dependent endpoints...")
    
    endpoints_to_test = [
        "/api/v1/settings/system",
        "/api/v1/users/me", 
        "/api/v1/candidates",
        "/api/v1/jobs"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = f"https://atsai-jade.vercel.app{endpoint}"
            response = requests.get(url)
            print(f"{endpoint}: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   ❌ Internal server error - likely database related")
            elif response.status_code == 401:
                print(f"   🔐 Unauthorized - endpoint requires authentication")
            elif response.status_code == 404:
                print(f"   ⚠️  Endpoint not found")
            elif response.status_code == 200:
                print(f"   ✅ Working")
            else:
                print(f"   📄 Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_database_connectivity()