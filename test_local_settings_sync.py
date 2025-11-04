import requests
import json

# Test adding all the important settings from local environment
api_base = "https://atsai-jade.vercel.app/api/v1"

# Local settings to replicate
local_settings = {
    "AI_PROVIDER": "groq",
    "PROJECT_NAME": "ATS System",
    "GROQ_API_KEY": "MASKED_FOR_SECURITY",
    "AI_MODEL": "llama-3.3-70b-versatile",
    "AI_INSTRUCTIONS": """أنت مساعد ذكي متخصص في تحليل السير الذاتية وتقييم المرشحين. مهمتك هي:

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

# Login first
login_data = {"email": "admin@ats.com", "password": "admin123"}
response = requests.post(f"{api_base}/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    print("\nUpdating settings from local environment:")
    
    success_count = 0
    failed_settings = []
    
    for key, value in local_settings.items():
        setting_data = {"value": value}
        
        response = requests.put(
            f"{api_base}/settings/{key}",
            headers=headers,
            json=setting_data
        )
        
        if response.status_code == 200:
            print(f"✅ {key}: Updated successfully")
            success_count += 1
        else:
            print(f"❌ {key}: Failed ({response.status_code})")
            failed_settings.append(key)
    
    print(f"\n📊 Results: {success_count}/{len(local_settings)} settings updated successfully")
    
    if failed_settings:
        print(f"Failed settings: {', '.join(failed_settings)}")
    
    # Verify by reading all settings
    get_response = requests.get(f"{api_base}/settings/", headers=headers)
    if get_response.status_code == 200:
        settings = get_response.json()
        print("\n🔍 Current settings values:")
        for setting in settings:
            if setting['key'] in local_settings:
                value = setting['value']
                if setting['is_encrypted'] and value:
                    value = "***ENCRYPTED***"
                print(f"  {setting['key']}: {value}")
else:
    print(f"❌ Login failed: {response.status_code}")