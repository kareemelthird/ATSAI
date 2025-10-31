# Add Windows Firewall Rules for ATS Application
# Run this script as Administrator

Write-Host "🛡️ Adding Windows Firewall Rules for ATS Application..." -ForegroundColor Cyan
Write-Host ""

# Remove existing rules if they exist
Write-Host "🧹 Removing old rules (if any)..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "ATS Backend Port 8000" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "ATS Frontend Port 3000" -ErrorAction SilentlyContinue

# Add new rules
Write-Host "✅ Adding firewall rule for Backend (Port 8000)..." -ForegroundColor Green
New-NetFirewallRule -DisplayName "ATS Backend Port 8000" `
    -Direction Inbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any `
    -Description "Allow ATS Backend API access on port 8000"

Write-Host "✅ Adding firewall rule for Frontend (Port 3000)..." -ForegroundColor Green
New-NetFirewallRule -DisplayName "ATS Frontend Port 3000" `
    -Direction Inbound `
    -LocalPort 3000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any `
    -Description "Allow ATS Frontend web access on port 3000"

Write-Host ""
Write-Host "🎉 Firewall rules added successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now access ATS from other devices on your network:" -ForegroundColor Cyan
Write-Host "  Frontend: http://10.0.21.86:3000" -ForegroundColor White
Write-Host "  Backend:  http://10.0.21.86:8000" -ForegroundColor White
Write-Host ""
Write-Host "To verify rules were added, run:" -ForegroundColor Yellow
Write-Host "  Get-NetFirewallRule -DisplayName 'ATS*'" -ForegroundColor White
