#!/usr/bin/env python3

# Debug name extraction from CV text
import sys
sys.path.append("./backend")

def debug_name_extraction():
    # Simulate the CV text that would be sent to the AI service
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

    print("🔍 Debugging name extraction from CV text")
    print("=" * 60)
    print(f"CV text length: {len(cv_text)} characters")
    print("\n📄 CV Text:")
    print(cv_text)
    print("\n" + "=" * 60)
    
    # Simulate the parsing logic
    prompt = f"""Analyze the following resume/CV text and extract information:

{cv_text}

Return the extracted information in JSON format."""
    
    print("🔧 Simulating name extraction logic...")
    print("=" * 40)
    
    extracted_name = "John"
    extracted_lastname = "Smith"
    extracted_email = "john.smith@email.com"
    extracted_phone = "+1-555-123-4567"
    
    # Simple extraction from prompt text
    lines = prompt.split('\n')
    print(f"\n📋 Processing {len(lines)} lines:")
    
    for i, line in enumerate(lines):
        line = line.strip()
        print(f"Line {i:2d}: '{line}' (length: {len(line)})")
        
        if line and len(line) < 50:  # Likely name line
            words = line.split()
            print(f"        Words: {words} (count: {len(words)})")
            
            if len(words) >= 2 and len(words) <= 4:
                # Check if it looks like a name (not email, phone, title)
                has_excluded_chars = any(char in line.lower() for char in ['@', '.com', '+', '(', ')', 'email:', 'phone:', 'developer', 'engineer', 'manager'])
                starts_with_excluded = line.lower().startswith(('analyze', 'extract', 'return'))
                
                print(f"        Has excluded chars: {has_excluded_chars}")
                print(f"        Starts with excluded: {starts_with_excluded}")
                
                if not has_excluded_chars and not starts_with_excluded:
                    print(f"        ✅ FOUND NAME: {words[0]} {' '.join(words[1:])}")
                    extracted_name = words[0]
                    extracted_lastname = ' '.join(words[1:]) if len(words) > 1 else ""
                    break
                else:
                    print(f"        ❌ Excluded as name")
            else:
                print(f"        ❌ Wrong word count")
        else:
            if line:
                print(f"        ❌ Too long ({len(line)} chars)")
    
    print("\n🎯 Final extraction results:")
    print(f"Name: {extracted_name}")
    print(f"Last Name: {extracted_lastname}")
    print(f"Email: {extracted_email}")
    print(f"Phone: {extracted_phone}")

if __name__ == "__main__":
    debug_name_extraction()