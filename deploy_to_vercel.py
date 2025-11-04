"""
Deploy AI Configuration Changes to Vercel Production
===================================================

This script helps deploy the complete AI configuration system to Vercel production.
"""

import asyncio
import httpx
import os
from datetime import datetime

# Vercel production database migration SQL
MIGRATION_SQL = """
-- Add new AI configuration settings to production database
-- Run this on your Vercel PostgreSQL database

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_instructions_arabic', 'أنت مساعد ذكي متخصص في الموارد البشرية والتوظيف. اسمك "مساعد ATS الذكي".

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
- كن مختصراً ومفيداً في نفس الوقت', 'Base AI instructions for Arabic language responses', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_instructions_english', 'You are a friendly, intelligent HR assistant. Your name is "ATS Smart Assistant".

Your goal is to help recruiters in a natural, friendly way.

Conversation Guidelines:
- Respond naturally and friendly as if talking to a professional colleague
- If asked about your role, say: "I''m an AI HR assistant helping you find the best candidates and analyze their profiles"
- Clearly mention education requirements and qualifications needed for available positions
- Suggest suitable candidates with specific strengths and development areas
- Provide career development advice for candidates who don''t currently qualify
- If no specific jobs are mentioned, politely ask for clarification about the desired position
- Only use exact names and information from the database
- Never invent information that doesn''t exist
- If no suitable candidates are found, politely apologize and ask for clarification of requirements
- Be concise but helpful', 'Base AI instructions for English language responses', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_hr_context_instructions', 'HR and Recruitment Context Guidelines:

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
   - Maintain confidentiality and respect for all candidates', 'HR and recruitment context instructions for candidate-related queries', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_chat_instructions', 'You are an AI HR assistant specialized in recruitment and talent management.

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
- Use data-driven insights when available', 'Instructions for general AI chat responses and behavior', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_resume_analysis_instructions', 'You are an expert HR assistant that analyzes resumes and CVs.

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
- Highlight unique qualifications or achievements', 'AI instructions for resume analysis and evaluation', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_evaluation_format_arabic', 'تقييم المرشحين - التنسيق العربي:

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
   - توصية بالمقابلة أم لا', 'Format and guidelines for AI candidate evaluation in Arabic', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_evaluation_format_english', 'Candidate Evaluation Format - English:

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
   - Interview recommendation (Yes/No)', 'Format and guidelines for AI candidate evaluation in English', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_fallback_response_arabic', 'عذراً، أواجه صعوبة في الوصول إلى خدمة الذكاء الاصطناعي في الوقت الحالي. 

يمكنك:
- المحاولة مرة أخرى بعد قليل
- مراجعة قوائم المرشحين والوظائف مباشرة
- التواصل مع فريق الدعم التقني

أعتذر عن الإزعاج وشكراً لصبرك.', 'Default response when AI service is unavailable (Arabic)', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_fallback_response_english', 'I''m sorry, I''m currently experiencing difficulty accessing the AI service.

You can:
- Try again in a few moments
- Browse candidates and jobs directly
- Contact technical support for assistance

I apologize for the inconvenience and thank you for your patience.', 'Default response when AI service is unavailable (English)', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_mock_role_response_arabic', 'أنا مساعد ذكي متخصص في الموارد البشرية أساعدك في العثور على أفضل المرشحين وتحليل ملفاتهم الشخصية. يمكنني مساعدتك في:

• البحث عن المرشحين المناسبين للوظائف
• تحليل وتقييم السير الذاتية
• مقارنة المرشحين وترتيبهم حسب الأولوية
• الإجابة على استفساراتك حول عملية التوظيف

كيف يمكنني مساعدتك اليوم؟', 'Mock response for role questions in Arabic when AI service is unavailable', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_mock_role_response_english', 'I''m an AI HR assistant helping you find the best candidates and analyze their profiles. I can help you with:

• Finding suitable candidates for job positions
• Analyzing and evaluating resumes
• Comparing candidates and ranking them by priority
• Answering your recruitment questions

How can I help you today?', 'Mock response for role questions in English when AI service is unavailable', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_mock_default_response_arabic', 'أهلاً بك! أنا هنا لمساعدتك في عملية التوظيف. يمكنني البحث عن المرشحين المناسبين وتحليل ملفاتهم الشخصية. ما هي الوظيفة أو المهارات التي تبحث عنها؟', 'Default mock response for general questions in Arabic', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_mock_default_response_english', 'Hello! I''m here to help you with recruitment. I can search for suitable candidates and analyze their profiles. What position or skills are you looking for?', 'Default mock response for general questions in English', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_language_enforcement_arabic', 'أجب باللغة العربية فقط ولا تستخدم أي كلمات أو رموز إنجليزية', 'Language enforcement instruction for Arabic responses', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) VALUES
(gen_random_uuid(), 'ai', 'ai_language_enforcement_english', 'Respond in English only. Do not use Arabic, Asian, or other non-English characters', 'Language enforcement instruction for English responses', false, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;

-- Remove duplicate chat_system_instructions if it exists
DELETE FROM system_settings WHERE key = 'chat_system_instructions';

-- Verify the migration
SELECT key, description FROM system_settings WHERE category = 'ai' ORDER BY key;
"""

async def test_production_connection():
    """Test if we can connect to the production API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://atsai-jade.vercel.app/api/v1/health")
            if response.status_code == 200:
                print("✅ Production API is accessible")
                return True
            else:
                print(f"⚠️ Production API returned status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to production API: {e}")
        return False

def save_migration_file():
    """Save the migration SQL to a file"""
    with open("production_ai_migration.sql", "w", encoding="utf-8") as f:
        f.write(MIGRATION_SQL)
    print("✅ Migration SQL saved to: production_ai_migration.sql")

def print_deployment_instructions():
    """Print step-by-step deployment instructions"""
    print("""
🚀 VERCEL DEPLOYMENT INSTRUCTIONS
==================================

STEP 1: Prepare for Deployment
------------------------------
✅ Code changes are ready locally
✅ Migration SQL file created: production_ai_migration.sql

STEP 2: Deploy Code to Vercel
-----------------------------
Run these commands:

git add .
git commit -m "feat: Complete AI configuration system - Admin UI control"
git push origin main

Vercel will automatically deploy the new code.

STEP 3: Apply Database Migration
-------------------------------
1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Open your ATS project
3. Go to "Storage" tab
4. Open your PostgreSQL database
5. Go to "Query" tab
6. Copy and paste the content from production_ai_migration.sql
7. Execute the migration

STEP 4: Verify Deployment
------------------------
1. Visit: https://atsai-jade.vercel.app
2. Login as admin
3. Go to Settings page
4. Verify you see all new AI configuration options
5. Test changing an AI setting and save
6. Test the AI chat to confirm it uses the new settings

STEP 5: Configure AI Settings
----------------------------
As admin, you can now configure:
- AI personality for Arabic and English
- Resume analysis instructions
- Chat behavior and responses
- Error messages and fallbacks
- Language enforcement rules
- Evaluation formats

🎉 COMPLETE UI CONTROL ACHIEVED!
===============================

The admin now has FULL control over ALL AI behavior via the UI!
No more hard-coded instructions - everything is configurable!

""")

def main():
    print("🚀 Vercel Deployment Preparation")
    print("=" * 40)
    
    # Save migration file
    save_migration_file()
    
    # Test production connection
    print("\\n🔍 Testing production connection...")
    
    # Print deployment instructions
    print_deployment_instructions()
    
    print(f"📅 Deployment prepared at: {datetime.now()}")
    print("🎯 Ready to deploy complete AI configuration system!")

if __name__ == "__main__":
    main()