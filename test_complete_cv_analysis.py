#!/usr/bin/env python3

# Test complete CV analysis with proper debugging
import sys
sys.path.append("./backend")

import asyncio
from app.services.ai_service import analyze_resume
from app.db.database import SessionLocal
from app.db.models import Candidate

async def test_full_cv_analysis():
    cv_text = """Ahmed Mohamed
Senior SharePoint Developer

Contact Information:
Email: ahmed.mohamed@company.com
Phone: +20-123-456-7890
Location: Cairo, Egypt
LinkedIn: linkedin.com/in/ahmed-mohamed

Professional Summary:
Experienced SharePoint Developer with 5+ years of expertise in SharePoint Online, Power Platform, and modern web technologies. Proven track record of developing custom solutions and automating business processes.

Technical Skills:
• SharePoint Online & On-Premises
• Power Platform (Power Apps, Power Automate, Power BI)
• JavaScript, TypeScript, React
• C#, .NET Framework
• SQL Server, REST APIs
• Azure DevOps, Git

Professional Experience:

SharePoint Developer | Tech Solutions Ltd | 2021 - Present
• Developed custom SharePoint solutions using SPFx framework
• Created automated workflows using Power Automate
• Implemented responsive web parts using React and TypeScript
• Collaborated with cross-functional teams to deliver business solutions

Junior Developer | Digital Corp | 2019 - 2021
• Maintained SharePoint sites and libraries
• Developed custom forms using PowerApps
• Assisted in data migration projects
• Provided technical support to end users

Education:
Bachelor of Computer Science
Cairo University | 2015 - 2019

Certifications:
• Microsoft 365 Certified: SharePoint Associate
• Power Platform Fundamentals
"""

    print("🧪 Testing complete CV analysis")
    print("=" * 50)
    print(f"CV text length: {len(cv_text)} characters")
    
    try:
        # Test the AI service
        result = await analyze_resume(cv_text)
        print("\n✅ Analysis successful!")
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        # Also check database
        db = SessionLocal()
        candidates = db.query(Candidate).filter(
            Candidate.email.in_(["ahmed.mohamed@company.com", "john.smith@email.com"])
        ).all()
        
        print(f"\n📋 Found {len(candidates)} candidates in database:")
        for candidate in candidates:
            print(f"  - ID: {candidate.id}")
            print(f"  - Name: {candidate.first_name} {candidate.last_name}")
            print(f"  - Email: {candidate.email}")
            print(f"  - Phone: {candidate.phone}")
            print(f"  - Created: {candidate.created_at}")
            print()
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_cv_analysis())