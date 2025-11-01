# 🔍 Prerequisites Test Script
# Tests if all required software is installed and accessible

Write-Host "🧪 Testing Prerequisites for ATS Fresh Installation" -ForegroundColor Cyan
Write-Host "=" * 60

$errors = @()
$warnings = @()

# Test Node.js
Write-Host "`n📦 Testing Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        $versionNum = [Version]($nodeVersion -replace "v", "")
        if ($versionNum -ge [Version]"18.0.0") {
            Write-Host "✅ Node.js $nodeVersion (OK)" -ForegroundColor Green
        } else {
            $errors += "❌ Node.js version $nodeVersion is below required 18.0.0"
        }
    } else {
        $errors += "❌ Node.js not found or not in PATH"
    }
} catch {
    $errors += "❌ Node.js test failed: $($_.Exception.Message)"
}

# Test npm
Write-Host "`n📦 Testing npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>$null
    if ($npmVersion) {
        Write-Host "✅ npm $npmVersion (OK)" -ForegroundColor Green
    } else {
        $errors += "❌ npm not found"
    }
} catch {
    $errors += "❌ npm test failed: $($_.Exception.Message)"
}

# Test Python
Write-Host "`n🐍 Testing Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        $versionMatch = $pythonVersion -match "Python (\d+\.\d+\.\d+)"
        if ($versionMatch) {
            $versionNum = [Version]$matches[1]
            if ($versionNum -ge [Version]"3.9.0") {
                Write-Host "✅ $pythonVersion (OK)" -ForegroundColor Green
                
                # Check for Python 3.13+ compatibility note
                if ($versionNum -ge [Version]"3.13.0") {
                    $warnings += "⚠️  Python 3.13+ detected - ensure latest package versions are used for compatibility"
                }
            } else {
                $errors += "❌ Python version $pythonVersion is below required 3.9.0"
            }
        }
    } else {
        $errors += "❌ Python not found or not in PATH"
    }
} catch {
    $errors += "❌ Python test failed: $($_.Exception.Message)"
}

# Test pip
Write-Host "`n📦 Testing pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>$null
    if ($pipVersion) {
        Write-Host "✅ pip available (OK)" -ForegroundColor Green
    } else {
        $errors += "❌ pip not found"
    }
} catch {
    $errors += "❌ pip test failed: $($_.Exception.Message)"
}

# Test PostgreSQL
Write-Host "`n🐘 Testing PostgreSQL..." -ForegroundColor Yellow
try {
    $psqlVersion = psql --version 2>$null
    if ($psqlVersion) {
        Write-Host "✅ $psqlVersion (OK)" -ForegroundColor Green
    } else {
        $warnings += "⚠️  psql command not found - PostgreSQL may not be in PATH"
    }
} catch {
    $warnings += "⚠️  PostgreSQL test failed - may need manual verification"
}

# Test Git
Write-Host "`n📡 Testing Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>$null
    if ($gitVersion) {
        Write-Host "✅ $gitVersion (OK)" -ForegroundColor Green
    } else {
        $errors += "❌ Git not found"
    }
} catch {
    $errors += "❌ Git test failed: $($_.Exception.Message)"
}

# Test Docker (optional)
Write-Host "`n🐳 Testing Docker (optional)..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✅ $dockerVersion (OK)" -ForegroundColor Green
    } else {
        $warnings += "⚠️  Docker not found - manual installation will be used"
    }
} catch {
    $warnings += "⚠️  Docker not available - manual installation will be used"
}

# Summary
Write-Host "`n" + "=" * 60
Write-Host "📊 Prerequisites Test Summary" -ForegroundColor Cyan

if ($errors.Count -eq 0) {
    Write-Host "`n✅ All critical prerequisites are satisfied!" -ForegroundColor Green
    $exitCode = 0
} else {
    Write-Host "`n❌ Critical issues found:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "   $error" -ForegroundColor Red
    }
    $exitCode = 1
}

if ($warnings.Count -gt 0) {
    Write-Host "`n⚠️  Warnings:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "   $warning" -ForegroundColor Yellow
    }
}

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "   • Run .\test-installation.ps1 to test the installation process"
    Write-Host "   • Make sure you have a Groq API key ready"
    Write-Host "   • Ensure PostgreSQL service is running"
} else {
    Write-Host "   • Install missing prerequisites listed above"
    Write-Host "   • Re-run this test after installation"
}

exit $exitCode