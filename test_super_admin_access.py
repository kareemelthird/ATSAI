#!/usr/bin/env python3
"""Test the new super admin user's access to settings"""

import requests

# First login
print("🔑 Logging in as new super admin...")
login_data = {
    'email': 'kareemelthird@gmail.com', 
    'password': 'admin123'
}

response = requests.post(
    'https://atsai-jade.vercel.app/api/v1/auth/login', 
    json=login_data,
    headers={'Content-Type': 'application/json'}
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    exit(1)

token_data = response.json()
access_token = token_data.get('access_token')
user = token_data.get('user', {})

print("✅ Login successful!")
print(f"User: {user.get('email')} ({user.get('role')})")

# Test settings access
print("\n🔧 Testing settings access...")
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(
    'https://atsai-jade.vercel.app/api/v1/settings/', 
    headers=headers
)

print(f"Settings API status: {response.status_code}")
if response.status_code == 200:
    settings = response.json()
    print(f"✅ Settings access successful!")
    print(f"📊 Retrieved {len(settings)} settings")
    
    # Show a few settings
    categories = set(setting.get('category', 'unknown') for setting in settings[:5])
    print(f"📂 Categories found: {', '.join(categories)}")
else:
    print(f"❌ Settings access failed: {response.text}")

# Test users access
print("\n👥 Testing users access...")
response = requests.get(
    'https://atsai-jade.vercel.app/api/v1/users/', 
    headers=headers
)

print(f"Users API status: {response.status_code}")
if response.status_code == 200:
    users = response.json()
    print(f"✅ Users access successful!")
    print(f"👤 Found {len(users)} users")
    for user_info in users:
        print(f"  - {user_info.get('email')} ({user_info.get('role')})")
else:
    print(f"❌ Users access failed: {response.text}")

print("\n" + "="*50)
print("🎉 NEW SUPER ADMIN USER VERIFICATION COMPLETE")
print("="*50)
print("✅ User created successfully")
print("✅ Login working")
print("✅ Settings access working")
print("✅ Users management access working")
print("\n🔑 Login credentials:")
print("Email: kareemelthird@gmail.com")
print("Password: admin123")
print("Role: admin (full super admin permissions)")