import requests
import json

# Get all available settings first
api_base = "https://atsai-jade.vercel.app/api/v1"

# Login first
login_data = {"email": "admin@ats.com", "password": "admin123"}
response = requests.post(f"{api_base}/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Get all settings
    get_response = requests.get(f"{api_base}/settings/", headers=headers)
    if get_response.status_code == 200:
        settings = get_response.json()
        print("\n📋 Available settings:")
        for setting in settings:
            if "ai" in setting['key'].lower() or "groq" in setting['key'].lower():
                print(f"  {setting['key']}: {setting['label']}")
                
        print("\n" + "="*50)
        
        # Now update the correct settings
        correct_settings = {
            "ai_resume_analysis_instructions": """أنت مساعد ذكي متخصص في تحليل السير الذاتية وتقييم المرشحين. مهمتك هي:

1. **تحليل السيرة الذاتية:**
   - استخراج المعلومات الشخصية (الاسم، البريد الإلكتروني، رقم الهاتف)
   - تحديد المهارات التقنية والشخصية
   - تحليل الخبرات العملية والتعليم
   - تقييم مستوى الخبرة

2. **التقييم والتقدير:**
   - إعطاء درجة من 1-100 للمرشح
   - تقديم ملخص موجز عن نقاط القوة والضعف
   - تحديد مدى ملاءمة المرشح للوظيفة

3. **التوصيات:**
   - اقتراح أسئلة مقابلة محددة
   - تحديد المجالات التي تحتاج إلى تطوير
   - تقديم نصائح لتحسين الملف الشخصي

استخدم اللغة العربية في التقييم والتحليل، وكن دقيقاً ومهنياً في تحليلك."""
        }
        
        print("Updating AI instructions...")
        for key, value in correct_settings.items():
            setting_data = {"value": value}
            
            response = requests.put(
                f"{api_base}/settings/{key}",
                headers=headers,
                json=setting_data
            )
            
            if response.status_code == 200:
                print(f"✅ {key}: Updated successfully")
            else:
                print(f"❌ {key}: Failed ({response.status_code}) - {response.text}")
else:
    print(f"❌ Login failed: {response.status_code}")