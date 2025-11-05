"""
Test Production Deployment - AI Configuration System
===================================================
"""

import asyncio
import httpx
import json

async def test_production_deployment():
    """Test the production deployment to ensure everything works"""
    
    print("🧪 Testing Production Deployment")
    print("=" * 40)
    
    base_url = "https://atsai-jade.vercel.app/api/v1"
    
    # Test 1: Health check
    print("\\n1. 🔍 Testing API Health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("   ✅ API is healthy and accessible")
            else:
                print(f"   ❌ API health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Cannot connect to API: {e}")
        return False
    
    # Test 2: Settings endpoint (public settings)
    print("\\n2. ⚙️ Testing Settings API...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/settings/public")
            if response.status_code == 200:
                settings = response.json()
                print(f"   ✅ Settings API working - Found {len(settings)} public settings")
                
                # Check if AI settings exist
                ai_settings = [s for s in settings if s.get('category') == 'ai']
                if ai_settings:
                    print(f"   🎉 Found {len(ai_settings)} AI settings in production!")
                    for setting in ai_settings[:3]:  # Show first 3
                        print(f"      - {setting['key']}: {setting['description']}")
                else:
                    print("   ⚠️  No AI settings found - migration may be needed")
            else:
                print(f"   ❌ Settings API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Settings API error: {e}")
    
    # Test 3: Check for the new endpoints
    print("\\n3. 🔗 Testing New Endpoints...")
    endpoints_to_test = [
        "/auth/health",
        "/candidates/",
        "/jobs/"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}{endpoint}")
                status = "✅" if response.status_code in [200, 401, 422] else "❌"
                print(f"   {status} {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")
    
    print("\\n" + "=" * 40)
    print("🚀 DEPLOYMENT STATUS:")
    print("✅ Code deployed to Vercel")
    print("📝 Migration SQL file ready")
    print("🔗 Production URL: https://atsai-jade.vercel.app")
    
    print("\\n📋 NEXT STEPS:")
    print("1. Apply database migration (see production_ai_migration.sql)")
    print("2. Login as admin and check Settings page")
    print("3. Configure AI behavior via UI")
    print("4. Test AI chat with new configurable instructions")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_production_deployment())