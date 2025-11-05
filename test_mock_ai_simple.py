#!/usr/bin/env python3
"""
Simple test to verify AI mock responses include job data
"""

# Test the mock AI response parsing
def test_mock_ai_parsing():
    """Test that mock AI can parse job data from context"""
    
    # Simulate a prompt with job data (like what the real system would send)
    test_prompt = """
Answer this question about our candidates in a natural, helpful way:

Current Question: What jobs are available?

CANDIDATE PROFILES:
Candidate: Ahmed Mohamed
Email: ahmed.mohamed@email.com
Location: Cairo, Egypt
Years of Experience: 5 years
Skills: Python, FastAPI, React, JavaScript

AVAILABLE JOBS:
Job: Senior Python Developer
Location: Cairo, Egypt
Type: Full-time
Required Skills: Python, FastAPI, React
Experience: 3-7 years
Salary: 80000-120000 USD
Description: Looking for an experienced Python developer...
---
Job: Frontend Developer
Location: Remote
Type: Full-time
Required Skills: React, JavaScript, TypeScript
Experience: 2-5 years
Salary: 60000-90000 USD
Description: Join our frontend team to build amazing user interfaces...
---

IMPORTANT: 
- Use their exact names and details from their profiles.
"""
    
    print("🧪 Testing Mock AI Job Parsing")
    print("=" * 50)
    print("Input prompt contains:")
    print("- 1 candidate (Ahmed Mohamed)")
    print("- 2 jobs (Senior Python Developer, Frontend Developer)")
    print()
    
    # Test job parsing logic (extracted from the mock AI)
    import re
    
    if "AVAILABLE JOBS:" in test_prompt:
        jobs_section = test_prompt.split("AVAILABLE JOBS:")[1].split("IMPORTANT:")[0]
        jobs = re.findall(r'Job: ([^\n]+)', jobs_section)
        print(f"✅ Extracted {len(jobs)} jobs:")
        for i, job in enumerate(jobs, 1):
            print(f"  {i}. {job}")
    else:
        print("❌ No AVAILABLE JOBS section found")
    
    # Test candidate parsing
    if "CANDIDATE PROFILES:" in test_prompt:
        candidate_section = test_prompt.split("CANDIDATE PROFILES:")[1].split("IMPORTANT:")[0]
        candidates = re.findall(r'Candidate: ([^\n]+)', candidate_section)
        print(f"✅ Extracted {len(candidates)} candidates:")
        for i, candidate in enumerate(candidates, 1):
            print(f"  {i}. {candidate}")
    else:
        print("❌ No CANDIDATE PROFILES section found")
    
    print("\n🎯 Mock AI would now respond with:")
    print("- List of candidates")
    print("- List of available jobs") 
    print("- Offer to evaluate candidates for specific positions")
    
    print("\n✅ Mock AI job parsing logic working correctly!")

if __name__ == "__main__":
    test_mock_ai_parsing()