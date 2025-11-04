import requests

# Test the improved AI chat system
api_base = "https://atsai-jade.vercel.app/api/v1"

# Login as admin
login_data = {"email": "admin@ats.com", "password": "admin123"}
response = requests.post(f"{api_base}/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful - Testing improved AI chat\n")
    
    # Test 1: Role/Function question in Arabic
    print("🧪 Test 1: Role question in Arabic")
    test_data = {
        "query_text": "ما هي وظيفتك؟",
        "user_id": "test-user",
        "conversation_history": []
    }
    
    response = requests.post(f"{api_base}/ai/chat", headers=headers, json=test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Response: {result['response'][:300]}...")
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Capabilities question in English  
    print("🧪 Test 2: Capabilities question in English")
    test_data = {
        "query_text": "How can you help me with recruitment?",
        "user_id": "test-user", 
        "conversation_history": []
    }
    
    response = requests.post(f"{api_base}/ai/chat", headers=headers, json=test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Response: {result['response'][:300]}...")
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Candidate evaluation scenario
    print("🧪 Test 3: Candidate evaluation scenario")
    test_data = {
        "query_text": "I have a job that requires bachelor's degree. Show me candidates and evaluate them.",
        "user_id": "test-user",
        "conversation_history": []
    }
    
    response = requests.post(f"{api_base}/ai/chat", headers=headers, json=test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Evaluation Response: {result['response'][:400]}...")
        if result.get('candidates'):
            print(f"📊 Candidates mentioned: {len(result['candidates'])}")
            for candidate in result['candidates']:
                print(f"   - {candidate['name']}")
    else:
        print(f"❌ Failed: {response.text}")
        
else:
    print(f"❌ Login failed: {response.status_code}")