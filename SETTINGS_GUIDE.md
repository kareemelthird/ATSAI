# ATS System Settings Management Guide

## Overview

The ATS application provides a comprehensive web-based settings management interface that allows administrators to configure system settings without manually editing configuration files. All settings are stored in the `.env` file and can be modified through the admin panel.

## Accessing Settings

1. **Login as Admin**: Only users with `ADMIN` or `SUPER_ADMIN` roles can access settings
2. **Navigate to Settings**: Go to Admin → Settings in the sidebar
3. **Select Category**: Choose from 5 categories (AI Provider, Database, Application, Security, Server)

## Settings Categories

### 1. AI Provider Settings 🤖

Configure AI services for resume analysis and chat features.

| Setting | Description | Example | Requires Restart |
|---------|-------------|---------|------------------|
| `AI_PROVIDER` | Active AI provider (groq/deepseek/openrouter) | `groq` | ✅ Yes |
| `AI_MODEL` | Model name to use | `llama-3.1-8b-instant` | ❌ No |
| `USE_MOCK_AI` | Use mock responses for testing | `false` | ✅ Yes |
| `GROQ_API_KEY` | Groq API key (encrypted) | `gsk_...` | ✅ Yes |
| `GROQ_API_URL` | Groq API endpoint | `https://api.groq.com/openai/v1/chat/completions` | ✅ Yes |
| `DEEPSEEK_API_KEY` | DeepSeek API key (encrypted) | `sk-...` | ✅ Yes |
| `DEEPSEEK_API_URL` | DeepSeek API endpoint | `https://api.deepseek.com/v1/chat/completions` | ✅ Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key (encrypted) | `sk-...` | ✅ Yes |
| `OPENROUTER_API_URL` | OpenRouter API endpoint | `https://openrouter.ai/api/v1/chat/completions` | ✅ Yes |

**Features:**
- **Test Connection**: Click "Test Connection" button to verify AI provider configuration
- Returns response time and model info

### 2. Database Settings 🗄️

Configure PostgreSQL database connection.

| Setting | Description | Example | Requires Restart |
|---------|-------------|---------|------------------|
| `DATABASE_URL` | PostgreSQL connection string (encrypted) | `postgresql://user:pass@localhost:5432/ats` | ✅ Yes |

**Format:**
```
postgresql://[username]:[password]@[host]:[port]/[database]
```

### 3. Application Settings ⚙️

General application configuration.

| Setting | Description | Example | Requires Restart |
|---------|-------------|---------|------------------|
| `PROJECT_NAME` | Application display name | `ATS - AI-Powered Recruitment` | ❌ No |
| `API_V1_STR` | API version prefix | `/api/v1` | ✅ Yes |
| `UPLOAD_DIR` | Resume upload directory | `uploads/resumes` | ❌ No |

### 4. Security Settings 🔒

JWT authentication and CORS configuration.

| Setting | Description | Example | Requires Restart |
|---------|-------------|---------|------------------|
| `SECRET_KEY` | JWT secret key (min 32 chars, encrypted) | `your-super-secret-key-here` | ✅ Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` | ✅ Yes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` | ✅ Yes |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000,https://ats.example.com` | ✅ Yes |

**Security Notes:**
- SECRET_KEY must be at least 32 characters
- Use strong, random keys in production
- Limit ALLOWED_ORIGINS to specific domains in production (avoid `*`)

### 5. Server Settings 🖥️

Server host and port configuration.

| Setting | Description | Example | Requires Restart |
|---------|-------------|---------|------------------|
| `HOST` | Server bind address | `0.0.0.0` | ✅ Yes |
| `PORT` | Server port number | `8000` | ✅ Yes |

## How to Change Settings

### Method 1: Via Web Interface (Recommended)

1. **Navigate to Settings Page**
   - Login as admin user
   - Click "Admin" in sidebar
   - Click "Settings"

2. **Select Category**
   - Click on category tab (AI Provider, Database, etc.)

3. **Edit Value**
   - Click on the input field
   - Enter new value
   - For encrypted fields, existing values show as `***ENCRYPTED***`

4. **Save Setting**
   - Click "Save" button next to the field
   - Success message will appear
   - If "restart required" warning shows, you need to restart the server

5. **Restart Server (if needed)**
   - Click the orange "Restart Server" button in the top-right
   - Confirm the restart dialog
   - Server will restart automatically
   - Page will reload after restart completes

### Method 2: Manual .env File Edit

1. **Locate .env file**
   ```
   C:\Users\karim.hassan\ATS\backend\.env
   ```

2. **Edit with text editor**
   ```bash
   AI_PROVIDER=groq
   GROQ_API_KEY=gsk_your_key_here
   AI_MODEL=llama-3.1-8b-instant
   ```

3. **Restart server**
   - Stop backend: `Ctrl+C` in terminal
   - Start backend: Run task "Start Backend"

## Examples

### Example 1: Switching AI Provider from Groq to DeepSeek

1. Go to Settings → AI Provider
2. Change `AI_PROVIDER` from `groq` to `deepseek`
3. Update `DEEPSEEK_API_KEY` with your DeepSeek API key
4. Update `AI_MODEL` to `deepseek-chat` or appropriate model
5. Click "Test Connection" to verify
6. Click "Save" on each modified setting
7. Click "Restart Server" button
8. Wait for server to restart

### Example 2: Changing JWT Token Expiry

