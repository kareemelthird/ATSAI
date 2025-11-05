-- SAFE PRODUCTION MIGRATION FOR AI SETTINGS
-- This migration uses safe INSERT WHERE NOT EXISTS pattern
-- No unique constraints needed

-- Clean up any duplicate chat instructions first
DELETE FROM system_settings WHERE key = 'chat_system_instructions';

-- AI Instructions Arabic
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_instructions_arabic', 
    'أنت مساعد ذكي متخصص في الموارد البشرية والتوظيف. اسمك "مساعد ATS الذكي".

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
- كن مختصراً ومفيداً في نفس الوقت', 
    'Base AI instructions for Arabic language responses', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_instructions_arabic');

-- AI Instructions English
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_instructions_english', 
    'You are a friendly, intelligent HR assistant. Your name is "ATS Smart Assistant".

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
- Be concise but helpful', 
    'Base AI instructions for English language responses', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_instructions_english');

-- HR Context Instructions
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_hr_context_instructions', 
    'HR and Recruitment Context Guidelines:

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
   - Maintain confidentiality and respect for all candidates', 
    'HR and recruitment context instructions for candidate-related queries', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_hr_context_instructions');

-- Chat Instructions
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_chat_instructions', 
    'You are an AI HR assistant specialized in recruitment and talent management.

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
- Use data-driven insights when available', 
    'Instructions for general AI chat responses and behavior', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_chat_instructions');

-- Resume Analysis Instructions
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_resume_analysis_instructions', 
    'You are an expert HR assistant that analyzes resumes and CVs.

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
- Highlight unique qualifications or achievements', 
    'AI instructions for resume analysis and evaluation', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_resume_analysis_instructions');

-- Evaluation Format Arabic
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_evaluation_format_arabic', 
    'تقييم المرشحين - التنسيق العربي:

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
   - توصية بالمقابلة أم لا', 
    'Format and guidelines for AI candidate evaluation in Arabic', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_evaluation_format_arabic');

-- Evaluation Format English
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_evaluation_format_english', 
    'Candidate Evaluation Format - English:

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
   - Interview recommendation (Yes/No)', 
    'Format and guidelines for AI candidate evaluation in English', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_evaluation_format_english');

-- Fallback Response Arabic
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_fallback_response_arabic', 
    'عذراً، أواجه صعوبة في الوصول إلى خدمة الذكاء الاصطناعي في الوقت الحالي. 

يمكنك:
- المحاولة مرة أخرى بعد قليل
- مراجعة قوائم المرشحين والوظائف مباشرة
- التواصل مع فريق الدعم التقني

أعتذر عن الإزعاج وشكراً لصبرك.', 
    'Default response when AI service is unavailable (Arabic)', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_fallback_response_arabic');

-- Fallback Response English
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_fallback_response_english', 
    'I''m sorry, I''m currently experiencing difficulty accessing the AI service.

You can:
- Try again in a few moments
- Browse candidates and jobs directly
- Contact technical support for assistance

I apologize for the inconvenience and thank you for your patience.', 
    'Default response when AI service is unavailable (English)', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_fallback_response_english');

-- Mock Role Response Arabic
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_mock_role_response_arabic', 
    'أنا مساعد ذكي متخصص في الموارد البشرية أساعدك في العثور على أفضل المرشحين وتحليل ملفاتهم الشخصية. يمكنني مساعدتك في:

• البحث عن المرشحين المناسبين للوظائف
• تحليل وتقييم السير الذاتية
• مقارنة المرشحين وترتيبهم حسب الأولوية
• الإجابة على استفساراتك حول عملية التوظيف

كيف يمكنني مساعدتك اليوم؟', 
    'Mock response for role questions in Arabic when AI service is unavailable', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_mock_role_response_arabic');

-- Mock Role Response English
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_mock_role_response_english', 
    'I''m an AI HR assistant helping you find the best candidates and analyze their profiles. I can help you with:

• Finding suitable candidates for job positions
• Analyzing and evaluating resumes
• Comparing candidates and ranking them by priority
• Answering your recruitment questions

How can I help you today?', 
    'Mock response for role questions in English when AI service is unavailable', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_mock_role_response_english');

-- Mock Default Response Arabic
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_mock_default_response_arabic', 
    'أهلاً بك! أنا هنا لمساعدتك في عملية التوظيف. يمكنني البحث عن المرشحين المناسبين وتحليل ملفاتهم الشخصية. ما هي الوظيفة أو المهارات التي تبحث عنها؟', 
    'Default mock response for general questions in Arabic', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_mock_default_response_arabic');

-- Mock Default Response English
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_mock_default_response_english', 
    'Hello! I''m here to help you with recruitment. I can search for suitable candidates and analyze their profiles. What position or skills are you looking for?', 
    'Default mock response for general questions in English', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_mock_default_response_english');

-- Language Enforcement Arabic
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_language_enforcement_arabic', 
    'أجب باللغة العربية فقط ولا تستخدم أي كلمات أو رموز إنجليزية', 
    'Language enforcement instruction for Arabic responses', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_language_enforcement_arabic');

-- Language Enforcement English
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'ai_language_enforcement_english', 
    'Respond in English only. Do not use Arabic, Asian, or other non-English characters', 
    'Language enforcement instruction for English responses', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'ai_language_enforcement_english');

-- Force Personal API Key Setting (with toggle option)
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'require_personal_api_key', 
    'false', 
    'Force users to provide their own API key for AI chat functionality (true/false)', 
    true, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'require_personal_api_key');

-- API Key Required Message Arabic
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'api_key_required_message_arabic', 
    'للاستفادة من خدمة الذكاء الاصطناعي، يجب عليك إضافة مفتاح API الخاص بك في صفحة الملف الشخصي. يمكنك الحصول على مفتاح مجاني من Groq.com', 
    'Message shown to Arabic users when personal API key is required', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'api_key_required_message_arabic');

-- API Key Required Message English
INSERT INTO system_settings (id, category, key, value, description, is_public, created_at, updated_at) 
SELECT 
    gen_random_uuid(), 
    'ai', 
    'api_key_required_message_english', 
    'To use AI features, please add your personal API key in your Profile settings. You can get a free API key from Groq.com', 
    'Message shown to English users when personal API key is required', 
    false, 
    NOW(), 
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'api_key_required_message_english');

-- Verify the migration worked
SELECT 
    key, 
    description,
    CASE WHEN LENGTH(value) > 50 THEN LEFT(value, 50) || '...' ELSE value END as preview
FROM system_settings 
WHERE category = 'ai' 
ORDER BY key;

-- Count total AI settings
SELECT COUNT(*) as total_ai_settings FROM system_settings WHERE category = 'ai';