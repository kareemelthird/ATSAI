"""
Debug CV Analysis Issue
======================

Test the CV analysis functionality to see why name and skills are showing as "Unknown" and "N/A"
"""

import sys
from pathlib import Path
import asyncio
import json

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

from app.db.database import SessionLocal
from app.services.ai_service import analyze_resume, get_ai_setting

async def test_cv_analysis():
    """Test CV analysis with sample resume text"""
    
    print("🧪 Testing CV Analysis Functionality")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Check if AI settings exist
        print("1. 🔍 Checking AI Settings...")
        
        ai_resume_instructions = get_ai_setting(db, "ai_resume_analysis_instructions")
        if ai_resume_instructions:
            print(f"   ✅ Found AI resume analysis instructions: {len(ai_resume_instructions)} characters")
        else:
            print("   ❌ No AI resume analysis instructions found!")
            print("   💡 You need to apply the database migration first!")
            return
        
        # Sample resume text for testing
        sample_resume = """
        John Smith
        Software Engineer
        
        Email: john.smith@email.com
        Phone: +1-555-123-4567
        Location: New York, NY
        LinkedIn: linkedin.com/in/johnsmith
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5+ years of expertise in Python, JavaScript, and React development.
        
        SKILLS
        - Python (Expert)
        - JavaScript (Advanced) 
        - React (Advanced)
        - PostgreSQL (Intermediate)
        - AWS (Intermediate)
        - Problem Solving (Expert)
        - Team Leadership (Advanced)
        
        WORK EXPERIENCE
        
        Senior Software Engineer | TechCorp Inc | Jan 2020 - Present
        • Led development of web applications using React and Python
        • Managed team of 3 junior developers
        • Improved system performance by 40%
        • Technologies: Python, React, PostgreSQL, AWS
        
        Software Engineer | StartupXYZ | Jun 2018 - Dec 2019
        • Developed and maintained web applications
        • Collaborated with cross-functional teams
        • Technologies: JavaScript, Node.js, MongoDB
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology | 2018
        GPA: 3.8/4.0
        """
        
        print("\\n2. 🤖 Testing AI Analysis...")
        print(f"   Sample resume length: {len(sample_resume)} characters")
        
        # Test the analysis
        try:
            result = await analyze_resume(sample_resume, None, db, current_user=None)
            
            print("\\n3. 📊 Analysis Results:")
            print("   " + "=" * 30)
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
                return
            
            # Show key extracted information
            if isinstance(result, dict):
                print(f"   ✅ Analysis completed successfully!")
                print(f"   📝 Keys found: {list(result.keys())}")
                
                # Check critical fields
                critical_fields = ['first_name', 'last_name', 'email', 'skills']
                for field in critical_fields:
                    if field in result:
                        value = result[field]
                        if field == 'skills' and isinstance(value, list):
                            print(f"   {field}: {len(value)} skills found")
                            for skill in value[:3]:  # Show first 3 skills
                                print(f"      - {skill}")
                        else:
                            print(f"   {field}: {value}")
                    else:
                        print(f"   ❌ Missing: {field}")
            else:
                print(f"   ⚠️ Unexpected result type: {type(result)}")
                print(f"   Raw result: {result}")
                
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            print(f"   Error type: {type(e)}")
            import traceback
            traceback.print_exc()
        
        print("\\n4. 🔧 Debugging Tips:")
        print("   - Check if database migration was applied")
        print("   - Verify AI API key is configured")
        print("   - Check network connectivity")
        print("   - Review AI service logs for errors")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_cv_analysis())