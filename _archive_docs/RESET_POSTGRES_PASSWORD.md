# Reset PostgreSQL Password on Windows

## Method 1: Using pg_hba.conf (Recommended)

### Step 1: Locate pg_hba.conf file
The file is usually located at:
```
C:\Program Files\PostgreSQL\17\data\pg_hba.conf
```

### Step 2: Backup the original file
Copy `pg_hba.conf` to `pg_hba.conf.backup`

### Step 3: Edit pg_hba.conf
Open `pg_hba.conf` in a text editor **as Administrator**

Find the lines that look like:
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256
# IPv6 local connections:
host    all             all             ::1/128                 scram-sha-256
```

Change `scram-sha-256` to `trust` (temporarily):
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
```

### Step 4: Restart PostgreSQL service
Open PowerShell **as Administrator** and run:
```powershell
Restart-Service postgresql-x64-17
```

Or use Services:
1. Press `Win + R`, type `services.msc`
2. Find "postgresql-x64-17" service
3. Right-click → Restart

### Step 5: Connect without password
```powershell
cd "C:\Program Files\PostgreSQL\17\bin"
.\psql.exe -U postgres
```

### Step 6: Reset the password
Once connected, run:
```sql
ALTER USER postgres WITH PASSWORD 'your_new_password';
ALTER USER k3admin WITH PASSWORD 'KH@123456';
\q
```

### Step 7: Restore security
1. Edit `pg_hba.conf` again
2. Change `trust` back to `scram-sha-256`
3. Restart PostgreSQL service again

### Step 8: Create the database
```powershell
cd "C:\Program Files\PostgreSQL\17\bin"
.\psql.exe -U postgres -c "CREATE DATABASE ats_db OWNER k3admin;"
```

---

## Method 2: Reinstall (If Method 1 doesn't work)

### Option A: Repair Installation
1. Go to Control Panel → Programs → Uninstall a program
2. Find PostgreSQL 17
3. Right-click → Change/Modify
4. Choose "Repair"
5. Set a new password during repair

### Option B: Complete Reinstall
1. Uninstall PostgreSQL completely
2. Delete data folder: `C:\Program Files\PostgreSQL\17\data`
3. Reinstall PostgreSQL
4. Set new password during installation
5. Create k3admin user and ats_db database

---

## Quick Commands After Password Reset

### Create k3admin user (if doesn't exist):
```sql
CREATE USER k3admin WITH PASSWORD 'KH@123456';
ALTER USER k3admin CREATEDB;
```

### Create database:
```sql
CREATE DATABASE ats_db OWNER k3admin;
```

### Test connection:
```powershell
cd "C:\Program Files\PostgreSQL\17\bin"
.\psql.exe -U k3admin -d ats_db
```

---

## After Database is Created

Run the table creation script:
```powershell
cd C:\Users\karim.hassan\ATS\backend
C:\Users\karim.hassan\ATS\.venv\Scripts\python.exe create_tables.py
```

Then restart the backend server (if needed):
```powershell
cd C:\Users\karim.hassan\ATS\backend
C:\Users\karim.hassan\ATS\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
