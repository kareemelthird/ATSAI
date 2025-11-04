"""
Test script to verify the custom instructions functionality
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from app.db.database import SessionLocal
from app.db.models_users import User, SystemSettings

def test_custom_instructions():
    """Test custom instructions features"""
    print("🧪 Testing custom instructions functionality...")
    
    db = SessionLocal()
    try:
        # Check if new fields exist in User table
        print("\n📋 Checking User table fields...")
        users = db.query(User).first()
        if users:
            print(f"✅ Found user: {users.email}")
            print(f"   Custom chat instructions: {'✅' if hasattr(users, 'custom_chat_instructions') else '❌'}")
            print(f"   Custom CV analysis instructions: {'✅' if hasattr(users, 'custom_cv_analysis_instructions') else '❌'}")
            print(f"   Use custom instructions: {'✅' if hasattr(users, 'use_custom_instructions') else '❌'}")
        else:
            print("⚠️  No users found in database")
        
        # Check if new settings exist
        print("\n⚙️  Checking SystemSettings...")
        required_settings = [
            "MAX_MESSAGES_PER_USER_DAILY",
            "MAX_UPLOAD_SIZE_MB", 
            "MAX_UPLOADS_PER_USER_DAILY",
            "ALLOW_USER_CUSTOM_INSTRUCTIONS"
        ]
        
        for setting_key in required_settings:
            setting = db.query(SystemSettings).filter(SystemSettings.key == setting_key).first()
            if setting:
                print(f"✅ {setting_key}: {setting.value} (public: {setting.is_public})")
            else:
                print(f"❌ {setting_key}: Not found")
        
        # Test AI service import
        print("\n🤖 Testing AI service integration...")
        try:
            from app.services.ai_service import get_ai_setting
            test_setting = get_ai_setting(db, "ALLOW_USER_CUSTOM_INSTRUCTIONS", "false")
            print(f"✅ AI service integration working: ALLOW_USER_CUSTOM_INSTRUCTIONS = {test_setting}")
        except Exception as e:
            print(f"❌ AI service error: {e}")
        
        print("\n🎉 Custom instructions functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_custom_instructions()