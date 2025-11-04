"""
Test AI chat quality on production after deployment
"""
import requests
import json

def test_production_ai_chat():
    """Test AI chat on production to verify improvements"""
    print("🧪 Testing AI Chat Quality on Production")
    print("=" * 50)
    
    # Production URL (update with actual deployment URL)
    base_url = "https://atsai-jade.vercel.app"
    
    # Test queries in both languages
    test_queries = [
        ("Hello, what is your role?", "english"),
        ("ما هي وظيفتك؟", "arabic"),
        ("What jobs are available in the system?", "english"),
        ("ما الوظائف المتاحة حالياً؟", "arabic")
    ]
    
    print(f"🌐 Testing AI chat at: {base_url}")
    
    # First, try to login and get a token (this might not work without credentials)
    login_url = f"{base_url}/api/v1/auth/login"
    chat_url = f"{base_url}/api/v1/ai/chat"
    
    for query, language in test_queries:
        print(f"\n🔍 Testing: {query}")
        print(f"   Language: {language}")
        
        try:
            # Try direct chat request (might need authentication)
            response = requests.post(
                chat_url,
                json={"message": query},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', 'No response found')
                print(f"   ✅ Response: {ai_response[:100]}...")
                
                # Check for improved quality indicators
                if "recruitment" in ai_response.lower() or "hr" in ai_response.lower() or "أستقطاب" in ai_response:
                    print(f"   🎯 Quality: GOOD - Contains relevant HR/recruitment context")
                else:
                    print(f"   ⚠️  Quality: Check needed - May still have generic responses")
            
            elif response.status_code == 401:
                print(f"   🔒 Authentication required - Cannot test without login")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Login to {base_url} manually")
    print(f"2. Test AI chat functionality")
    print(f"3. Verify no more generic responses")
    print(f"4. Check if custom instructions work")

if __name__ == "__main__":
    test_production_ai_chat()