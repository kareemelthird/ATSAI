#!/usr/bin/env python3

import requests
import json

def test_correct_endpoint():
    """Test the endpoint that actually worked in our earlier debug"""
    
    print("🔧 Testing the correct working endpoint...")
    print("-" * 60)
    
    # Test authentication
    auth_data = {"email": "admin@ats.com", "password": "admin123"}
    
    auth_response = requests.post(
        "https://atsai-jade.vercel.app/api/v1/auth/login",
        json=auth_data,
        headers={"Content-Type": "application/json"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.text}")
        return
        
    token = auth_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test the endpoint that returned 18 settings in our earlier test
    print(f"\n🔧 Testing /api/v1/settings/ (the working one)...")
    try:
        response = requests.get("https://atsai-jade.vercel.app/api/v1/settings/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Type: {type(data)}")
            if isinstance(data, list):
                print(f"   Count: {len(data)}")
                if len(data) > 0:
                    print(f"   First item: {data[0]}")
                    
        else:
            print(f"   Error: {response.text[:100]}")
            
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_correct_endpoint()