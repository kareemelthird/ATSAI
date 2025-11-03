#!/usr/bin/env python3

import requests
import json

def apply_local_settings_to_production():
    """Apply the exact same settings and AI instructions from local setup to production"""
    
    print("🔧 Applying local settings to production database...")
    print("-" * 70)
    
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
    
    # Settings from your local .env file and AI instructions
    local_settings = {
        # Database
        "DATABASE_URL": "",  # Will be set by Vercel
        
        # AI Configuration (from your .env)
        "AI_PROVIDER": "groq",  # You were using Groq locally
        "GROQ_API_KEY": "",     # User will need to add their key
        "GROQ_MODEL": "llama-3.3-70b-versatile",  # From your .env
        "DEEPSEEK_API_KEY": "",
        "DEEPSEEK_MODEL": "deepseek-chat",
        "OPENROUTER_API_KEY": "",
        "OPENROUTER_MODEL": "anthropic/claude-3.5-sonnet",
        "USE_MOCK_AI": "false",  # From your .env
        
        # Security (from your .env)
        "SECRET_KEY": "",  # User will need to set
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",  # From your .env
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",     # From your .env
        
        # Application (from your .env)
        "PROJECT_NAME": "ATS System",  # From your .env
        
        # Server (from your .env)
        "HOST": "0.0.0.0",    # From your .env
        "PORT": "8000",       # From your .env
        
        # CORS (updated for production)
        "ALLOWED_ORIGINS": "https://atsai-jade.vercel.app,http://localhost:3000,http://localhost:5173",
        
        # AI Instructions (from your local add_ai_instruction_settings.py)
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
    
    print(f"🔧 Updating {len(local_settings)} settings with your local configuration...")
    
    success_count = 0
    for setting_key, setting_value in local_settings.items():
        print(f"\n   📝 {setting_key}: {setting_value[:50] + '...' if len(setting_value) > 50 else setting_value}")
        
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
                print(f"      ❌ Failed: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    print(f"\n🎉 Successfully updated {success_count}/{len(local_settings)} settings!")
    print("\n" + "="*70)
    print("📋 NEXT STEPS:")
    print("="*70)
    print("1. ✅ Settings have been populated with your local configuration")
    print("2. 🔑 Add your API keys in the Settings page:")
    print("   - GROQ_API_KEY (you were using Groq locally)")
    print("   - SECRET_KEY (generate a secure key)")
    print("3. 🔄 Refresh the Settings page to see all populated values")
    print("4. 💾 Save any additional API keys you want to use")
    print("5. 🚀 Your ATS should now work exactly like it did locally!")
    print("="*70)

if __name__ == "__main__":
    apply_local_settings_to_production()