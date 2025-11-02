#!/usr/bin/env python3
"""
Test upload with detailed error tracking to isolate the 500 error
"""
import requests
import traceback

def test_upload_with_error_isolation():
    base_url = "https://atsai-jade.vercel.app"
    
    # Login first
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com", 
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with a very minimal PDF that should be easily parsable
    minimal_pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj  
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT
/F1 12 Tf
100 700 Td
(John Doe CV) Tj
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
295
%%EOF"""
    
    print("🧪 Testing minimal PDF upload...")
    
    # Try the upload
    files = {"file": ("John_Doe_CV.pdf", minimal_pdf, "application/pdf")}
    
    try:
        upload_response = requests.post(
            f"{base_url}/api/v1/resumes/upload",
            files=files,
            headers=headers,
            timeout=30  # Give it time
        )
        
        print(f"Upload Status: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print(f"✅ Success! Resume ID: {result.get('id')}")
            print(f"   Candidate ID: {result.get('candidate_id')}")
            print(f"   File Path: {result.get('file_path')}")
        else:
            print(f"❌ Upload Failed")
            print(f"Response Headers: {dict(upload_response.headers)}")
            print(f"Response Text: {upload_response.text}")
            
            # Try to get more info if it's JSON
            try:
                error_json = upload_response.json()
                print(f"Error JSON: {error_json}")
            except:
                pass
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out - likely a processing issue on the server")
    except Exception as e:
        print(f"❌ Request failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_upload_with_error_isolation()