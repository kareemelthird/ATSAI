#!/usr/bin/env python3

# Debug email extraction from CV text
import sys
sys.path.append("./backend")

def debug_email_extraction():
    cv_text = """Ahmed Mohamed
Senior SharePoint Developer

Contact Information:
Email: ahmed.mohamed@company.com
Phone: +20-123-456-7890
Location: Cairo, Egypt
LinkedIn: linkedin.com/in/ahmed-mohamed

Professional Summary:
Experienced SharePoint Developer with 5+ years of expertise in SharePoint Online, Power Platform, and modern web technologies."""

    prompt = f"""Analyze the following resume/CV text and extract information:

{cv_text}

Return the extracted information in JSON format."""
    
    print("🔍 Debugging email extraction from CV text")
    print("=" * 60)
    
    extracted_email = "john.smith@email.com"
    
    lines = prompt.split('\n')
    print(f"\n📋 Processing {len(lines)} lines for email:")
    
    for i, line in enumerate(lines):
        line = line.strip()
        print(f"Line {i:2d}: '{line}'")
        
        # Look for email
        if '@' in line and '.com' in line:
            print(f"        ✅ Found email candidate: {line}")
            email_match = line.split()
            print(f"        Words: {email_match}")
            for word in email_match:
                print(f"        Checking word: '{word}'")
                if '@' in word and '.com' in word:
                    extracted_email = word.strip(':').strip()
                    print(f"        ✅ EXTRACTED EMAIL: {extracted_email}")
                    break
    
    print(f"\n🎯 Final email: {extracted_email}")

if __name__ == "__main__":
    debug_email_extraction()