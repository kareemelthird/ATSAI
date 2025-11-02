#!/usr/bin/env python3
"""
Add AI instruction settings via API
"""
import requests

def add_ai_instructions():
    base_url = "https://atsai-jade.vercel.app"
    
    print("🤖 Adding AI Instruction Settings")
    print("=" * 40)
    
    # Login
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json={
        "email": "admin@ats.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # AI Instructions to add
    ai_instructions = {
        "AI_INSTRUCTIONS_ARABIC": {
            "value": '''أنت مساعد ذكي ودود متخصص في الموارد البشرية. اسمك "مساعد ATS الذكي".

هدفك مساعدة المسؤولين عن التوظيف بطريقة طبيعية وودودة.

تعليمات المحادثة:
- أجب بطريقة طبيعية ودودة كما لو كنت تتحدث مع صديق مهني
- إذا سُئلت عن وظيفتك، أجب: "أنا مساعد ذكي متخصص في الموارد البشرية أساعدك في العثور على أفضل المرشحين وتحليل ملفاتهم الشخصية"
- إذا لم تكن هناك وظائف محددة، اطلب توضيحاً بلطف عن نوع الوظيفة المطلوبة
- استخدم الأسماء والمعلومات الدقيقة من قاعدة البيانات فقط
- لا تخترع معلومات غير موجودة
- إذا لم تجد مرشحين مناسبين، اعتذر بلطف واطلب توضيح المتطلبات
- كن مختصراً ومفيداً في نفس الوقت''',
            "label": "AI Instructions (Arabic)",
            "description": "Arabic language instructions for AI assistant behavior"
        },
        "AI_INSTRUCTIONS_ENGLISH": {
            "value": '''You are a friendly, intelligent HR assistant. Your name is "ATS Smart Assistant".

Your goal is to help recruiters in a natural, friendly way.

Conversation Guidelines:
- Respond naturally and friendly as if talking to a professional colleague
- If asked about your role, say: "I'm an AI HR assistant helping you find the best candidates and analyze their profiles"
- If no specific jobs are mentioned, politely ask for clarification about the desired position
- Only use exact names and information from the database
- Never invent information that doesn't exist
- If no suitable candidates are found, politely apologize and ask for clarification of requirements
- Be concise but helpful''',
            "label": "AI Instructions (English)",
            "description": "English language instructions for AI assistant behavior"
        },
        "AI_RESUME_ANALYSIS_INSTRUCTIONS": {
            "value": '''You are an expert HR assistant that analyzes resumes.

Extract information accurately and comprehensively:
- Personal details (name, email, phone, location, links)
- Professional summary highlighting key achievements
- Calculate years of experience from work history
- Skills categorized by type (technical, soft, domain)
- Work experience with roles, companies, dates
- Education with degrees, institutions, dates
- Certifications with names, issuers, dates
- Projects with descriptions and technologies
- Languages with proficiency levels

Return structured JSON data only.''',
            "label": "Resume Analysis Instructions", 
            "description": "Instructions for AI resume analysis and data extraction"
        }
    }
    
    # Add each setting
    for key, setting_data in ai_instructions.items():
        print(f"\n📝 Adding {setting_data['label']}...")
        
        # Try to update existing setting
        update_response = requests.put(
            f"{base_url}/api/v1/settings/{key}",
            json={"value": setting_data["value"]},
            headers=headers
        )
        
        if update_response.status_code == 200:
            print(f"✅ Updated {setting_data['label']}")
        else:
            print(f"⚠️ Update failed for {key}: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
    
    print("\n🔍 Checking final settings...")
    settings_response = requests.get(f"{base_url}/api/v1/settings", headers=headers)
    if settings_response.status_code == 200:
        settings = settings_response.json()
        instruction_settings = [s for s in settings if 'instruction' in s.get('key', '').lower()]
        print(f"✅ AI Instruction settings found: {len(instruction_settings)}")
        for setting in instruction_settings:
            print(f"   - {setting.get('key')}: {setting.get('label')}")
    
if __name__ == "__main__":
    add_ai_instructions()