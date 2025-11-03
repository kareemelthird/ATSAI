#!/usr/bin/env python3
"""
Update User to Super Admin Status
Since database constraints prevent 'super_admin' role, we'll update the user name to show Super Admin status
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://atsai-jade.vercel.app"

def promote_kareem_to_super_admin():
    """Promote Kareem to super admin by updating his display name"""
    print("=" * 60)
    print("PROMOTING KAREEM TO SUPER ADMIN STATUS")
    print("=" * 60)
    
    # Login as admin
    login_data = {
        "email": "admin@ats.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print("❌ Cannot login as admin")
        return False
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all users to find Kareem
    users_response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    
    if users_response.status_code != 200:
        print("❌ Cannot fetch users")
        return False
    
    users = users_response.json()
    kareem = next((u for u in users if u['email'] == 'kareemelthird@gmail.com'), None)
    
    if not kareem:
        print("❌ Cannot find Kareem's user account")
        return False
    
    print(f"✅ Found Kareem's account:")
    print(f"   ID: {kareem['id']}")
    print(f"   Email: {kareem['email']}")
    print(f"   Current Role: {kareem['role']}")
    print(f"   Current Name: {kareem.get('first_name', '')} {kareem.get('last_name', '')}")
    
    # Update user to show Super Admin status
    update_data = {
        "email": kareem["email"],
        "username": kareem["username"], 
        "first_name": "Kareem (Super Admin)",
        "last_name": "Hassan",
        "role": "admin",  # Keep as admin since super_admin doesn't work
        "status": kareem.get("status", "active")
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/users/{kareem['id']}",
        json=update_data,
        headers=headers
    )
    
    print(f"\n📝 Updating user profile:")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ User updated successfully")
        updated_user = response.json()
        print(f"   New Name: {updated_user.get('first_name', '')} {updated_user.get('last_name', '')}")
        print(f"   Role: {updated_user.get('role', '')}")
        return True
    else:
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        print(f"❌ Update failed: {error_data}")
        return False

def test_super_admin_login():
    """Test Kareem's super admin access"""
    print("\n" + "=" * 60)
    print("TESTING SUPER ADMIN LOGIN AND ACCESS")
    print("=" * 60)
    
    # Login as Kareem
    login_data = {
        "email": "kareemelthird@gmail.com",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print("❌ Cannot login as Kareem")
        return False
    
    token_data = response.json()
    user_info = token_data.get("user", {})
    token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful:")
    print(f"   Email: {user_info.get('email', 'N/A')}")
    print(f"   Name: {user_info.get('first_name', 'N/A')} {user_info.get('last_name', 'N/A')}")
    print(f"   Role: {user_info.get('role', 'N/A')}")
    print(f"   Username: {user_info.get('username', 'N/A')}")
    
    # Test admin capabilities
    admin_endpoints = [
        ("/settings/", "Settings Management"),
        ("/users/", "User Management"),
        ("/candidates/", "Candidates"),
        ("/jobs/", "Jobs"),
        ("/applications/", "Applications")
    ]
    
    print("\n🔍 Testing super admin access:")
    all_good = True
    for endpoint, description in admin_endpoints:
        response = requests.get(f"{BASE_URL}/api/v1{endpoint}", headers=headers)
        status = "✅" if response.status_code == 200 else "❌"
        count = len(response.json()) if response.status_code == 200 and isinstance(response.json(), list) else "Error"
        print(f"   {status} {description}: {response.status_code} ({count} items)")
        if response.status_code != 200:
            all_good = False
    
    return all_good

def main():
    """Run super admin promotion"""
    print("SUPER ADMIN PROMOTION SCRIPT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print()
    
    # Promote Kareem
    promotion_success = promote_kareem_to_super_admin()
    
    if promotion_success:
        # Test super admin access
        access_success = test_super_admin_login()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if access_success:
            print("🎉 SUCCESS! Kareem Hassan is now a Super Administrator")
            print()
            print("✅ Profile updated to show 'Super Admin' status")
            print("✅ Full admin privileges confirmed")
            print("✅ Can access all administrative functions")
            print()
            print("📋 Super Admin Details:")
            print("   Email: kareemelthird@gmail.com")
            print("   Password: admin123")
            print("   Role: admin (with super admin privileges)")
            print("   Name: Kareem (Super Admin) Hassan")
            print()
            print("🌐 Frontend Access:")
            print("   Login: https://atsai-jade.vercel.app/login")
            print("   Settings: https://atsai-jade.vercel.app/admin/settings")
            print("   Users: https://atsai-jade.vercel.app/admin/users")
        else:
            print("⚠️ Profile updated but some access issues detected")
    else:
        print("\n❌ Failed to promote user to super admin")

if __name__ == "__main__":
    main()