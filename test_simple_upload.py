"""
Test Simple Upload Endpoint
"""
import requests
import io

def test_simple_upload():
    """Test the simple upload debug endpoint"""
    base_url = 'https://atsai-jade.vercel.app'
    
    print("🔍 Testing Simple Upload Debug Endpoint...")
    print("=" * 40)
    
    # Login first
    login_data = {'email': 'admin@ats.com', 'password': 'admin123'}
    login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        
        print(f"✅ Login successful")
        
        # Create test content
        test_content = b"""Sample Resume Content
        
John Doe
Software Engineer
Email: john.doe@example.com
Phone: (555) 123-4567

EXPERIENCE:
- Software Developer at TechCorp (2020-2024)
- Worked on web applications using Python and React

EDUCATION:
- Bachelor of Computer Science

SKILLS:
- Python, JavaScript, React, FastAPI"""
        
        files = {
            'file': ('test_resume.pdf', io.BytesIO(test_content), 'application/pdf')
        }
        
        print(f"\n🔄 Testing simple upload endpoint...")
        
        try:
            response = requests.post(
                f'{base_url}/api/v1/debug/simple-upload',
                files=files,
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                
                if 'details' in result:
                    details = result['details']
                    print(f"   File size: {details.get('size')} bytes")
                    print(f"   Upload dir: {details.get('upload_dir')}")
                    if details.get('pdf_text_length'):
                        print(f"   PDF text length: {details.get('pdf_text_length')} chars")
                        print(f"   PDF preview: {details.get('pdf_preview', '')[:100]}...")
            else:
                result = response.json()
                print(f"   ❌ Failed")
                print(f"   Response: {result}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    test_simple_upload()