import requests
import json

# Test a simpler settings update
api_base = "https://atsai-jade.vercel.app/api/v1"

# Login first
login_data = {"email": "admin@ats.com", "password": "admin123"}
response = requests.post(f"{api_base}/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try updating a simple setting
    simple_setting = {"value": "Test Value"}
    
    response = requests.put(
        f"{api_base}/settings/PROJECT_NAME",
        headers=headers,
        json=simple_setting
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Also try to see what the current settings look like
    get_response = requests.get(f"{api_base}/settings/", headers=headers)
    print(f"\nGet settings status: {get_response.status_code}")
    if get_response.status_code == 200:
        settings = get_response.json()
        project_name = next((s for s in settings if s["key"] == "PROJECT_NAME"), None)
        print(f"PROJECT_NAME setting: {project_name}")
else:
    print(f"Login failed: {response.status_code}")