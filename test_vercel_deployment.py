#!/usr/bin/env python3
"""
Quick test script to verify Vercel deployment environment variables
and backend functionality.
"""

import os
import sys
import requests
from urllib.parse import urlparse

def test_vercel_deployment():
    """Test the Vercel deployment health and configuration."""
    
    # Test URL - replace with your actual Vercel URL
    base_url = "https://atsai-jade.vercel.app"
    
    print("🚀 Testing Vercel Deployment")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: Frontend accessibility
    print("📱 Testing Frontend...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
    
    print()
    
    # Test 2: Backend API health endpoint
    print("🔧 Testing Backend API...")
    health_url = f"{base_url}/api/v1/health"
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API is accessible")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'no message')}")
            print(f"   Database: {data.get('database_status', 'unknown')}")
        else:
            print(f"❌ Backend API returned status: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Backend API connection failed: {e}")
    
    print()
    
    # Test 3: Backend API docs
    print("📚 Testing API Documentation...")
    docs_url = f"{base_url}/api/docs"
    try:
        response = requests.get(docs_url, timeout=10)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
        else:
            print(f"❌ API docs returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs connection failed: {e}")
    
    print()
    
    # Test 4: Login endpoint
    print("🔐 Testing Login Endpoint...")
    login_url = f"{base_url}/api/v1/auth/login"
    test_credentials = {
        "email": "admin@ats.local",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            login_url,
            json=test_credentials,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Login endpoint works - credentials accepted")
        elif response.status_code == 401:
            print("⚠️  Login endpoint works - credentials rejected (database not initialized?)")
        elif response.status_code == 422:
            print("⚠️  Login endpoint works - validation error (check request format)")
        else:
            print(f"❌ Login endpoint returned status: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Login endpoint connection failed: {e}")
    
    print()
    print("🎯 Next Steps:")
    print("1. Ensure environment variables are set in Vercel dashboard")
    print("2. Run database schema in Supabase SQL Editor")
    print("3. Create admin user in database")
    print("4. Test login with admin@ats.local / admin123")

if __name__ == "__main__":
    test_vercel_deployment()