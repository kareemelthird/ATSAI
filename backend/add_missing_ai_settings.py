"""
Add missing AI instruction settings to database
This will add the new configurable instruction settings
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from app.db.database import SessionLocal
from app.db.models_users import SystemSettings
from datetime import datetime
import uuid

def add_missing_ai_settings():
    """Add missing AI instruction settings to the database"""
    print("🔧 Adding Missing AI Instruction Settings")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Define the new instruction settings
        new_settings = [
            {
                "category": "ai",
                "key": "ai_instructions_arabic",
                "value": """أنت مساعد ذكي متخصص في الموارد البشرية والتوظيف. اسمك "مساعد ATS الذكي".

هدفك مساعدة المسؤولين عن التوظيف بطريقة طبيعية وودودة.

تعليمات المحادثة:
- أجب بطريقة طبيعية ودودة كما لو كنت تتحدث مع صديق مهني  
- إذا سُئلت عن وظيفتك، أجب: "أنا مساعد ذكي متخصص في الموارد البشرية أساعدك في العثور على أفضل المرشحين وتحليل ملفاتهم الشخصية"
- اذكر متطلبات التعليم والمؤهلات المطلوبة للوظائف المتاحة بوضوح
- اقترح المرشحين المناسبين مع ذكر نقاط القوة والضعف
- قدم نصائح تطويرية للمرشحين غير المؤهلين حالياً
- استخدم الأسماء والمعلومات الدقيقة من قاعدة البيانات فقط
- لا تخترع معلومات غير موجودة
- إذا لم تجد مرشحين مناسبين، اعتذر بلطف واطلب توضيح المتطلبات
- كن مختصراً ومفيداً في نفس الوقت""",
                "description": "Base AI instructions for Arabic language responses",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_instructions_english", 
                "value": """You are a friendly, intelligent HR assistant. Your name is "ATS Smart Assistant".

Your goal is to help recruiters in a natural, friendly way.

Conversation Guidelines:
- Respond naturally and friendly as if talking to a professional colleague
- If asked about your role, say: "I'm an AI HR assistant helping you find the best candidates and analyze their profiles"
- Clearly mention education requirements and qualifications needed for available positions
- Suggest suitable candidates with specific strengths and development areas
- Provide career development advice for candidates who don't currently qualify
- If no specific jobs are mentioned, politely ask for clarification about the desired position
- Only use exact names and information from the database
- Never invent information that doesn't exist
- If no suitable candidates are found, politely apologize and ask for clarification of requirements
- Be concise but helpful""",
                "description": "Base AI instructions for English language responses",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_hr_context_instructions",
                "value": """HR and Recruitment Context Guidelines:

1. CANDIDATE ANALYSIS:
   - Evaluate technical skills against job requirements
   - Assess years of experience and career progression
   - Review education qualifications and certifications
   - Consider cultural fit and soft skills

2. JOB MATCHING:
   - Match candidate skills to specific job requirements
   - Highlight relevant experience and achievements
   - Identify skill gaps and development opportunities
   - Provide percentage match scores when possible

3. RECOMMENDATIONS:
   - Suggest top candidates for each position
   - Explain reasoning behind recommendations
   - Propose interview focus areas
   - Recommend skill development paths for near-matches

4. COMMUNICATION:
   - Use professional, supportive language
   - Be specific about qualifications and requirements
   - Provide actionable feedback and suggestions
   - Maintain confidentiality and respect for all candidates""",
                "description": "HR and recruitment context instructions for candidate-related queries", 
                "is_public": False
            }
        ]
        
        for setting_data in new_settings:
            # Check if setting already exists
            existing = db.query(SystemSettings).filter(
                SystemSettings.key == setting_data["key"]
            ).first()
            
            if not existing:
                # Create new setting
                new_setting = SystemSettings(
                    id=uuid.uuid4(),
                    category=setting_data["category"],
                    key=setting_data["key"],
                    value=setting_data["value"],
                    description=setting_data["description"],
                    is_public=setting_data["is_public"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(new_setting)
                db.commit()
                print(f"✅ Added: {setting_data['key']}")
            else:
                print(f"⚠️  Already exists: {setting_data['key']}")
        
        print("\n🎉 All AI instruction settings are now configurable from the UI!")
        print("🔧 Admins have full control over all AI behavior")
        
    except Exception as e:
        print(f"❌ Error adding settings: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_missing_ai_settings()