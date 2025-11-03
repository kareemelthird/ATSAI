import requests
import json

# Test login with proper form data format
api_base = "https://atsai-jade.vercel.app/api/v1"

# Test the login endpoint
login_data = {
    "username": "admin@ats.com",
    "password": "admin123"
}

print("Testing login...")
response = requests.post(
    f"{api_base}/auth/login",
    data=login_data,  # Using form data
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

print(f"Login status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code != 200:
    # Try with JSON format
    print("\nTrying with JSON format...")
    response2 = requests.post(
        f"{api_base}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"JSON Login status: {response2.status_code}")
    print(f"JSON Response: {response2.text}")