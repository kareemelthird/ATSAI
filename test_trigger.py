"""
Test CV Analysis Trigger
========================
"""

import sys
from pathlib import Path
import asyncio

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

from app.db.database import SessionLocal
from app.services.ai_service import call_ai_api

async def test_trigger():
    """Test the exact trigger used in CV analysis"""
    
    print("🧪 Testing CV Analysis Trigger")
    print("=" * 40)
    
    db = SessionLocal()
    
    try:
        # Test the exact prompt used in analyze_resume
        prompt = """Analyze this resume and extract structured information:

John Doe
SharePoint Developer
Email: john.doe@example.com

Return the analysis as JSON."""
        
        print(f"Prompt: {prompt[:100]}...")
        
        response = await call_ai_api(prompt, None, None, db)
        
        print(f"Response: {response[:200]}...")
        
        # Check if it contains JSON
        if "first_name" in response and "last_name" in response:
            print("✅ SUCCESS: Mock AI returned resume analysis!")
        else:
            print("❌ FAILED: Mock AI returned chat response")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_trigger())