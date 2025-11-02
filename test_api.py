#!/usr/bin/env python3
"""
Simple test script to verify the AI chat API is working
"""
import requests
import json

def test_ai_chat():
    url = "http://localhost:8000/api/v1/ai/chat"
    headers = {"Content-Type": "application/json"}
    data = {"query": "hi"}
    
    try:
        print("🧪 Testing AI Chat API...")
        print(f"URL: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📝 Response Content:")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("response"):
                print(f"\n✅ AI Response: {result['response']}")
                print("🎉 API is working correctly!")
            else:
                print("\n⚠️ API responded but no AI response found")
        else:
            print(f"❌ API Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server on port 8000")
        print("Make sure the backend is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_chat()