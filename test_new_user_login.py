#!/usr/bin/env python3
"""Test the newly created user login"""

import requests

login_data = {
    'email': 'kareemelthird@gmail.com', 
    'password': 'admin123'
}

response = requests.post(
    'https://atsai-jade.vercel.app/api/v1/auth/login', 
    json=login_data,
    headers={'Content-Type': 'application/json'}
)

print(f'Login status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'✅ Login successful!')
    print(f'User: {data.get("user", {}).get("email")}')
    print(f'Role: {data.get("user", {}).get("role")}')
    print(f'Name: {data.get("user", {}).get("first_name")} {data.get("user", {}).get("last_name")}')
    print(f'Username: {data.get("user", {}).get("username")}')
    print(f'Token received: {"✅ YES" if data.get("access_token") else "❌ NO"}')
else:
    print(f'❌ Login failed: {response.text}')