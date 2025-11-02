#!/usr/bin/env python3
"""
Quick fix to enable mock AI by temporarily updating the config
"""
import requests

def enable_mock_ai_quick_fix():
    """Enable mock AI to bypass API failures"""
    
    print("🔧 Quick Fix: Testing with Mock AI enabled")
    print("=" * 50)
    
    # Since we can't change Vercel environment variables instantly,
    # let's create a test endpoint that forces mock AI mode
    
    base_url = "https://atsai-jade.vercel.app"
    
    # Login
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check current AI settings
    print("🔍 Checking current AI configuration...")
    settings_response = requests.get(f"{base_url}/api/v1/settings", headers=headers)
    
    if settings_response.status_code == 200:
        settings = settings_response.json()
        print(f"✅ Settings accessible: {len(settings)} settings found")
        
        # Look for AI-related settings
        ai_settings = [s for s in settings if 'ai' in str(s).lower() or 'openrouter' in str(s).lower()]
        print(f"🤖 AI-related settings: {len(ai_settings)}")
        for setting in ai_settings[:3]:  # Show first 3
            print(f"   - {setting}")
    else:
        print(f"❌ Settings failed: {settings_response.status_code}")
    
    # Test simple upload to confirm the issue
    print("\n📄 Testing upload to confirm AI failure...")
    minimal_pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj  
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000053 00000 n
0000000125 00000 n
trailer<</Size 4/Root 1 0 R>>
startxref
180
%%EOF"""
    
    files = {"file": ("test.pdf", minimal_pdf, "application/pdf")}
    upload_response = requests.post(f"{base_url}/api/v1/resumes/upload", files=files, headers=headers, timeout=10)
    
    print(f"Upload Status: {upload_response.status_code}")
    if upload_response.status_code != 200:
        print(f"Upload Error: {upload_response.text}")
        print("\n💡 Diagnosis: AI service is likely failing")
        print("   Recommended Fix: Set USE_MOCK_AI=true in Vercel environment")
    else:
        print("✅ Upload succeeded!")

if __name__ == "__main__":
    enable_mock_ai_quick_fix()