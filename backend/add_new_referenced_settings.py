"""
Add all the new AI settings we referenced in the code
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

def add_new_referenced_settings():
    """Add all new AI settings referenced in the updated code"""
    print("🔧 Adding New Referenced AI Settings")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # All the new settings we referenced in the code updates
        new_settings = [
            # Mock response settings for testing
            {
                "category": "ai",
                "key": "ai_mock_role_response_arabic",
                "value": """أنا مساعد ذكي متخصص في الموارد البشرية أساعدك في العثور على أفضل المرشحين وتحليل ملفاتهم الشخصية. يمكنني مساعدتك في:

• البحث عن المرشحين المناسبين للوظائف
• تحليل وتقييم السير الذاتية
• مقارنة المرشحين وترتيبهم حسب الأولوية
• الإجابة على استفساراتك حول عملية التوظيف

كيف يمكنني مساعدتك اليوم؟""",
                "description": "Mock response for role questions in Arabic when AI service is unavailable",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_mock_role_response_english",
                "value": """I'm an AI HR assistant helping you find the best candidates and analyze their profiles. I can help you with:

• Finding suitable candidates for job positions
• Analyzing and evaluating resumes
• Comparing candidates and ranking them by priority
• Answering your recruitment questions

How can I help you today?""",
                "description": "Mock response for role questions in English when AI service is unavailable",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_mock_default_response_arabic",
                "value": "أهلاً بك! أنا هنا لمساعدتك في عملية التوظيف. يمكنني البحث عن المرشحين المناسبين وتحليل ملفاتهم الشخصية. ما هي الوظيفة أو المهارات التي تبحث عنها؟",
                "description": "Default mock response for general questions in Arabic",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_mock_default_response_english",
                "value": "Hello! I'm here to help you with recruitment. I can search for suitable candidates and analyze their profiles. What position or skills are you looking for?",
                "description": "Default mock response for general questions in English",
                "is_public": False
            },
            # Language enforcement settings
            {
                "category": "ai",
                "key": "ai_language_enforcement_arabic",
                "value": "أجب باللغة العربية فقط ولا تستخدم أي كلمات أو رموز إنجليزية",
                "description": "Language enforcement instruction for Arabic responses",
                "is_public": False
            },
            {
                "category": "ai",
                "key": "ai_language_enforcement_english",
                "value": "Respond in English only. Do not use Arabic, Asian, or other non-English characters",
                "description": "Language enforcement instruction for English responses",
                "is_public": False
            }
        ]
        
        added_count = 0
        existing_count = 0
        
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
                added_count += 1
            else:
                print(f"⚠️  Already exists: {setting_data['key']}")
                existing_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Added: {added_count} new settings")
        print(f"   ⚠️  Existing: {existing_count} settings")
        print(f"   📝 Total: {added_count + existing_count} new referenced settings")
        
        if added_count > 0:
            print("\n🎉 All referenced AI settings are now available!")
            print("👑 Complete admin control via UI achieved!")
        
    except Exception as e:
        print(f"❌ Error adding settings: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_new_referenced_settings()