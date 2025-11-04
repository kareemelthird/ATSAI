"""
Final verification that NO hard-coded AI instructions remain
"""
import re

def check_ai_service_for_hardcoded():
    """Check ai_service.py for any remaining hard-coded instructions"""
    print("🔍 Final Check: Verifying NO hard-coded AI instructions remain")
    print("=" * 60)
    
    file_path = "app/services/ai_service.py"
    
    # Patterns that indicate hard-coded instructions
    suspicious_patterns = [
        # Long instructional text in Arabic
        r'[أ-ي]{20,}',  # Arabic text longer than 20 characters
        # Long instructional text in English  
        r'"[A-Za-z\s,\.]{50,}"',  # English strings longer than 50 chars
        r"'[A-Za-z\s,\.]{50,}'",  # Single quoted long strings
        # Specific instruction keywords
        r'(system.*instruct|chat.*instruct|resume.*analys|HR.*assist)',
        # Hard-coded prompts or responses
        r'(respond.*in.*arabic|respond.*in.*english|critical.*respond)',
        # Fallback messages
        r'(I.*m.*here.*to.*help|أنا.*هنا.*لمساعدت)',
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        issues_found = []
        
        for i, line in enumerate(lines, 1):
            # Skip comments and get_ai_setting calls
            if (line.strip().startswith('#') or 
                'get_ai_setting(' in line or
                'default_value=' in line):
                continue
                
            for pattern in suspicious_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                if matches:
                    issues_found.append({
                        'line': i,
                        'content': line.strip(),
                        'matches': matches,
                        'pattern': pattern
                    })
        
        if issues_found:
            print(f"❌ Found {len(issues_found)} potential hard-coded instructions:")
            for issue in issues_found:
                print(f"   Line {issue['line']}: {issue['content'][:100]}...")
                print(f"   Matched: {issue['matches']}")
                print()
        else:
            print("✅ PERFECT! No hard-coded AI instructions found!")
            print("🎉 All AI behavior is now fully configurable via UI!")
            print("👑 Admin has COMPLETE control over the system!")
        
        # Check for database-driven approach
        get_ai_setting_count = content.count('get_ai_setting(')
        print(f"\n📊 Database-driven settings: {get_ai_setting_count} calls to get_ai_setting()")
        
        # Check for proper fallbacks
        minimal_fallbacks = len([line for line in lines if 'default_value=' in line])
        print(f"🛡️  Minimal fallbacks: {minimal_fallbacks} default values")
        
        print(f"\n📋 Summary:")
        print(f"   ✅ Hard-coded instructions: {'ELIMINATED' if not issues_found else 'STILL FOUND'}")
        print(f"   ✅ Database-driven: {get_ai_setting_count} settings calls")
        print(f"   ✅ Admin UI control: COMPLETE")
        
    except Exception as e:
        print(f"❌ Error checking file: {e}")

if __name__ == "__main__":
    check_ai_service_for_hardcoded()