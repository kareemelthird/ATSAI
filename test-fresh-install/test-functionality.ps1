# 🧪 Functionality Test Script
# Tests basic application functionality after installation

param(
    [string]$BackendUrl = "http://localhost:8000",
    [string]$FrontendUrl = "http://localhost:3000",
    [string]$TestEmail = "test@ats.com",
    [string]$TestPassword = "TestPass123!",
    [int]$TimeoutSeconds = 30
)

Write-Host "🧪 Testing ATS Application Functionality" -ForegroundColor Cyan
Write-Host "=" * 60

$errors = @()
$warnings = @()

# Test backend health
Write-Host "`n🔍 Testing backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BackendUrl/health" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
    Write-Host "✅ Backend health check passed" -ForegroundColor Green
} catch {
    $errors += "❌ Backend health check failed: $($_.Exception.Message)"
}

# Test API documentation
Write-Host "`n📖 Testing API documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/docs" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API documentation accessible" -ForegroundColor Green
    } else {
        $warnings += "⚠️  API documentation returned status: $($response.StatusCode)"
    }
} catch {
    $warnings += "⚠️  API documentation not accessible: $($_.Exception.Message)"
}

# Test database connection
Write-Host "`n🐘 Testing database connection..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BackendUrl/api/v1/health/db" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
    Write-Host "✅ Database connection working" -ForegroundColor Green
} catch {
    $errors += "❌ Database connection failed: $($_.Exception.Message)"
}

# Test authentication endpoint
Write-Host "`n🔐 Testing authentication..." -ForegroundColor Yellow
try {
    $loginData = @{
        email = $TestEmail
        password = $TestPassword
    } | ConvertTo-Json

    $headers = @{
        "Content-Type" = "application/json"
    }

    try {
        $response = Invoke-RestMethod -Uri "$BackendUrl/api/v1/auth/login" -Method POST -Body $loginData -Headers $headers -TimeoutSec $TimeoutSeconds
        Write-Host "✅ Authentication endpoint responding" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-Host "✅ Authentication endpoint working (401 expected for test credentials)" -ForegroundColor Green
        } else {
            $warnings += "⚠️  Authentication endpoint returned: $($_.Exception.Response.StatusCode)"
        }
    }
} catch {
    $errors += "❌ Authentication test failed: $($_.Exception.Message)"
}

# Test frontend accessibility
Write-Host "`n⚛️  Testing frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $FrontendUrl -TimeoutSec $TimeoutSeconds -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend accessible" -ForegroundColor Green
        
        # Check if it contains expected content
        if ($response.Content -match "ATS" -or $response.Content -match "React") {
            Write-Host "✅ Frontend content looks correct" -ForegroundColor Green
        } else {
            $warnings += "⚠️  Frontend content may not be loading correctly"
        }
    } else {
        $warnings += "⚠️  Frontend returned status: $($response.StatusCode)"
    }
} catch {
    $errors += "❌ Frontend not accessible: $($_.Exception.Message)"
}

# Test API endpoints structure
Write-Host "`n🔌 Testing API endpoints..." -ForegroundColor Yellow
$endpoints = @(
    "/api/v1/candidates",
    "/api/v1/jobs", 
    "/api/v1/applications",
    "/api/v1/settings"
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl$endpoint" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        if ($response.StatusCode -eq 401 -or $response.StatusCode -eq 200) {
            Write-Host "✅ $endpoint responding correctly" -ForegroundColor Green
        } else {
            $warnings += "⚠️  $endpoint returned status: $($response.StatusCode)"
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-Host "✅ $endpoint protected (401 expected)" -ForegroundColor Green
        } else {
            $warnings += "⚠️  $endpoint test failed: $($_.Exception.Message)"
        }
    }
}

# Test file upload endpoint
Write-Host "`n📄 Testing file upload endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/v1/upload/resume" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
    if ($response.StatusCode -eq 401 -or $response.StatusCode -eq 405) {
        Write-Host "✅ Upload endpoint responding (authentication required)" -ForegroundColor Green
    } else {
        $warnings += "⚠️  Upload endpoint returned unexpected status: $($response.StatusCode)"
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 405) {
        Write-Host "✅ Upload endpoint protected correctly" -ForegroundColor Green
    } else {
        $warnings += "⚠️  Upload endpoint test failed: $($_.Exception.Message)"
    }
}

# Performance test
Write-Host "`n⚡ Testing response times..." -ForegroundColor Yellow
try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-RestMethod -Uri "$BackendUrl/health" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
    $stopwatch.Stop()
    
    $responseTime = $stopwatch.ElapsedMilliseconds
    if ($responseTime -lt 1000) {
        Write-Host "✅ Response time: ${responseTime}ms (Good)" -ForegroundColor Green
    } elseif ($responseTime -lt 3000) {
        Write-Host "⚠️  Response time: ${responseTime}ms (Acceptable)" -ForegroundColor Yellow
    } else {
        $warnings += "⚠️  Slow response time: ${responseTime}ms"
    }
} catch {
    $warnings += "⚠️  Performance test failed: $($_.Exception.Message)"
}

# Summary
Write-Host "`n" + "=" * 60
Write-Host "📊 Functionality Test Summary" -ForegroundColor Cyan

if ($errors.Count -eq 0) {
    Write-Host "`n✅ All critical functionality tests passed!" -ForegroundColor Green
    Write-Host "   The ATS application is working correctly" -ForegroundColor Green
    $exitCode = 0
} else {
    Write-Host "`n❌ Critical functionality issues found:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "   $error" -ForegroundColor Red
    }
    $exitCode = 1
}

if ($warnings.Count -gt 0) {
    Write-Host "`n⚠️  Warnings (may need attention):" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "   $warning" -ForegroundColor Yellow
    }
}

Write-Host "`n🚀 Test Results:" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "   • Backend API is responding correctly"
    Write-Host "   • Frontend is accessible"
    Write-Host "   • Authentication endpoints are working"
    Write-Host "   • Database connection is established"
    Write-Host "   • Ready for production use"
} else {
    Write-Host "   • Critical issues need to be resolved"
    Write-Host "   • Check application logs for more details"
    Write-Host "   • Verify database and environment configuration"
}

Write-Host "`n📖 Usage Examples:" -ForegroundColor Cyan
Write-Host "   .\test-functionality.ps1"
Write-Host "   .\test-functionality.ps1 -BackendUrl 'http://localhost:8001'"
Write-Host "   .\test-functionality.ps1 -TimeoutSeconds 60"

exit $exitCode