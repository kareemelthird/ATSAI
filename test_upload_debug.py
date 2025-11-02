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
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        
        print(f"✅ Login successful")
        
        # Test 1: Simple PDF content
        print(f"\n🔄 Test 1: Simple PDF Upload...")
        
        # Create a simple text file and treat it as PDF for testing
        test_content = b"""Sample Resume Content
        
John Doe
Software Engineer
Email: john.doe@example.com
Phone: (555) 123-4567

EXPERIENCE:
- Software Developer at TechCorp (2020-2024)
- Worked on web applications using Python and React
- Led team of 3 developers

EDUCATION:
- Bachelor of Computer Science
- University of Technology (2016-2020)

SKILLS:
- Python, JavaScript, React, FastAPI
- Database design and optimization
- Team leadership and project management"""
        
        files = {
            'file': ('test_resume.pdf', io.BytesIO(test_content), 'application/pdf')
        }
        
        try:
            upload_response = requests.post(
                f'{base_url}/api/v1/resumes/upload',
                files=files,
                headers=headers
            )
            
            print(f"   Upload status: {upload_response.status_code}")
            
            if upload_response.status_code == 200:
                print("   ✅ Upload successful!")
                result = upload_response.json()
                print(f"   Candidate ID: {result.get('candidate_id', 'N/A')}")
                print(f"   Resume ID: {result.get('id', 'N/A')}")
            else:
                print(f"   ❌ Upload failed")
                print(f"   Error: {upload_response.text}")
                
        except Exception as e:
            print(f"   ❌ Upload error: {e}")
        
        # Test 2: Test the debug upload endpoint (if available)
        print(f"\n🔄 Test 2: Debug Upload Endpoint...")
        
        try:
            debug_response = requests.post(
                f'{base_url}/api/v1/test-upload',
                files=files,
                headers=headers
            )
            
            print(f"   Debug upload status: {debug_response.status_code}")
            
            if debug_response.status_code == 200:
                print("   ✅ Debug upload successful!")
                print(f"   Response: {debug_response.json()}")
            else:
                print(f"   Debug response: {debug_response.text}")
                
        except Exception as e:
            print(f"   Debug upload error: {e}")
    
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    test_pdf_upload()