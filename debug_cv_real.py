"""
Debug Real CV Upload Issue
==========================

Test actual CV upload to see what's happening with name extraction
"""

import sys
from pathlib import Path
import asyncio
import json

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

from app.db.database import SessionLocal
from app.services.ai_service import analyze_resume, call_ai_api
from app.core.config import settings

async def debug_cv_upload():
    """Debug the actual CV upload process"""
    
    print("🔍 Debugging CV Upload Issue")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        print(f"1. 🔧 Configuration Check:")
        print(f"   USE_MOCK_AI: {settings.USE_MOCK_AI}")
        print(f"   AI_PROVIDER: {settings.AI_PROVIDER}")
        
        # Test the actual CV text that was uploaded
        real_cv_text = """
        John Doe
        SharePoint Developer
        
        Email: john.doe@example.com
        Phone: +1-234-567-8900
        
        Professional Summary:
        Experienced SharePoint-online and Power platform developer with over one year of experience 
        in developing and supporting various web-based applications using Microsoft technologies 
        such as Power Automate and Model Driven Apps.
        
        Skills:
        - SharePoint Online
        - Power Platform
        - Power Automate
        - Model Driven Apps
        - Microsoft Technologies
        
        Experience:
        SharePoint Developer | Company ABC | 2023 - Present
        • Developed SharePoint Online solutions
        • Built Power Platform applications
        • Implemented Power Automate workflows
        """
        
        print(f"\\n2. 🤖 Testing AI Call...")
        print(f"   CV text length: {len(real_cv_text)} characters")
        
        # Test direct AI call first
        system_message = "Extract the name from this resume and return as JSON with first_name and last_name fields."
        
        ai_response = await call_ai_api(
            f"Extract name from: {real_cv_text[:200]}...", 
            system_message, 
            None, 
            db
        )
        
        print(f"\\n3. 📊 Raw AI Response:")
        print(f"   Response type: {type(ai_response)}")
        print(f"   Response: {ai_response[:500]}...")
        
        # Test full CV analysis
        print(f"\\n4. 🔄 Full CV Analysis...")
        result = await analyze_resume(real_cv_text, None, db, current_user=None)
        
        print(f"\\n5. 📋 Analysis Result:")
        if isinstance(result, dict):
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   ✅ Success! Keys: {list(result.keys())}")
                for key in ['first_name', 'last_name', 'email']:
                    print(f"   {key}: {result.get(key, 'MISSING')}")
        else:
            print(f"   ⚠️ Unexpected type: {type(result)}")
            print(f"   Raw: {result}")
        
        print(f"\\n6. 🔧 Debugging Tips:")
        print(f"   - Check if mock AI is being used correctly")
        print(f"   - Verify JSON parsing is working")
        print(f"   - Check safe_extract_string function")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(debug_cv_upload())