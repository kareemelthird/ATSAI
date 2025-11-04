"""
Add ALL missing AI settings to make everything fully configurable
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

def add_all_missing_ai_settings():
    """Add all missing AI settings to make everything UI-configurable"""
    print("🔧 Adding ALL Missing AI Settings")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Complete set of AI settings
        all_ai_settings = [
            # Already added in previous script - check if they exist
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
            },
            # New settings that were missing
            {
                "category": "ai",
                "key": "ai_chat_instructions",
                "value": """You are an AI HR assistant specialized in recruitment and talent management.

Your Role:
- Help recruiters and HR professionals with candidate evaluation
- Provide insights on job matching and candidate assessment
- Assist with recruitment process optimization
- Offer professional, helpful guidance

Guidelines:
- Be professional yet approachable
- Focus on candidate qualifications and job fit
- Provide specific, actionable recommendations
- Respect candidate privacy and confidentiality
- Use data-driven insights when available""",
                "description": "Instructions for general AI chat responses and behavior",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_resume_analysis_instructions",
                "value": """You are an expert HR assistant that analyzes resumes and CVs.

Extract information accurately and comprehensively:
- Personal details (name, email, phone, location, links)
- Professional summary highlighting key achievements
- Calculate years of experience from work history
- Skills categorized by type (technical, soft, domain)
- Complete work experience with dates, companies, roles
- Education with institutions, degrees, dates
- Certifications with names, organizations, dates
- Languages with proficiency levels

Analysis Guidelines:
- Be thorough but accurate
- Include team leadership and project management details
- Extract daily tasks, main responsibilities, and key accomplishments
- Capture ALL relevant information about each role
- Identify career progression and growth patterns
- Note any gaps in employment or education
- Highlight unique qualifications or achievements""",
                "description": "AI instructions for resume analysis and evaluation",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_evaluation_format_arabic",
                "value": """تقييم المرشحين - التنسيق العربي:

1. تقييم المهارات التقنية:
   - مطابقة المهارات مع متطلبات الوظيفة
   - تقييم مستوى الخبرة والكفاءة
   - تحديد نقاط القوة والضعف

2. تقييم الخبرة المهنية:
   - سنوات الخبرة ذات الصلة
   - التطور الوظيفي والترقيات
   - انجازات ومشاريع محددة

3. تقييم التعليم والمؤهلات:
   - الدرجات الأكاديمية والتخصص
   - الشهادات المهنية والدورات
   - مدى ملاءمة المؤهلات للوظيفة

4. التوصية النهائية:
   - مستوى الملاءمة للوظيفة (نسبة مئوية)
   - نقاط القوة الرئيسية
   - مجالات التطوير المطلوبة
   - توصية بالمقابلة أم لا""",
                "description": "Format and guidelines for AI candidate evaluation in Arabic",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_evaluation_format_english",
                "value": """Candidate Evaluation Format - English:

1. Technical Skills Assessment:
   - Match skills against job requirements
   - Evaluate proficiency level and experience
   - Identify strengths and skill gaps

2. Professional Experience Review:
   - Years of relevant experience
   - Career progression and promotions
   - Specific achievements and projects

3. Education and Qualifications:
   - Academic degrees and specialization
   - Professional certifications and training
   - Relevance of qualifications to the role

4. Final Recommendation:
   - Overall job fit percentage
   - Key strengths and advantages
   - Areas for development
   - Interview recommendation (Yes/No)""",
                "description": "Format and guidelines for AI candidate evaluation in English",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_fallback_response_arabic",
                "value": """عذراً، أواجه صعوبة في الوصول إلى خدمة الذكاء الاصطناعي في الوقت الحالي. 

يمكنك:
- المحاولة مرة أخرى بعد قليل
- مراجعة قوائم المرشحين والوظائف مباشرة
- التواصل مع فريق الدعم التقني

أعتذر عن الإزعاج وشكراً لصبرك.""",
                "description": "Default response when AI service is unavailable (Arabic)",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_fallback_response_english",
                "value": """I'm sorry, I'm currently experiencing difficulty accessing the AI service.

You can:
- Try again in a few moments
- Browse candidates and jobs directly
- Contact technical support for assistance

I apologize for the inconvenience and thank you for your patience.""",
                "description": "Default response when AI service is unavailable (English)",
                "is_public": False
            }
        ]
        
        added_count = 0
        existing_count = 0
        
        for setting_data in all_ai_settings:
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
                added_count += 1
            else:
                print(f"⚠️  Already exists: {setting_data['key']}")
                existing_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Added: {added_count} new settings")
        print(f"   ⚠️  Existing: {existing_count} settings")
        print(f"   📝 Total: {added_count + existing_count} AI settings")
        
        print("\n🎉 ALL AI instructions are now fully configurable!")
        print("👑 Admin has complete control over AI behavior via UI!")
        print("🚫 No hard-coded instructions remain!")
        
    except Exception as e:
        print(f"❌ Error adding settings: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_all_missing_ai_settings()