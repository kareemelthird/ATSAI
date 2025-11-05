#!/usr/bin/env python3

"""
Fix Temp Emails in Production Database
=====================================

This script identifies candidates with temp emails and attempts to extract
their real email addresses from their original CV text.
"""

import sys
sys.path.append("./backend")

import asyncio
import re
from app.db.database import SessionLocal
from app.db.models import Candidate

def extract_email_from_text(text: str) -> str:
    """Extract email from CV text using regex"""
    if not text:
        return None
    
    # Email regex pattern
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    
    # Find all emails in the text
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    
    if emails:
        # Return the first email found (usually the candidate's email)
        for email in emails:
            # Skip obviously temp or invalid emails
            if not any(word in email.lower() for word in ['temp', 'example', 'test', 'dummy']):
                return email.lower().strip()
    
    return None

async def fix_temp_emails():
    """Fix candidates with temp emails by extracting real emails from CV text"""
    
    print("🔧 Fixing Temp Emails in Production Database")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Find candidates with temp emails
        temp_email_candidates = db.query(Candidate).filter(
            Candidate.email.like("temp_%@temp.com")
        ).all()
        
        print(f"📋 Found {len(temp_email_candidates)} candidates with temp emails")
        
        if not temp_email_candidates:
            print("✅ No candidates with temp emails found!")
            return
        
        fixed_count = 0
        failed_count = 0
        
        for candidate in temp_email_candidates:
            print(f"\\n🔍 Processing: {candidate.first_name} {candidate.last_name}")
            print(f"   Current email: {candidate.email}")
            
            if candidate.original_resume_text:
                # Extract email from CV text
                real_email = extract_email_from_text(candidate.original_resume_text)
                
                if real_email and real_email != candidate.email:
                    # Check if this email is already used by another candidate
                    existing = db.query(Candidate).filter(
                        Candidate.email == real_email,
                        Candidate.id != candidate.id
                    ).first()
                    
                    if existing:
                        print(f"   ⚠️  Email {real_email} already used by another candidate")
                        failed_count += 1
                    else:
                        # Update the email
                        old_email = candidate.email
                        candidate.email = real_email
                        print(f"   ✅ Updated email: {old_email} → {real_email}")
                        fixed_count += 1
                else:
                    print(f"   ❌ No valid email found in CV text")
                    failed_count += 1
            else:
                print(f"   ❌ No CV text available")
                failed_count += 1
        
        # Commit changes
        db.commit()
        
        print(f"\\n📊 RESULTS:")
        print(f"✅ Successfully fixed: {fixed_count} candidates")
        print(f"❌ Could not fix: {failed_count} candidates")
        print(f"📋 Total processed: {len(temp_email_candidates)} candidates")
        
        # Show remaining temp emails
        remaining = db.query(Candidate).filter(
            Candidate.email.like("temp_%@temp.com")
        ).count()
        
        print(f"\\n📈 Remaining temp emails: {remaining}")
        
        if fixed_count > 0:
            print(f"\\n🎉 SUCCESS: Fixed {fixed_count} candidates with real emails!")
            print("📝 These candidates now have their correct email addresses.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fix_temp_emails())