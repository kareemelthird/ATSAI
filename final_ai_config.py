import requests

# Final update for GROQ_MODEL
api_base = "https://atsai-jade.vercel.app/api/v1"

# Login
login_data = {"email": "admin@ats.com", "password": "admin123"}
response = requests.post(f"{api_base}/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update GROQ_MODEL
    setting_data = {"value": "llama-3.3-70b-versatile"}
    response = requests.put(
        f"{api_base}/settings/GROQ_MODEL",
        headers=headers,
        json=setting_data
    )
    
    if response.status_code == 200:
        print("✅ GROQ_MODEL updated successfully")
    else:
        print(f"❌ GROQ_MODEL failed: {response.status_code}")
    
    # Final verification - show all AI settings
    get_response = requests.get(f"{api_base}/settings/", headers=headers)
    if get_response.status_code == 200:
        settings = get_response.json()
        print("\n🎯 Final AI Configuration:")
        ai_settings = [s for s in settings if "ai" in s['key'].lower() or "groq" in s['key'].lower()]
        for setting in ai_settings:
            value = setting['value']
            if setting['is_encrypted'] and value:
                value = "***ENCRYPTED***"
            elif len(value) > 50:
                value = value[:50] + "..."
            print(f"  ✓ {setting['label']}: {value}")
else:
    print(f"❌ Login failed: {response.status_code}")