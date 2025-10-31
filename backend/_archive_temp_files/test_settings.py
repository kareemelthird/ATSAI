import os
import sys
sys.path.append(r'C:\Users\karim.hassan\ATS\backend')
os.environ['PYTHONPATH'] = r'C:\Users\karim.hassan\ATS\backend'

from app.api.v1.endpoints.settings import get_all_settings_definitions

settings = get_all_settings_definitions()
print(f"Total settings: {len(settings)}")
print("\nInstruction-related settings:")
for s in settings:
    if 'instruction' in s['key'].lower():
        print(f"- {s['key']} ({s['data_type']}) - {s['label']}")

print("\nAll settings keys:")
for s in settings:
    print(f"- {s['key']} ({s['data_type']})")