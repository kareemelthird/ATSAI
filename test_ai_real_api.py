import requests

# Check if USE_MOCK_AI is enabled and test real AI
api_base = "https://atsai-jade.vercel.app/api/v1"

# Login as admin
login_data = {"email": "admin@ats.com", "password": "admin123"}
response = requests.post(f"{api_base}/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check USE_MOCK_AI setting
    settings_response = requests.get(f"{api_base}/settings/", headers=headers)
    if settings_response.status_code == 200:
        settings = settings_response.json()
        mock_setting = next((s for s in settings if s['key'] == 'USE_MOCK_AI'), None)
        if mock_setting:
            print(f"🔍 USE_MOCK_AI: {mock_setting['value']}")
            
            if mock_setting['value'].lower() in ['true', '1', 'yes']:
                print("❌ ISSUE FOUND: USE_MOCK_AI is enabled - disabling it")
                
                # Disable mock AI
                update_data = {"value": "false"}
                update_response = requests.put(
                    f"{api_base}/settings/USE_MOCK_AI",
                    headers=headers,
                    json=update_data
                )
                
                if update_response.status_code == 200:
                    print("✅ USE_MOCK_AI disabled successfully")
                    
                    # Test AI chat again
                    print("\n🤖 Testing AI Chat with real API:")
                    test_data = {
                        "query_text": "ما هي وظيفتك؟",
                        "user_id": "test-user",
                        "conversation_history": []
                    }
                    
                    chat_response = requests.post(
                        f"{api_base}/ai/chat",
                        headers=headers,
                        json=test_data
                    )
                    
                    print(f"Status: {chat_response.status_code}")
                    if chat_response.status_code == 200:
                        result = chat_response.json()
                        print(f"AI Response: {result['response']}")
                    else:
                        print(f"Error: {chat_response.text}")
                else:
                    print(f"❌ Failed to disable USE_MOCK_AI: {update_response.text}")
            else:
                print("✅ USE_MOCK_AI is already disabled")
        else:
            print("❌ USE_MOCK_AI setting not found")
else:
    print(f"❌ Login failed: {response.status_code}")