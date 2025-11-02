#!/usr/bin/env python3
"""
Test PDF upload after datetime fix
"""
import requests
import json

def test_fixed_upload():
    base_url = "https://atsai-jade.vercel.app"
    
    print("🧪 Testing PDF Upload After DateTime Fix")
    print("=" * 50)
    
    # Login
    print("🔐 Logging in...")
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    print("✅ Login successful")
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple test PDF
    test_pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj  
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 55>>stream
BT
/F1 12 Tf
100 700 Td
(Test CV - Jane Smith) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000010 00000 n
0000000060 00000 n
0000000120 00000 n
0000000207 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
306
%%EOF"""
    
    print("📄 Testing PDF upload...")
    files = {"file": ("Jane_Smith_CV.pdf", test_pdf, "application/pdf")}
    
    upload_response = requests.post(
        f"{base_url}/api/v1/resumes/upload",
        files=files,
        headers=headers,
        timeout=60  # Allow more time for processing
    )
    
    print(f"Upload Status: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        result = upload_response.json()
        print("🎉 SUCCESS! PDF Upload Fixed!")
        print(f"   Resume ID: {result.get('id')}")
        print(f"   Candidate ID: {result.get('candidate_id')}")
        print(f"   File Path: {result.get('file_path')}")
        print(f"   File Size: {result.get('file_size_bytes')} bytes")
        print(f"   Parse Status: {result.get('parse_status')}")
        if result.get('extracted_text'):
            print(f"   Extracted Text: {result.get('extracted_text')[:100]}...")
    else:
        print("❌ Upload still failing")
        print(f"Response: {upload_response.text}")
        
        try:
            error_data = upload_response.json()
            print(f"Error Details: {error_data}")
        except:
            pass

if __name__ == "__main__":
    test_fixed_upload()