#!/usr/bin/env python3

# Debug email extraction issue
import sys
sys.path.append("./backend")

import asyncio
from app.services.ai_service import call_ai_api, safe_extract_string
from app.db.database import SessionLocal
import json

async def debug_email_issue():
    """Debug why real email is being replaced with temp email"""
    
    print("🔍 Debugging Email Extraction Issue")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Test CV with real email
        cv_text = """Ahmed Mohamed
Senior SharePoint Developer

Contact Information:
Email: ahmed.mohamed@company.com
Phone: +20-123-456-7890
Location: Cairo, Egypt
"""

        # Test the AI call
        prompt = f"""Analyze the following resume/CV text and extract information:

{cv_text}

Return the extracted information in JSON format."""

        print("1. 🤖 Testing AI Response...")
        ai_response = await call_ai_api(prompt, None, None, db)
        print(f"AI Response: {ai_response[:200]}...")
        
        # Extract JSON from response
        if "```json" in ai_response:
            json_start = ai_response.find("```json") + 7
            json_end = ai_response.find("```", json_start)
            json_text = ai_response[json_start:json_end].strip()
        else:
            json_text = ai_response
        
        print(f"\n2. 📋 JSON Text: {json_text[:200]}...")
        
        # Parse JSON
        try:
            analysis = json.loads(json_text)
            print(f"\n3. ✅ JSON Parsed Successfully")
            print(f"Keys: {list(analysis.keys())}")
            
            # Test email extraction
            raw_email = safe_extract_string(analysis, "email", "NO_EMAIL_FALLBACK")
            print(f"\n4. 📧 Email Extraction:")
            print(f"   Raw email from analysis: '{raw_email}'")
            
            # Test the clean_email_address function
            from app.services.ai_service import clean_email_address
            cleaned_email = clean_email_address(raw_email)
            print(f"   Cleaned email: '{cleaned_email}'")
            
            # Test validation logic
            is_valid = cleaned_email and "@" in cleaned_email and not cleaned_email.startswith("temp_")
            print(f"   Is valid: {is_valid}")
            print(f"   Has @: {'@' in cleaned_email if cleaned_email else False}")
            print(f"   Starts with temp_: {cleaned_email.startswith('temp_') if cleaned_email else False}")
            
        except Exception as e:
            print(f"❌ JSON Parse Error: {e}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(debug_email_issue())