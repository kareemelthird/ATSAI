#!/usr/bin/env python3
"""
Test Network Error Fix
Verify that the project-info endpoint network error is resolved
"""

import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "https://atsai-jade.vercel.app"

def wait_for_deployment():
    """Wait for Vercel deployment to complete"""
    print("Waiting for Vercel deployment to complete...")
    print("(This usually takes 1-2 minutes)")
    
    for i in range(12):  # Wait up to 2 minutes
        try:
            response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ Deployment ready after {(i+1)*10} seconds")
                return True
        except:
            pass
        
        print(f"⏳ Waiting... ({(i+1)*10}s)")
        time.sleep(10)
    
    print("⚠️ Deployment may still be in progress")
    return False

def test_project_info_endpoints():
    """Test the project info endpoints that were causing network errors"""
    print("\n" + "=" * 60)
    print("TESTING PROJECT INFO ENDPOINTS")
    print("=" * 60)
    
    endpoints = [
        "/api/v1/settings/public/project-info",
        "/api/v1/health"
    ]
    
    for endpoint in endpoints:
        print(f"\n--- Testing {endpoint} ---")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data}")
            else:
                print(f"❌ Failed: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Timeout error")
        except requests.exceptions.ConnectionError:
            print("❌ Connection error") 
        except Exception as e:
            print(f"❌ Error: {e}")

def test_frontend_accessibility():
    """Test that frontend pages are accessible"""
    print("\n" + "=" * 60)
    print("TESTING FRONTEND ACCESSIBILITY")
    print("=" * 60)
    
    pages = [
        "/",
        "/login", 
        "/admin/settings",
        "/admin/users"
    ]
    
    for page in pages:
        print(f"\n--- Testing {page} ---")
        
        try:
            response = requests.get(f"{BASE_URL}{page}", timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Page accessible")
            else:
                print(f"❌ Page error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run network error fix test"""
    print("NETWORK ERROR FIX TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print()
    
    # Wait for deployment
    deployment_ready = wait_for_deployment()
    
    if deployment_ready:
        # Test API endpoints
        test_project_info_endpoints()
        
        # Test frontend pages
        test_frontend_accessibility()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Open your browser and test the application:")
    print("   https://atsai-jade.vercel.app")
    print()
    print("2. Check browser console for any remaining network errors")
    print()
    print("3. Test the Settings page specifically:")
    print("   https://atsai-jade.vercel.app/admin/settings")
    print("   - Should load without 'Loading...' getting stuck")
    print("   - Should not show 'Failed to fetch project info' errors")
    print()
    print("4. Login with your super admin account:")
    print("   Email: kareemelthird@gmail.com")
    print("   Password: admin123")

if __name__ == "__main__":
    main()