# Settings System Fix - Using Stored Credentials

## Problem

When clicking "Test Connection" in the Settings page, users were getting a **401 Invalid API Key** error because:

1. The settings page loads API keys as `***ENCRYPTED***` for security
2. When testing the connection, the system was trying to use the masked value `***ENCRYPTED***` instead of the actual API key
3. The AI provider rejected this invalid key with HTTP 401 error

## Solution

Implemented **automatic stored credential loading** for the test connection feature.

### Frontend Changes (`Settings.tsx`)

**Before:**
```typescript
const handleTestAIConnection = async () => {
  const apiKey = editedValues[`${provider.toUpperCase()}_API_KEY`] || '';
  
  const response = await axios.post(`${API_URL}/settings/test-ai-connection`, {
    provider,
    api_key: apiKey,  // Sends '***ENCRYPTED***' which fails
    model
  });
}
```

**After:**
```typescript
const handleTestAIConnection = async () => {
  const apiKey = editedValues[`${provider.toUpperCase()}_API_KEY`] || '';
  
  // Check if API key is the masked value or empty
  const useStoredKey = !apiKey || apiKey === '***ENCRYPTED***';
  
  const response = await axios.post(`${API_URL}/settings/test-ai-connection`, {
    provider,
    api_key: useStoredKey ? undefined : apiKey,  // Don't send masked value
    model,
    use_stored_credentials: useStoredKey  // Tell backend to use .env value
  });
}
```

### Backend Changes (`settings.py`)

**Updated Request Model:**
```python
class TestAIConnectionRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None  # Now optional
    model: str
    use_stored_credentials: bool = False  # New flag
```

**Updated Endpoint Logic:**
```python
@router.post("/test-ai-connection")
async def test_ai_connection(request: TestAIConnectionRequest, ...):
    # Determine which API key to use
    api_key = request.api_key
    
    if request.use_stored_credentials or not api_key:
        # Load API key from .env file
        env_vars = read_env_file()
        api_key_name = f"{request.provider.upper()}_API_KEY"
        api_key = env_vars.get(api_key_name)
        
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail=f"No API key found for {request.provider}"
            )
    
    # Test connection with actual API key
    headers = {"Authorization": f"Bearer {api_key}"}
    # ... rest of test logic
```

**Improved Error Messages:**
```python
except httpx.HTTPStatusError as e:
    error_detail = e.response.text
    try:
        error_json = e.response.json()
        if "error" in error_json:
            error_detail = error_json["error"].get("message", error_detail)
    except:
        pass
    
    return TestAIConnectionResponse(
        success=False,
        message=f"HTTP Error {e.response.status_code}: {error_detail}"
    )
```

## How It Works Now

### Scenario 1: Testing with Stored Credentials (Default)

1. User navigates to Settings → AI Provider
2. API key field shows `***ENCRYPTED***` (masked for security)
3. User clicks "Test Connection"
4. Frontend detects masked value
5. Frontend sends `use_stored_credentials: true`
6. Backend reads actual API key from `.env` file
7. Backend tests connection with real key
8. ✅ Success - shows response time and model info

### Scenario 2: Testing with New API Key

1. User navigates to Settings → AI Provider
2. User types new API key in the field: `gsk_newkey123...`
3. User clicks "Test Connection"
4. Frontend detects real value (not masked)
5. Frontend sends `use_stored_credentials: false` with new key
6. Backend tests connection with provided key
7. ✅ Success or ❌ Failure based on key validity

### Scenario 3: No API Key Configured

1. User navigates to Settings → AI Provider
2. API key field is empty
3. User clicks "Test Connection"
4. Frontend sends `use_stored_credentials: true`
5. Backend tries to read from `.env`
6. Backend finds no key
7. ❌ Returns error: "No API key found for groq. Please configure GROQ_API_KEY in settings."

## Benefits

### 🔒 Security
- API keys remain masked in UI
- No need to re-enter keys for testing
- Original keys never exposed to frontend

### ✅ User Experience
- "Test Connection" works without re-entering credentials
- Can test current configuration easily
- Can test new keys before saving

### 🔧 Flexibility
- Supports testing with stored credentials
- Supports testing with new credentials
- Clear error messages for missing keys

## Testing the Fix

### Test 1: Test with Current Groq Configuration
```
1. Go to http://localhost:3000/admin/settings
2. Click "AI Provider" tab
3. Verify AI_PROVIDER shows: groq
4. Verify GROQ_API_KEY shows: ***ENCRYPTED***
5. Click "Test Connection"
6. Should see: "Successfully connected to groq" with response time
```

### Test 2: Test with New API Key
```
1. Go to Settings → AI Provider
2. Clear GROQ_API_KEY field
3. Enter new API key: gsk_...
4. Click "Test Connection"
5. Should test with new key (success or failure based on validity)
6. Don't save - just testing
```

### Test 3: Switch to DeepSeek
```
1. Go to Settings → AI Provider
2. Change AI_PROVIDER to: deepseek
3. Change AI_MODEL to: deepseek-chat
4. Click "Test Connection"
5. Should use stored DEEPSEEK_API_KEY from .env
6. Should show: "Successfully connected to deepseek"
```

## Your Current Configuration

Based on your `.env` file:

```bash
AI_PROVIDER=groq
AI_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

You have:
- ✅ Groq API key configured
- ✅ DeepSeek API key configured
- ✅ Using Groq as active provider
- ✅ Model: llama-3.3-70b-versatile

## Next Steps

1. **Test the fix**: Navigate to Settings and click "Test Connection"
2. **Should work**: Now uses actual stored API key from .env
3. **Try switching providers**: Test DeepSeek connection too
4. **Use restart button**: After any changes that need restart

## Files Modified

1. **Frontend**: `frontend/src/pages/admin/Settings.tsx`
   - Updated `handleTestAIConnection()` to detect masked values
   - Sends `use_stored_credentials` flag to backend

2. **Backend**: `backend/app/api/v1/endpoints/settings.py`
   - Updated `TestAIConnectionRequest` model with optional api_key
   - Added `use_stored_credentials` flag
   - Loads API key from .env when flag is true
   - Improved error message extraction

3. **Documentation**: `SETTINGS_GUIDE.md`
   - Added note about automatic credential loading
   - Added troubleshooting for 401 errors

## Summary

The settings system now intelligently handles API key testing:
- **Masked values** → Use stored credentials from .env
- **New values** → Test with provided credentials
- **Empty values** → Use stored credentials or show error

This provides the best of both worlds: security (keys stay hidden) and usability (testing works out of the box).
