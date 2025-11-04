"""
Direct API test for custom instructions endpoints
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

import asyncio
from fastapi import Depends
from app.db.database import SessionLocal, get_db
from app.db.models_users import User, SystemSettings
from app.api.v1.endpoints.users import get_my_custom_instructions, update_my_custom_instructions
from app.schemas.schemas import CustomInstructionsUpdate
from app.core.auth import get_current_user

async def test_custom_instructions_api():
    """Test custom instructions API endpoints"""
    print("🧪 Testing custom instructions API endpoints...")
    
    db = SessionLocal()
    try:
        # Get a test user
        user = db.query(User).first()
        if not user:
            print("❌ No user found for testing")
            return
        
        print(f"📋 Testing with user: {user.email}")
        
        # Test get_my_custom_instructions
        print("\n🔍 Testing GET custom instructions...")
        try:
            result = await get_my_custom_instructions(current_user=user)
            print(f"✅ GET result: {result}")
        except Exception as e:
            print(f"❌ GET error: {e}")
        
        # Test update_my_custom_instructions 
        print("\n✏️  Testing PUT custom instructions...")
        try:
            update_data = CustomInstructionsUpdate(
                custom_chat_instructions="You are a helpful assistant specialized in HR.",
                custom_cv_analysis_instructions="Analyze CVs with focus on technical skills.",
                use_custom_instructions=True
            )
            
            result = await update_my_custom_instructions(
                instructions=update_data,
                db=db,
                current_user=user
            )
            print(f"✅ PUT result: {result}")
        except Exception as e:
            print(f"❌ PUT error: {e}")
        
        # Test settings endpoint functionality 
        print("\n⚙️  Testing settings integration...")
        try:
            from app.api.v1.endpoints.settings import get_public_settings
            public_settings = await get_public_settings(db=db)
            print(f"✅ Public settings: {len(public_settings)} settings available")
            
            # Check if our new settings are there
            setting_keys = [s['key'] for s in public_settings]
            required_keys = ["MAX_MESSAGES_PER_USER_DAILY", "MAX_UPLOAD_SIZE_MB", "ALLOW_USER_CUSTOM_INSTRUCTIONS"]
            
            for key in required_keys:
                if key in setting_keys:
                    print(f"   ✅ {key}: Found in public settings")
                else:
                    print(f"   ❌ {key}: Missing from public settings")
                    
        except Exception as e:
            print(f"❌ Settings integration error: {e}")
        
        print("\n🎉 API endpoints test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_custom_instructions_api())