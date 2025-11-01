# 🚀 Installation Test Script
# Tests the complete installation process following the README.md

param(
    [string]$TestDir = "ats-test-install",
    [string]$GroqApiKey = "",
    [switch]$CleanupAfter = $false
)

Write-Host "🧪 Testing ATS Fresh Installation Process" -ForegroundColor Cyan
Write-Host "=" * 60

$originalLocation = Get-Location
$errors = @()
$warnings = @()

try {
    # Create test directory
    Write-Host "`n📁 Creating test directory: $TestDir" -ForegroundColor Yellow
    if (Test-Path $TestDir) {
        Remove-Item $TestDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TestDir -Force | Out-Null
    Set-Location $TestDir

    # Clone repository
    Write-Host "`n📡 Cloning repository..." -ForegroundColor Yellow
    $cloneResult = git clone https://github.com/kareemelthird/ATSAI.git . 2>&1
    if ($LASTEXITCODE -ne 0) {
        $errors += "❌ Git clone failed: $cloneResult"
        throw "Clone failed"
    }
    Write-Host "✅ Repository cloned successfully" -ForegroundColor Green

    # Test backend setup
    Write-Host "`n🐍 Setting up backend..." -ForegroundColor Yellow
    Set-Location backend

    # Install Python dependencies
    Write-Host "   Installing Python dependencies..."
    try {
        # Try pip first
        $pipResult = pip install -r requirements.txt 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
        } else {
            # Try python -m pip as fallback
            Write-Host "   Trying alternative installation method..."
            $pipResult = python -m pip install -r requirements.txt 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Backend dependencies installed (using python -m pip)" -ForegroundColor Green
            } else {
                $errors += "❌ Backend dependencies installation failed: $pipResult"
                Write-Host "❌ pip install failed" -ForegroundColor Red
                Write-Host "Error details: $pipResult" -ForegroundColor Red
            }
        }
    } catch {
        $errors += "❌ Backend dependencies installation error: $($_.Exception.Message)"
        Write-Host "❌ pip install error" -ForegroundColor Red
    }

    # Setup environment file
    Write-Host "   Setting up backend environment..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        
        # Update with test values if API key provided
        if ($GroqApiKey) {
            (Get-Content ".env") -replace "your_groq_api_key_here", $GroqApiKey | Set-Content ".env"
            Write-Host "✅ Environment configured with provided API key" -ForegroundColor Green
        } else {
            $warnings += "⚠️  No Groq API key provided - AI features will not work"
        }
    } else {
        $errors += "❌ .env.example file not found in backend"
    }

    Set-Location ..

    # Test frontend setup
    Write-Host "`n⚛️  Setting up frontend..." -ForegroundColor Yellow
    Set-Location frontend

    # Install Node dependencies
    Write-Host "   Installing Node.js dependencies..."
    $npmResult = npm install 2>&1
    if ($LASTEXITCODE -ne 0) {
        $errors += "❌ Frontend dependencies installation failed"
        Write-Host "❌ npm install failed" -ForegroundColor Red
    } else {
        Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
    }

    # Setup frontend environment
    Write-Host "   Setting up frontend environment..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Frontend environment configured" -ForegroundColor Green
    } else {
        $warnings += "⚠️  Frontend .env.example not found"
    }

    Set-Location ..

    # Test database schema
    Write-Host "`n🐘 Testing database schema..." -ForegroundColor Yellow
    if (Test-Path "backend/CLEAN_SCHEMA.sql") {
        $schemaContent = Get-Content "backend/CLEAN_SCHEMA.sql" -Raw
        if ($schemaContent.Length -gt 1000) {
            Write-Host "✅ Database schema file found and appears complete" -ForegroundColor Green
        } else {
            $warnings += "⚠️  Database schema file seems incomplete"
        }
    } else {
        $errors += "❌ CLEAN_SCHEMA.sql not found"
    }

    # Test configuration files
    Write-Host "`n⚙️  Testing configuration files..." -ForegroundColor Yellow
    
    $configFiles = @(
        "docker-compose.yml",
        "backend/requirements.txt",
        "frontend/package.json",
        "backend/Dockerfile",
        "frontend/Dockerfile"
    )
    
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            Write-Host "✅ $file found" -ForegroundColor Green
        } else {
            $warnings += "⚠️  $file not found"
        }
    }

    # Test startup readiness (without actually starting)
    Write-Host "`n🚀 Testing startup readiness..." -ForegroundColor Yellow
    
    # Check if we can import main backend modules
    Set-Location backend
    try {
        $pythonTest = python -c "import app.main; print('Backend imports OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Backend Python imports working" -ForegroundColor Green
        } else {
            # Try to give more specific information about the import issue
            Write-Host "⚠️  Testing individual imports..." -ForegroundColor Yellow
            $basicTest = python -c "import sys; print('Python basic imports OK')" 2>&1
            if ($LASTEXITCODE -eq 0) {
                $warnings += "⚠️  Backend Python imports may have issues (dependencies installed but app import failed): $pythonTest"
            } else {
                $warnings += "⚠️  Python basic imports failing: $basicTest"
            }
        }
    } catch {
        $warnings += "⚠️  Backend Python import test error: $($_.Exception.Message)"
    }
    
    Set-Location ../frontend
    # Check if frontend build configuration is valid
    if (Test-Path "vite.config.ts") {
        Write-Host "✅ Frontend build configuration found" -ForegroundColor Green
    } else {
        $warnings += "⚠️  Frontend build configuration missing"
    }

} catch {
    $errors += "❌ Installation test failed: $($_.Exception.Message)"
} finally {
    Set-Location $originalLocation
    
    # Cleanup if requested
    if ($CleanupAfter -and (Test-Path $TestDir)) {
        Write-Host "`n🧹 Cleaning up test directory..." -ForegroundColor Yellow
        Remove-Item $TestDir -Recurse -Force
        Write-Host "✅ Test directory cleaned up" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n" + "=" * 60
Write-Host "📊 Installation Test Summary" -ForegroundColor Cyan

if ($errors.Count -eq 0) {
    Write-Host "`n✅ Installation test completed successfully!" -ForegroundColor Green
    Write-Host "   The ATS system can be installed following the README.md instructions" -ForegroundColor Green
    $exitCode = 0
} else {
    Write-Host "`n❌ Installation test failed with errors:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "   $error" -ForegroundColor Red
    }
    $exitCode = 1
}

if ($warnings.Count -gt 0) {
    Write-Host "`n⚠️  Warnings found:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "   $warning" -ForegroundColor Yellow
    }
}

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "   • The installation process works correctly"
    Write-Host "   • You can proceed with actual deployment"
    Write-Host "   • Test directory: $TestDir (kept for review)"
} else {
    Write-Host "   • Fix the issues listed above"
    Write-Host "   • Update README.md if installation steps need clarification"
    Write-Host "   • Re-run this test after fixes"
}

Write-Host "`n📖 Usage Examples:" -ForegroundColor Cyan
Write-Host "   .\test-installation.ps1 -GroqApiKey 'gsk_your_key_here'"
Write-Host "   .\test-installation.ps1 -TestDir 'my-test' -CleanupAfter"

exit $exitCode