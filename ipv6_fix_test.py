"""
IPv6 Connectivity Fix for Vercel + Supabase Deployment
======================================================

ISSUE: Vercel serverless functions cannot connect to Supabase database via IPv6
ERROR: "Cannot assign requested address" when connecting to IPv6 address

SOLUTIONS TO TRY (in order of preference):

1. Use Supabase Connection Pooler (RECOMMENDED)
   - More reliable for serverless environments
   - Built specifically for short-lived connections
   - IPv4/IPv6 agnostic

2. Use IPv4-only connection string
   - Force connection to IPv4 address if available

3. Configure connection parameters for serverless optimization

"""

import requests
import sys

def test_connection_solutions():
    """Test various database connection solutions"""
    
    print("🔍 TESTING IPv6 CONNECTIVITY SOLUTIONS")
    print("=" * 60)
    
    base_url = "https://atsai-jade.vercel.app"
    
    # Test current status
    print("1. Current Status Check")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        health = response.json()
        print(f"   Backend: {health['status']}")
        print(f"   Database: {health['database_status']}")
        if health['database_status'] == 'error':
            error_msg = health.get('database_info', '')
            if 'IPv6' in error_msg or '2a05:d016' in error_msg:
                print("   ❌ Confirmed: IPv6 connectivity issue")
            else:
                print(f"   Error: {error_msg[:100]}...")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
    
    # Test login endpoint
    print("\n2. Login Endpoint Test")
    try:
        login_data = {"email": "admin@ats.com", "password": "Admin@123"}
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 500:
            print("   ❌ Database connection blocking login")
        elif response.status_code == 422:
            print("   ⚠️  Login endpoint working, validation error")
        elif response.status_code == 200:
            print("   ✅ Login working!")
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🛠️  RECOMMENDED SOLUTIONS:")
    print("=" * 60)
    
    print("OPTION 1 - Use Supabase Connection Pooler:")
    print("  Replace DATABASE_URL with pooler URL:")
    print("  postgresql://postgres:Nevertry%4012@aws-0-us-east-1.pooler.supabase.co:6543/postgres?pgbouncer=true")
    
    print("\nOPTION 2 - Check Supabase IPv4 Settings:")
    print("  1. Go to Supabase Dashboard → Settings → Database")
    print("  2. Look for IPv4 connection string option")
    print("  3. Use IPv4-only connection if available")
    
    print("\nOPTION 3 - Contact Supabase Support:")
    print("  Ask about IPv6 connectivity issues from Vercel")
    print("  Request IPv4-only connection options")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_connection_solutions()