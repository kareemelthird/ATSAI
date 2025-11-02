#!/usr/bin/env python3
"""
Script to add AI instruction settings to the database.
This allows admin to configure all AI instructions through the system settings interface.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.models_system_settings import SystemAISetting
from app.db.database import Base

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://k3admin:KH%40123456@localhost:5432/ats_db")

def add_ai_settings():
    """Add AI instruction settings to the database."""
    
    # Create database engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # AI instruction settings to add
        settings = [
            {
                "setting_key": "ai_instructions_arabic",
                "setting_value": """أنت مساعد ذكي ودود متخصص في الموارد البشرية. اسمك "مساعد ATS الذكي".

هدفك مساعدة المسؤولين عن التوظيف بطريقة طبيعية وودودة.

تعليمات المحادثة:
- أجب بطريقة طبيعية ودودة كما لو كنت تتحدث مع صديق مهني
- إذا سُئلت عن وظيفتك، أجب: "أنا مساعد ذكي متخصص في الموارد البشرية أساعدك في العثور على أفضل المرشحين وتحليل ملفاتهم الشخصية"
- إذا لم تكن هناك وظائف محددة، اطلب توضيحاً بلطف عن نوع الوظيفة المطلوبة
- استخدم الأسماء والمعلومات الدقيقة من قاعدة البيانات فقط
- لا تخترع معلومات غير موجودة
- إذا لم تجد مرشحين مناسبين، اعتذر بلطف واطلب توضيح المتطلبات
- كن مختصراً ومفيداً في نفس الوقت""",
                "setting_type": "text",
                "description": "AI instructions in Arabic for chat responses"
            },
            {
                "setting_key": "ai_instructions_english", 
                "setting_value": """You are a friendly, intelligent HR assistant. Your name is "ATS Smart Assistant".

Your goal is to help recruiters in a natural, friendly way.

Conversation Guidelines:
- Respond naturally and friendly as if talking to a professional colleague
- If asked about your role, say: "I'm an AI HR assistant helping you find the best candidates and analyze their profiles"
- If no specific jobs are mentioned, politely ask for clarification about the desired position
- Only use exact names and information from the database
- Never invent information that doesn't exist
- If no suitable candidates are found, politely apologize and ask for clarification of requirements
- Be concise but helpful""",
                "setting_type": "text",
                "description": "AI instructions in English for chat responses"
            },
            {
                "setting_key": "ai_resume_analysis_instructions",
                "setting_value": """You are an expert HR analyst. Analyze the resume data and provide a professional assessment.

Instructions:
- Be comprehensive but concise
- Focus on key qualifications, experience, and skills
- Highlight strengths and potential areas for development
- Provide actionable insights for recruiters
- Use professional HR terminology
- Be objective and unbiased in your analysis""",
                "setting_type": "text", 
                "description": "AI instructions for resume analysis and evaluation"
            }
        ]
        
        # Add each setting if it doesn't already exist
        added_count = 0
        updated_count = 0
        
        for setting_data in settings:
            existing = db.query(SystemAISetting).filter(
                SystemAISetting.setting_key == setting_data["setting_key"]
            ).first()
            
            if existing:
                # Update existing setting
                existing.setting_value = setting_data["setting_value"]
                existing.setting_type = setting_data["setting_type"]
                existing.description = setting_data["description"]
                updated_count += 1
                print(f"✅ Updated setting: {setting_data['setting_key']}")
            else:
                # Create new setting
                new_setting = SystemAISetting(
                    setting_key=setting_data["setting_key"],
                    setting_value=setting_data["setting_value"],
                    setting_type=setting_data["setting_type"],
                    description=setting_data["description"],
                    is_active=True
                )
                db.add(new_setting)
                added_count += 1
                print(f"✅ Added new setting: {setting_data['setting_key']}")
        
        # Commit all changes
        db.commit()
        print(f"\n🎉 Database update completed!")
        print(f"   - Added: {added_count} new settings")
        print(f"   - Updated: {updated_count} existing settings")
        print(f"   - Total AI instruction settings: {len(settings)}")
        
        # Verify the settings were added
        print(f"\n📋 Current AI instruction settings:")
        ai_settings = db.query(SystemAISetting).filter(
            SystemAISetting.setting_key.in_([s["setting_key"] for s in settings])
        ).all()
        
        for setting in ai_settings:
            status = "🟢 Active" if setting.is_active else "🔴 Inactive"
            print(f"   - {setting.setting_key}: {status}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding AI settings: {str(e)}")
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    print("🚀 Adding AI instruction settings to database...")
    print("=" * 50)
    
    success = add_ai_settings()
    
    if success:
        print("\n✅ AI instruction settings have been successfully added!")
        print("🔧 You can now edit these instructions through the Admin System Settings interface.")
        print("🤖 All AI responses will now use your custom instructions.")
    else:
        print("\n❌ Failed to add AI instruction settings.")
        print("🔍 Please check the database connection and try again.")