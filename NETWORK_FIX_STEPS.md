# 🚨 Network Access - Manual Fix Steps

## Current Issue
Frontend is still trying to connect to `localhost:8000` instead of `10.0.21.86:8000` when accessed from other devices.

## ✅ Root Cause
The frontend `.env` file is correct (`VITE_API_URL=http://10.0.21.86:8000`), but Vite needs to be completely restarted to pick up the change.

---

## 🔧 Fix Steps (Do This Now)

### Step 1: Stop All Servers
Open PowerShell and run:
```powershell
cd C:\Users\karim.hassan\ATS
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

### Step 2: Start Backend (Terminal 1)
Open a NEW PowerShell terminal:
```powershell
cd C:\Users\karim.hassan\ATS\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait until you see: `Uvicorn running on http://0.0.0.0:8000`

### Step 3: Start Frontend (Terminal 2)
Open ANOTHER NEW PowerShell terminal:
```powershell
cd C:\Users\karim.hassan\ATS\frontend
npm run dev
```

Wait until you see:
```
➜  Local:   http://localhost:3000/
➜  Network: http://10.0.21.86:3000/
```

### Step 4: Test
**From your computer:**
- Open: `http://localhost:3000`
- Should work ✅

**From another device (phone/laptop on same Wi-Fi):**
- Open: `http://10.0.21.86:3000`
- Should work ✅

---

## 🔍 Verify Configuration

### Check Frontend .env
```powershell
cat C:\Users\karim.hassan\ATS\frontend\.env
```

Should show:
```
VITE_API_URL=http://10.0.21.86:8000
```

### Check Network Ports
```powershell
netstat -an | Select-String "3000|8000"
```

Should show:
```
TCP    0.0.0.0:3000    LISTENING
TCP    0.0.0.0:8000    LISTENING
```

---

## 🐛 If Still Not Working

### Issue: Connection Refused from Other Device

**Check 1: Firewall**
Run PowerShell **as Administrator**:
```powershell
cd C:\Users\karim.hassan\ATS
.\add-firewall-rules.ps1
```

**Check 2: Can you ping your computer?**
From another device:
```
ping 10.0.21.86
```

If it fails, Windows Firewall is blocking.

**Check 3: Backend accessible?**
From another device's browser:
```
http://10.0.21.86:8000/docs
```

Should show FastAPI documentation page.

**Check 4: Frontend accessible?**
From another device's browser:
```
http://10.0.21.86:3000
```

Should show login page.

---

## 📝 Important Notes

### Why Restart is Needed
- Vite (frontend) reads `.env` files **only at startup**
- Changing `.env` while Vite is running has NO effect
- Must **completely stop** and **restart** Vite

### Why localhost Doesn't Work on Network
- When you access `http://10.0.21.86:3000` from another device
- `localhost` in that context means the OTHER device, not your computer
- That's why we changed `.env` to use `10.0.21.86:8000`

### Browser Cache
- If it still shows old error, clear browser cache
- Or open in Incognito/Private mode
- Or hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

---

## 🎯 Expected Behavior

### From Your Computer:
```
Open: http://localhost:3000
API calls go to: http://10.0.21.86:8000
Result: ✅ Works
```

### From Other Device:
```
Open: http://10.0.21.86:3000
API calls go to: http://10.0.21.86:8000
Result: ✅ Works
```

---

## 🔄 Alternative: Use start.ps1

You can also use the startup script:
```powershell
cd C:\Users\karim.hassan\ATS
.\start.ps1
```

This will:
1. Check prerequisites
2. Start backend in new window
3. Start frontend in new window
4. Show you the URLs to access

---

## ✅ Success Indicators

You'll know it's working when:

1. **Backend terminal shows:**
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. **Frontend terminal shows:**
   ```
   ➜  Network: http://10.0.21.86:3000/
   ```

3. **From another device:**
   - Can open `http://10.0.21.86:3000`
   - Can login without "Network Error"
   - Can use all features

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Network Error" when logging in | Restart frontend (Step 3) |
| Can't access from other device | Run firewall script |
| Port 3000 in use | Kill node: `taskkill /F /IM node.exe` |
| Port 8000 in use | Kill python: `taskkill /F /IM python.exe` |
| Wrong IP address | Update `frontend/.env` with correct IP |

---

**Next Step:** Follow Step 1-4 above to restart both servers properly! 🚀
