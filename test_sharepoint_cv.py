"""
Test CV Upload with SharePoint developer resume
"""

import sys
from pathlib import Path
import asyncio

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

from app.db.database import SessionLocal
from app.services.ai_service import analyze_resume

async def test_sharepoint_cv():
    """Test with SharePoint developer CV like the user uploaded"""
    
    print("🧪 Testing SharePoint Developer CV")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Sample CV text similar to what user uploaded
        sharepoint_cv = """
        Ahmed Mohamed
        SharePoint Developer
        
        Email: ahmed.mohamed@company.com
        Phone: +20-123-456-7890
        Location: Cairo, Egypt
        LinkedIn: linkedin.com/in/ahmedmohamed
        
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
        - C#
        - JavaScript
        - SQL Server
        - Azure
        - Office 365
        
        Work Experience:
        
        SharePoint Developer | Tech Solutions Ltd | Jan 2023 - Present
        • Developed SharePoint Online solutions for enterprise clients
        • Built custom Power Platform applications
        • Implemented automated workflows using Power Automate
        • Created Model Driven Apps for business processes
        • Collaborated with cross-functional teams
        
        Junior Developer | Software House | Jun 2022 - Dec 2022
        • Supported web application development
        • Worked with Microsoft technologies
        • Participated in code reviews and testing
        
        Education:
        Bachelor of Computer Science
        Cairo University | 2022
        Grade: Very Good
        """
        
        print(f"CV text length: {len(sharepoint_cv)} characters")
        
        # Test the analysis
        result = await analyze_resume(sharepoint_cv, None, db, current_user=None)
        
        print(f"\\n📊 Analysis Results:")
        print("=" * 30)
        
        if isinstance(result, dict):
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Analysis successful!")
                print(f"📝 Candidate ID: {result.get('candidate_id', 'N/A')}")
                print(f"👤 Name: {result.get('first_name', 'N/A')} {result.get('last_name', 'N/A')}")
                print(f"📧 Email: {result.get('email', 'N/A')}")
                print(f"📱 Phone: {result.get('phone', 'N/A')}")
                print(f"📍 Location: {result.get('location', 'N/A')}")
                print(f"💼 Career Level: {result.get('career_level', 'N/A')}")
                print(f"⏱️ Years Experience: {result.get('years_of_experience', 'N/A')}")
                
                skills = result.get('skills', [])
                print(f"🔧 Skills ({len(skills)} found):")
                for skill in skills[:5]:  # Show first 5
                    if isinstance(skill, dict):
                        print(f"   - {skill.get('name', 'N/A')} ({skill.get('category', 'N/A')})")
                    else:
                        print(f"   - {skill}")
                
                work_exp = result.get('work_experience', [])
                print(f"💼 Work Experience ({len(work_exp)} found):")
                for exp in work_exp[:2]:  # Show first 2
                    if isinstance(exp, dict):
                        print(f"   - {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
        else:
            print(f"⚠️ Unexpected result type: {type(result)}")
        
        print(f"\\n🎯 Expected vs Actual:")
        print(f"   Expected Name: Ahmed Mohamed")
        print(f"   Actual Name: {result.get('first_name', 'N/A')} {result.get('last_name', 'N/A')}")
        print(f"   Expected Email: ahmed.mohamed@company.com")
        print(f"   Actual Email: {result.get('email', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_sharepoint_cv())