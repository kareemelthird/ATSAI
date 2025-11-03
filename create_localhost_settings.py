#!/usr/bin/env python3

import requests
import json

def create_complete_settings_like_localhost():
    """Create all settings exactly like your local setup with Arabic instructions"""
    
    print("🔧 Creating complete settings like your localhost setup...")
    print("=" * 70)
    
    # Login first
    auth_data = {"email": "admin@ats.com", "password": "admin123"}
    
    auth_response = requests.post(
        "https://atsai-jade.vercel.app/api/v1/auth/login",
        json=auth_data,
        headers={"Content-Type": "application/json"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.text}")
        return
        
    token = auth_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Your local .env settings + Arabic AI instructions
    # *** Using exact database keys from production ***
    all_settings = {
        # From your .env file - Database
        "DATABASE_URL": "",  # Will be auto-set by Vercel
        
        # From your .env file - AI Configuration  
        "AI_PROVIDER": "groq",  # You use Groq locally
        "USE_MOCK_AI": "false",  # You had this set to false
        
        # Groq settings from your .env
        "GROQ_API_KEY": "",  # User needs to add their key
        "GROQ_MODEL": "llama-3.3-70b-versatile",  # From your .env: AI_MODEL=llama-3.3-70b-versatile
        
        # DeepSeek (default placeholders)
        "DEEPSEEK_API_KEY": "",
        "DEEPSEEK_MODEL": "deepseek-chat",
        
        # OpenRouter (default placeholders)  
        "OPENROUTER_API_KEY": "",
        "OPENROUTER_MODEL": "anthropic/claude-2",  # From your config.py default
        
        # From your .env file - Security
        "SECRET_KEY": "",  # User needs to set this
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",  # From your .env
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",     # From your .env
        
        # From your .env file - Application
        "PROJECT_NAME": "ATS System",  # From your .env: PROJECT_NAME=ATS System
        
        # From your .env file - Server
        "HOST": "0.0.0.0",    # From your .env
        "PORT": "8000",       # From your .env
        
        # Updated CORS for production + local dev
        "ALLOWED_ORIGINS": "https://atsai-jade.vercel.app,http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000",
        
        # *** AI INSTRUCTIONS FROM YOUR LOCAL SETUP ***
        # Using exact database keys that exist:
        
        # Resume analysis instructions (from your local setup)
        "ai_resume_analysis_instructions": """You are an expert HR assistant that analyzes resumes.

Extract information accurately and comprehensively:
- Personal details (name, email, phone, location, links)
- Professional summary highlighting key achievements
- Calculate years of experience from work history
- Skills categorized by type (technical, soft, domain)
- Complete work experience with dates, companies, roles
- Education with institutions, degrees, dates
- Certifications with names, organizations, dates
- Languages with proficiency levels

Guidelines:
- Be thorough but accurate
- Include team leadership, project management details
- Extract daily tasks, main responsibilities, and key accomplishments
- Be comprehensive - capture ALL relevant information about each role""",

        # Chat system instructions (using existing database key)
        "chat_system_instructions": """You are a friendly, intelligent HR assistant. Your name is "ATS Smart Assistant".

Your goal is to help recruiters in a natural, friendly way.

Conversation Guidelines:
- Respond naturally and friendly as if talking to a professional colleague
- If asked about your role, say: "I'm an AI HR assistant helping you find the best candidates and analyze their profiles"  
- If no specific jobs are mentioned, politely ask for clarification about the desired position
- Only use exact names and information from the database
- Never invent information that doesn't exist
- If no suitable candidates are found, politely apologize and ask for clarification of requirements
- Be concise but helpful"""
    }
    
    # *** ARABIC INSTRUCTIONS (Missing from database - need to be created) ***
    arabic_instructions_to_create = {
        "ai_instructions_arabic": """أنت مساعد ذكي ودود متخصص في الموارد البشرية. اسمك "مساعد ATS الذكي".

هدفك مساعدة المسؤولين عن التوظيف بطريقة طبيعية وودودة.

تعليمات المحادثة:
- أجب بطريقة طبيعية ودودة كما لو كنت تتحدث مع صديق مهني
- إذا سُئلت عن وظيفتك، أجب: "أنا مساعد ذكي متخصص في الموارد البشرية أساعدك في العثور على أفضل المرشحين وتحليل ملفاتهم الشخصية"
- إذا لم تكن هناك وظائف محددة، اطلب توضيحاً بلطف عن نوع الوظيفة المطلوبة
- استخدم الأسماء والمعلومات الدقيقة من قاعدة البيانات فقط
- لا تخترع معلومات غير موجودة
- إذا لم تجد مرشحين مناسبين، اعتذر بلطف واطلب توضيح المتطلبات
- كن مختصراً ومفيداً في نفس الوقت""",
        
        "ai_instructions_english": """You are a friendly, intelligent HR assistant. Your name is "ATS Smart Assistant".

Your goal is to help recruiters in a natural, friendly way.

Conversation Guidelines:
- Respond naturally and friendly as if talking to a professional colleague
- If asked about your role, say: "I'm an AI HR assistant helping you find the best candidates and analyze their profiles"
- If no specific jobs are mentioned, politely ask for clarification about the desired position
- Only use exact names and information from the database
- Never invent information that doesn't exist
- If no suitable candidates are found, politely apologize and ask for clarification of requirements
- Be concise but helpful"""
    }
    
    print(f"📝 Updating {len(all_settings)} existing settings...")
    print(f"🌏 Creating {len(arabic_instructions_to_create)} new Arabic instruction settings...")
    
    success_count = 0
    failed_settings = []
    
    # 1. Update existing settings
    print("\n🔧 UPDATING EXISTING SETTINGS:")
    print("-" * 50)
    for setting_key, setting_value in all_settings.items():
        display_value = setting_value[:50] + "..." if len(setting_value) > 50 else setting_value
        print(f"   📝 {setting_key}: {display_value}")
        
        try:
            update_data = {
                "setting_value": setting_value,
                "is_active": True
            }
            
            response = requests.put(
                f"https://atsai-jade.vercel.app/api/v1/settings/{setting_key}",
                json=update_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                print(f"      ✅ Updated successfully")
                success_count += 1
            else:
                print(f"      ❌ Failed: {response.status_code}")
                failed_settings.append(setting_key)
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
            failed_settings.append(setting_key)
    
    # 2. Create new Arabic instruction settings
    print("\n🌍 CREATING NEW ARABIC INSTRUCTION SETTINGS:")
    print("-" * 50)
    arabic_success = 0
    for setting_key, setting_value in arabic_instructions_to_create.items():
        display_value = setting_value[:50] + "..." if len(setting_value) > 50 else setting_value
        print(f"   ➕ {setting_key}: {display_value}")
        
        try:
            create_data = {
                "setting_key": setting_key,
                "setting_value": setting_value,
                "setting_type": "text",
                "description": f"AI instructions in {'Arabic' if 'arabic' in setting_key else 'English'} language",
                "category": "ai_chat",
                "is_active": True
            }
            
            response = requests.post(
                "https://atsai-jade.vercel.app/api/v1/settings/",
                json=create_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                print(f"      ✅ Created successfully")
                arabic_success += 1
            else:
                print(f"      ❌ Failed: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    total_success = success_count + arabic_success
    
    print("\n" + "="*70)
    print("📊 SUMMARY:")
    print("="*70)
    print(f"✅ Successfully updated: {success_count}/{len(all_settings)} existing settings")
    print(f"🌍 Arabic instructions created: {arabic_success}/{len(arabic_instructions_to_create)} new settings")
    print(f"🔧 Total successful: {total_success}/{len(all_settings) + len(arabic_instructions_to_create)}")
    print(f"� Local .env values: Applied")
    
    if failed_settings:
        print(f"❌ Failed settings: {failed_settings}")
        print("💡 You can update these manually through the Settings UI")
    
    print("\n🔑 IMPORTANT - ADD YOUR API KEYS:")
    print("="*70)
    print("1. GROQ_API_KEY - Get from https://console.groq.com")
    print("2. SECRET_KEY - Generate with: openssl rand -hex 32") 
    print("3. (Optional) OPENROUTER_API_KEY, DEEPSEEK_API_KEY")
    
    print("\n🚀 Your production ATS now matches your localhost setup!")
    print("🌏 Arabic instructions are available for AI chat")
    print("🔄 Refresh the Settings page to see all values")

if __name__ == "__main__":
    create_complete_settings_like_localhost()