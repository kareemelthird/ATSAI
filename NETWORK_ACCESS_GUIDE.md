# 🌐 Network Access Setup Guide

## Your Network Configuration

**Your Network IP:** `10.0.21.86`

**Backend URL:** `http://10.0.21.86:8000`
**Frontend URL:** `http://10.0.21.86:3000`

---

## ✅ Changes Applied

### 1. Frontend Vite Config
**File:** `frontend/vite.config.ts`
```typescript
server: {
  host: '0.0.0.0', // ✅ Allows network access
  port: 3000,
  ...
}
```

### 2. Frontend Environment
**File:** `frontend/.env`
```bash
VITE_API_URL=http://10.0.21.86:8000  # ✅ Points to network IP
```

### 3. Backend Already Configured
**Command:** Already running with `--host 0.0.0.0 --port 8000` ✅

---

## 🚀 How to Start

### Option 1: Using Tasks (Recommended)
1. Stop any running servers
2. Press `Ctrl+Shift+P` → "Tasks: Run Task"
3. Select "Start ATS Application"
4. Both backend and frontend will start with network access

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## 📱 Accessing from Other Devices

### From Another Computer/Phone on Same Network:

1. **Open browser on the other device**
2. **Navigate to:** `http://10.0.21.86:3000`
3. **Login with your credentials**

### Important Notes:
- ✅ Both devices must be on the **same Wi-Fi network**
- ✅ Windows Firewall must allow connections (see below)
- ✅ Make sure backend is running on port 8000
- ✅ Make sure frontend is running on port 3000

---

## 🛡️ Windows Firewall Setup

You may need to allow these ports through Windows Firewall:

### Method 1: Quick Command (Run as Administrator)
```powershell
# Allow Node.js (Frontend)
New-NetFirewallRule -DisplayName "ATS Frontend (Node.js)" -Direction Inbound -Program "C:\Program Files\nodejs\node.exe" -Action Allow

# Allow Python (Backend)
New-NetFirewallRule -DisplayName "ATS Backend (Python)" -Direction Inbound -Program "C:\Users\karim.hassan\ATS\.venv\Scripts\python.exe" -Action Allow

# Or allow ports directly
New-NetFirewallRule -DisplayName "ATS Backend Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "ATS Frontend Port 3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

### Method 2: Windows Firewall GUI
1. Press `Win + R`, type `wf.msc`, press Enter
2. Click "Inbound Rules" → "New Rule"
3. Select "Port" → Next
4. TCP → Specific local ports: `3000, 8000` → Next
5. Allow the connection → Next
6. Check all profiles → Next
7. Name: "ATS Application" → Finish

---

## 🧪 Testing Network Access

### From Your Computer:
```powershell
# Test backend
curl http://10.0.21.86:8000/api/v1/health

# Test frontend (in browser)
# Open: http://10.0.21.86:3000
```

### From Another Device:
1. Open browser
2. Go to: `http://10.0.21.86:3000`
3. You should see the login page

---

## 📊 Network Access URLs

| Service | Local URL | Network URL |
|---------|-----------|-------------|
| **Frontend** | http://localhost:3000 | http://10.0.21.86:3000 |
| **Backend API** | http://localhost:8000 | http://10.0.21.86:8000 |
| **API Docs** | http://localhost:8000/docs | http://10.0.21.86:8000/docs |

---

## 🔧 Troubleshooting

### Issue: "Can't reach the site" from another device

**Check 1: Is the server running?**
```powershell
# Check if ports are open
netstat -an | Select-String "3000|8000"
```
You should see:
```
TCP    0.0.0.0:3000    LISTENING
TCP    0.0.0.0:8000    LISTENING
```

**Check 2: Can you ping your computer?**
From another device:
```bash
ping 10.0.21.86
```

**Check 3: Windows Firewall**
- Temporarily disable Windows Firewall to test
- If it works, add firewall rules (see above)

**Check 4: Same Network?**
- Both devices must be on the same Wi-Fi/LAN
- Check IP range (should start with same numbers: 10.0.21.x)

### Issue: "API connection error" in frontend

**Fix:** Make sure frontend .env has correct IP:
```bash
VITE_API_URL=http://10.0.21.86:8000
```

Then restart frontend:
```powershell
# Kill frontend
taskkill /F /IM node.exe

# Restart
cd frontend
npm run dev
```

### Issue: Network IP Changed

Your IP can change if you reconnect to Wi-Fi. To check current IP:
```powershell
ipconfig | Select-String "IPv4"
```

Update `frontend/.env` with new IP and restart servers.

---

## 🔒 Security Notes

### Important:
- ⚠️ This setup is for **local network only**
- ⚠️ Don't expose to the internet without proper security
- ⚠️ Use VPN for remote access instead

### For Production:
- Use HTTPS with SSL certificates
- Set up proper authentication
- Use a reverse proxy (nginx)
- Configure CORS properly
- Use environment-specific configs

---

## 📱 Mobile Access Example

### On Your Phone (Same Wi-Fi):
1. Connect to same Wi-Fi as your computer
2. Open browser (Chrome/Safari)
3. Enter: `http://10.0.21.86:3000`
4. Login with your credentials
5. Use the app normally!

---

## 🎯 Quick Start Checklist

- [ ] Stop all running servers
- [ ] Verify `frontend/.env` has network IP: `http://10.0.21.86:8000`
- [ ] Verify `frontend/vite.config.ts` has `host: '0.0.0.0'`
- [ ] Start backend: `--host 0.0.0.0 --port 8000`
- [ ] Start frontend: `npm run dev`
- [ ] Check firewall allows ports 3000 and 8000
- [ ] Test from another device: `http://10.0.21.86:3000`

---

## 🔄 Switching Between Local and Network

### For Local Development Only:
**frontend/.env:**
```bash
VITE_API_URL=http://localhost:8000
```

### For Network Access:
**frontend/.env:**
```bash
VITE_API_URL=http://10.0.21.86:8000
```

**Note:** You need to restart the frontend after changing .env

---

## 💡 Pro Tips

1. **Bookmark the Network URL** on your phone for quick access
2. **Add firewall rules once** - they persist across restarts
3. **Use `ipconfig` regularly** - your IP might change
4. **Test on your computer first** before trying from other devices
5. **Check backend logs** for incoming connections from network

---

## ✅ Success Indicators

You know it's working when:
- ✅ Backend shows: `Uvicorn running on http://0.0.0.0:8000`
- ✅ Frontend shows: `Network: http://10.0.21.86:3000`
- ✅ Another device can load login page
- ✅ You can login and use features from other device

---

## 📞 Need Help?

If you're still having issues:
1. Check Windows Firewall logs
2. Verify both servers are running
3. Test with `curl` or `ping`
4. Check router settings (some routers block inter-device communication)

---

**Status:** ✅ Configuration Complete
**Next Step:** Restart servers and test from another device!
