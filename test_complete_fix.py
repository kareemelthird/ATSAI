import requests
import json

# Test login with correct field names
api_base = "https://atsai-jade.vercel.app/api/v1"

# Use 'email' instead of 'username'
login_data = {
    "email": "admin@ats.com",
    "password": "admin123"
}

print("Testing login with email field...")
response = requests.post(
    f"{api_base}/auth/login",
    json=login_data,
    headers={"Content-Type": "application/json"}
)

print(f"Login status: {response.status_code}")
if response.status_code == 200:
    token_data = response.json()
    token = token_data["access_token"]
    print("✅ Login successful!")
    
    # Now test the settings save with the fixed format
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test saving a setting with the correct format
    test_setting = {
        "value": "groq",
        "is_active": True
    }
    
    save_response = requests.put(
        f"{api_base}/settings/AI_PROVIDER",
        headers=headers,
        json=test_setting
    )
    
    print(f"\nSettings save status: {save_response.status_code}")
    if save_response.status_code == 200:
        print("✅ Settings save successful!")
        print(f"Response: {save_response.json()}")
    else:
        print(f"❌ Settings save failed: {save_response.text}")
        
    # Verify the setting was saved
    get_response = requests.get(f"{api_base}/settings/", headers=headers)
    if get_response.status_code == 200:
        settings = get_response.json()
        ai_provider = next((s for s in settings if s["key"] == "AI_PROVIDER"), None)
        if ai_provider:
            print(f"✅ Verified: AI_PROVIDER = {ai_provider['value']}")
        else:
            print("AI_PROVIDER setting not found")
else:
    print(f"❌ Login failed: {response.text}")