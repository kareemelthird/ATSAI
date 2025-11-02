#!/usr/bin/env python3
"""
Test script for the improved PDF upload functionality.
Tests both valid PDF files and edge cases to verify error handling.
"""
import requests
import json
import os

def test_pdf_upload():
    """Test the improved PDF upload functionality"""
    base_url = "https://atsai-jade.vercel.app"
    
    # First, get authentication token
    login_data = {
        "email": "admin@ats.com",
        "password": "admin123"
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Test 1: Check if we have any existing PDF files
    print("\n📁 Checking existing PDF files...")
    pdf_files = []
    uploads_dir = "uploads/resumes"
    if os.path.exists(uploads_dir):
        pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
        print(f"Found {len(pdf_files)} existing PDF files")
    
    # Test 2: Try to upload an existing valid PDF file (if any)
    if pdf_files:
        test_file = os.path.join(uploads_dir, pdf_files[0])
        print(f"\n📄 Testing upload with existing file: {pdf_files[0]}")
        
        with open(test_file, 'rb') as f:
            files = {"file": (pdf_files[0], f, "application/pdf")}
            upload_response = requests.post(
                f"{base_url}/api/v1/resumes/upload",
                files=files,
                headers=headers
            )
        
        print(f"Upload status: {upload_response.status_code}")
        if upload_response.status_code == 200:
            print("✅ PDF upload successful!")
            result = upload_response.json()
            print(f"Resume ID: {result.get('id')}")
            print(f"Candidate: {result.get('candidate_name')}")
            print(f"Text preview: {result.get('text_content', '')[:100]}...")
        else:
            print(f"❌ Upload failed: {upload_response.text}")
    
    # Test 3: Test the debug endpoint with authentication
    print("\n🔍 Testing debug endpoint...")
    
    # Create a small test file
    test_content = b"%PDF-1.4\nTest content"
    files = {"file": ("test.pdf", test_content, "application/pdf")}
    
    debug_response = requests.post(
        f"{base_url}/api/v1/debug/simple-upload",
        files=files,
        headers=headers
    )
    
    print(f"Debug status: {debug_response.status_code}")
    if debug_response.status_code == 200:
        print("✅ Debug endpoint accessible")
        debug_result = debug_response.json()
        print(f"Debug steps: {len(debug_result.get('steps', []))}")
        for step in debug_result.get('steps', []):
            status = "✅" if step.get('success') else "❌"
            print(f"  {status} {step.get('step')}: {step.get('message')}")
    else:
        print(f"❌ Debug failed: {debug_response.text}")
    
    # Test 4: Check settings access (was previous issue)
    print("\n⚙️ Testing settings access...")
    settings_response = requests.get(f"{base_url}/api/v1/settings", headers=headers)
    print(f"Settings status: {settings_response.status_code}")
    if settings_response.status_code == 200:
        print("✅ Settings accessible")
        settings = settings_response.json()
        if isinstance(settings, list):
            print(f"Settings count: {len(settings)}")
        else:
            print(f"Available settings: {list(settings.keys())}")
    else:
        print(f"❌ Settings failed: {settings_response.text}")

if __name__ == "__main__":
    print("🧪 Testing Improved PDF Upload Functionality")
    print("=" * 50)
    test_pdf_upload()
    print("\n✨ Test completed!")