#!/usr/bin/env python3
"""
Simple PDF upload test to get detailed error information
"""
import requests
import json

def test_simple_upload():
    base_url = "https://atsai-jade.vercel.app"
    
    # Login
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a minimal valid PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
0000000301 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
395
%%EOF"""
    
    # Test debug endpoint first
    print("Testing debug endpoint...")
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    debug_response = requests.post(f"{base_url}/api/v1/debug/simple-upload", files=files, headers=headers)
    
    print(f"Debug Status: {debug_response.status_code}")
    if debug_response.status_code == 200:
        result = debug_response.json()
        print(f"Debug Result: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        if result.get('details'):
            details = result['details']
            print(f"Details:")
            print(f"  - File: {details.get('filename')}")
            print(f"  - Size: {details.get('size')} bytes")
            print(f"  - PDF Text Length: {details.get('pdf_text_length')}")
            if details.get('pdf_preview'):
                print(f"  - PDF Preview: {details.get('pdf_preview')[:100]}...")
        if result.get('traceback'):
            print(f"Traceback: {result['traceback']}")
    else:
        print(f"Debug Error: {debug_response.text}")
    
    # Test main upload endpoint
    print("\nTesting main upload endpoint...")
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    upload_response = requests.post(f"{base_url}/api/v1/resumes/upload", files=files, headers=headers)
    
    print(f"Upload Status: {upload_response.status_code}")
    if upload_response.status_code == 200:
        result = upload_response.json()
        print(f"Success: Resume ID {result.get('id')}")
    else:
        print(f"Upload Error: {upload_response.text}")

if __name__ == "__main__":
    test_simple_upload()