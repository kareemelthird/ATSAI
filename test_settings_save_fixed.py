import requests
import json

# Test the fixed settings save functionality
api_base = "https://atsai-jade.vercel.app/api/v1"

# Login to get token
login_response = requests.post(f"{api_base}/auth/login", 
    data={
        "username": "admin@ats.com",
        "password": "admin123"
    }
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Test saving a setting with the correct format
    test_setting = {
        "value": "groq",
        "is_active": True
    }
    
    response = requests.put(
        f"{api_base}/settings/AI_PROVIDER",
        headers=headers,
        json=test_setting
    )
    
    print(f"Settings save status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Settings save successful!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Settings save failed: {response.text}")
        
    # Verify the setting was saved
    get_response = requests.get(f"{api_base}/settings/", headers=headers)
    if get_response.status_code == 200:
        settings = get_response.json()
        ai_provider = next((s for s in settings if s["key"] == "AI_PROVIDER"), None)
        if ai_provider:
            print(f"Current AI_PROVIDER value: {ai_provider['value']}")
        else:
            print("AI_PROVIDER setting not found")
else:
    print(f"❌ Login failed: {login_response.status_code}")