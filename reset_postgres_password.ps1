# PostgreSQL Password Reset Script for Windows
# Run this script as Administrator

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "PostgreSQL Password Reset Utility" -ForegroundColor Yellow
Write-Host ("=" * 71) -ForegroundColor Cyan
Write-Host ""

$pgDataPath = "C:\Program Files\PostgreSQL\17\data"
$pgHbaPath = "$pgDataPath\pg_hba.conf"
$pgHbaBackup = "$pgDataPath\pg_hba.conf.backup"
$serviceName = "postgresql-x64-17"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Step 1: Backing up pg_hba.conf..." -ForegroundColor Green
try {
    Copy-Item $pgHbaPath $pgHbaBackup -Force
    Write-Host "  Backup created successfully" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: Could not backup file: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Modifying pg_hba.conf to allow passwordless access..." -ForegroundColor Green
try {
    $content = Get-Content $pgHbaPath
    $newContent = $content -replace 'scram-sha-256', 'trust' -replace 'md5', 'trust'
    $newContent | Set-Content $pgHbaPath
    Write-Host "  Configuration updated" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: Could not modify file: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Restarting PostgreSQL service..." -ForegroundColor Green
try {
    Restart-Service $serviceName -Force
    Start-Sleep -Seconds 3
    Write-Host "  Service restarted successfully" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: Could not restart service: $_" -ForegroundColor Red
    Write-Host "  Try manually: services.msc -> postgresql-x64-17 -> Restart" -ForegroundColor Yellow
    Read-Host "Press Enter after you've restarted the service manually"
}

Write-Host ""
Write-Host "Step 4: Resetting passwords..." -ForegroundColor Green
Write-Host ""
Write-Host "Enter new password for 'postgres' superuser:" -ForegroundColor Yellow
$postgresPassword = Read-Host -AsSecureString
$postgresPasswordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))

Write-Host ""
Write-Host "Connecting to PostgreSQL..." -ForegroundColor Gray

$psqlPath = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
$sqlCommands = @"
ALTER USER postgres WITH PASSWORD '$postgresPasswordText';
ALTER USER k3admin WITH PASSWORD 'KH@123456';
CREATE DATABASE ats_db OWNER k3admin;
\q
"@

$sqlCommands | & $psqlPath -U postgres 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Passwords reset successfully!" -ForegroundColor Gray
    Write-Host "  Database 'ats_db' created!" -ForegroundColor Gray
} else {
    Write-Host "  Note: Some commands may have failed if user/database already exists" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 5: Restoring security settings..." -ForegroundColor Green
try {
    Copy-Item $pgHbaBackup $pgHbaPath -Force
    Write-Host "  Security restored" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: Could not restore settings: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 6: Restarting PostgreSQL service again..." -ForegroundColor Green
try {
    Restart-Service $serviceName -Force
    Start-Sleep -Seconds 3
    Write-Host "  Service restarted" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: Could not restart service: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("=" * 71) -ForegroundColor Cyan
Write-Host "Password Reset Complete!" -ForegroundColor Green
Write-Host ("=" * 71) -ForegroundColor Cyan
Write-Host ""
Write-Host "Credentials:" -ForegroundColor Yellow
Write-Host "  Postgres superuser: postgres / [your new password]" -ForegroundColor Gray
Write-Host "  Application user:   k3admin / KH@123456" -ForegroundColor Gray
Write-Host "  Database:           ats_db" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run create_tables.py to create database tables" -ForegroundColor Gray
Write-Host "  2. Start your backend server" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
