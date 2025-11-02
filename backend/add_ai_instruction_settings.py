#!/usr/bin/env python3
"""
Add configurable AI instructions to system settings
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models_system_settings import SystemAISetting

def add_ai_instruction_settings():
    db: Session = SessionLocal()
    
    try:
        # Arabic AI instructions
        arabic_instructions = """أنت مساعد ذكي ودود متخصص في الموارد البشرية. اسمك "مساعد ATS الذكي".

هدفك مساعدة المسؤولين عن التوظيف بطريقة طبيعية وودودة.

تعليمات المحادثة:
- أجب بطريقة طبيعية ودودة كما لو كنت تتحدث مع صديق مهني
- إذا سُئلت عن وظيفتك، أجب: "أنا مساعد ذكي متخصص في الموارد البشرية أساعدك في العثور على أفضل المرشحين وتحليل ملفاتهم الشخصية"
- إذا لم تكن هناك وظائف محددة، اطلب توضيحاً بلطف عن نوع الوظيفة المطلوبة
- استخدم الأسماء والمعلومات الدقيقة من قاعدة البيانات فقط
- لا تخترع معلومات غير موجودة
- إذا لم تجد مرشحين مناسبين، اعتذر بلطف واطلب توضيح المتطلبات
- كن مختصراً ومفيداً في نفس الوقت"""

        english_instructions = """You are a friendly, intelligent HR assistant. Your name is "ATS Smart Assistant".

Your goal is to help recruiters in a natural, friendly way.

Conversation Guidelines:
- Respond naturally and friendly as if talking to a professional colleague
- If asked about your role, say: "I'm an AI HR assistant helping you find the best candidates and analyze their profiles"
- If no specific jobs are mentioned, politely ask for clarification about the desired position
- Only use exact names and information from the database
- Never invent information that doesn't exist
- If no suitable candidates are found, politely apologize and ask for clarification of requirements
- Be concise but helpful"""

        resume_analysis_instructions = """You are an expert HR assistant that analyzes resumes.

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
- Be comprehensive - capture ALL relevant information about each role"""

        # Settings to add
        settings_to_add = [
            {
                "key": "ai_instructions_arabic",
                "value": arabic_instructions,
                "data_type": "text",
                "description": "AI system instructions for Arabic language responses",
                "category": "ai_chat",
                "is_user_configurable": True
            },
            {
                "key": "ai_instructions_english", 
                "value": english_instructions,
                "data_type": "text",
                "description": "AI system instructions for English language responses",
                "category": "ai_chat",
                "is_user_configurable": True
            },
            {
                "key": "ai_resume_analysis_instructions",
                "value": resume_analysis_instructions,
                "data_type": "text", 
                "description": "AI system instructions for resume analysis",
                "category": "ai_analysis",
                "is_user_configurable": True
            }
        ]
        
        for setting_data in settings_to_add:
            # Check if setting already exists
            existing = db.query(SystemAISetting).filter(
                SystemAISetting.key == setting_data["key"]
            ).first()
            
            if existing:
                print(f"✅ Setting '{setting_data['key']}' already exists, updating...")
                for key, value in setting_data.items():
                    if key != "key":
                        setattr(existing, key, value)
            else:
                print(f"📝 Adding new setting: {setting_data['key']}")
                new_setting = SystemAISetting(**setting_data)
                db.add(new_setting)
        
        db.commit()
        print("\n✅ AI instruction settings have been added/updated successfully!")
        
        # Show what was added
        print("\n📋 Current AI instruction settings:")
        ai_settings = db.query(SystemAISetting).filter(
            SystemAISetting.key.in_([
                "ai_instructions_arabic",
                "ai_instructions_english", 
                "ai_resume_analysis_instructions"
            ])
        ).all()
        
        for setting in ai_settings:
            print(f"- {setting.key}: {setting.description}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_ai_instruction_settings()