1. Go to Settings → Security
2. Change `ACCESS_TOKEN_EXPIRE_MINUTES` from `30` to `60`
3. Click "Save"
4. Click "Restart Server" (required for security settings)

### Example 3: Updating CORS Origins for Production

1. Go to Settings → Security
2. Change `ALLOWED_ORIGINS` from:
   ```
   *
   ```
   to:
   ```
   https://ats.example.com,https://www.ats.example.com
   ```
3. Click "Save"
4. Click "Restart Server"

### Example 4: Testing AI Connection

1. Go to Settings → AI Provider
2. Ensure `AI_PROVIDER`, API key, and model are set
3. Click "Test Connection" button
4. Results show:
   - ✅ **Success**: Connection time, model response
   - ❌ **Failed**: Error message with details

**Note**: The test connection will automatically use the stored API key from your .env file if you haven't changed it in the form. This allows you to test your current configuration without exposing the actual API key value.

## System Restart Feature

### Web-Based Restart

The system provides a convenient restart button in the Settings page:

**Location**: Top-right corner of Settings page

**Button**: Orange "Restart Server" button with power icon

**Process**:
1. Click "Restart Server"
2. Confirm restart dialog
3. Server initiates graceful restart
4. Frontend shows progress messages:
   - "Server restart initiated..."
   - "Server is restarting..."
   - "Server restarted successfully!"
5. Page automatically reloads after restart

**How It Works**:
- Backend endpoint: `POST /api/v1/settings/restart-server`
- Logs audit trail of restart request
- Touches `main.py` file to trigger uvicorn auto-reload
- Only works when server runs with `--reload` flag

### When to Restart

Restart is **required** after changing:
- ✅ AI Provider settings (provider, API keys, URLs)
- ✅ Database connection
- ✅ Security settings (SECRET_KEY, token expiry, CORS)
- ✅ Server settings (host, port)
- ✅ API version path

Restart is **not required** after changing:
- ❌ AI Model (if provider stays same)
- ❌ Project Name
- ❌ Upload Directory

### Production Considerations

**Development Mode** (Current):
- Uses `uvicorn --reload`
- Restart by touching main.py
- Works with web-based restart button

**Production Mode** (Recommended):
- Use process manager: systemd, supervisor, or pm2
- Restart via process manager commands:
  ```bash
  # systemd
  sudo systemctl restart ats-backend
  
  # supervisor
  supervisorctl restart ats-backend
  
  # pm2
  pm2 restart ats-backend
  ```

- Disable web restart or integrate with process manager API

## Security Features

### Encrypted Values
- API keys and secrets are encrypted in database
- Displayed as `***ENCRYPTED***` in UI
- Original values hidden for security

### Audit Logging
- All setting changes logged to `audit_logs` table
- Tracks: user, timestamp, old/new values, IP address
- Server restarts also logged

### Role-Based Access
- Only ADMIN and SUPER_ADMIN can access settings
- Regular users get 403 Forbidden error

## API Endpoints

For programmatic access or custom integrations:

### Get All Settings
```http
GET /api/v1/settings/
Authorization: Bearer <admin_token>
```

### Get Settings by Category
```http
GET /api/v1/settings/{category}
Authorization: Bearer <admin_token>
```

### Update Setting
```http
PUT /api/v1/settings/{key}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "value": "new_value"
}
```

### Test AI Connection
```http
POST /api/v1/settings/test-ai-connection
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "provider": "groq",
  "api_key": "gsk_...",
  "model": "llama-3.1-8b-instant"
}
```

### Restart Server
```http
POST /api/v1/settings/restart-server
Authorization: Bearer <admin_token>
```

### Get Categories
```http
GET /api/v1/settings/categories/list
Authorization: Bearer <admin_token>
```

## Troubleshooting

### Settings Not Saving
- **Check**: Are you logged in as admin?
- **Check**: Is backend server running?
- **Check**: Does `.env` file have write permissions?
- **Solution**: Check browser console for errors

### AI Connection Test Fails
- **Check**: Is API key correct?
- **Check**: Is provider URL correct?
- **Check**: Do you have internet connection?
- **Check**: Is API key valid and not expired?
- **Error 401 Invalid API Key**: The system now automatically uses stored credentials from .env file. If you see this error, the API key in your .env file may be invalid or expired.
- **Solution**: Generate new API key from provider, update in Settings, and save

### Server Won't Restart
- **Check**: Is server running with `--reload` flag?
- **Check**: Check backend terminal for errors
- **Solution**: Manually restart from terminal if needed

### Changes Not Taking Effect
- **Check**: Did you click "Save" button?
- **Check**: Did you restart server if required?
- **Check**: Did you wait for restart to complete?
- **Solution**: Check if setting has "restart required" flag

## Best Practices

1. **Test Before Saving**: Use "Test Connection" for AI settings
2. **Backup .env**: Keep backup before major changes
3. **Restart After Changes**: Always restart when indicated
4. **Use Strong Keys**: Generate random SECRET_KEY (32+ chars)
5. **Limit CORS**: Restrict origins in production
6. **Monitor Audit Logs**: Review setting changes regularly
7. **Document Changes**: Note reason for configuration changes

## Environment File Location

**Backend .env file**:
```
C:\Users\karim.hassan\ATS\backend\.env
```

**Frontend (if needed)**:
```
C:\Users\karim.hassan\ATS\frontend\.env
```

## Additional Resources

- **Groq API**: https://console.groq.com/
- **DeepSeek API**: https://platform.deepseek.com/
- **OpenRouter API**: https://openrouter.ai/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
