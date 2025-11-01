# 🧪 Run All Tests Script
# Executes all test scripts in sequence

param(
    [string]$GroqApiKey = "",
    [string]$TestDir = "ats-test-install",
    [switch]$CleanupAfter = $false,
    [switch]$SkipFunctionality = $false
)

Write-Host "🧪 Running Complete ATS Installation Test Suite" -ForegroundColor Cyan
Write-Host "=" * 60

$totalErrors = 0
$testResults = @()

# Test 1: Prerequisites
Write-Host "`n🔍 Step 1: Testing Prerequisites" -ForegroundColor Magenta
Write-Host "-" * 40
try {
    & ".\test-prerequisites.ps1"
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        $testResults += "✅ Prerequisites Test: PASSED"
        Write-Host "`n✅ Prerequisites test completed successfully" -ForegroundColor Green
    } else {
        $testResults += "❌ Prerequisites Test: FAILED"
        $totalErrors++
        Write-Host "`n❌ Prerequisites test failed" -ForegroundColor Red
        Write-Host "Please install missing requirements before continuing." -ForegroundColor Red
        exit 1
    }
} catch {
    $testResults += "❌ Prerequisites Test: ERROR"
    $totalErrors++
    Write-Host "`n❌ Prerequisites test error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Installation
Write-Host "`n🚀 Step 2: Testing Installation Process" -ForegroundColor Magenta
Write-Host "-" * 40
try {
    $installParams = @{
        TestDir = $TestDir
        CleanupAfter = $false  # Keep for functionality test
    }
    
    if ($GroqApiKey) {
        $installParams.GroqApiKey = $GroqApiKey
    }
    
    & ".\test-installation.ps1" @installParams
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        $testResults += "✅ Installation Test: PASSED"
        Write-Host "`n✅ Installation test completed successfully" -ForegroundColor Green
    } else {
        $testResults += "❌ Installation Test: FAILED"
        $totalErrors++
        Write-Host "`n❌ Installation test failed" -ForegroundColor Red
    }
} catch {
    $testResults += "❌ Installation Test: ERROR"
    $totalErrors++
    Write-Host "`n❌ Installation test error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Functionality (only if installation passed and not skipped)
if (-not $SkipFunctionality -and $testResults[-1] -like "*Installation Test: PASSED*") {
    Write-Host "`n🔧 Step 3: Testing Application Functionality" -ForegroundColor Magenta
    Write-Host "-" * 40
    Write-Host "⚠️  Note: This test requires the application to be running" -ForegroundColor Yellow
    Write-Host "Please start the application manually if not already running:" -ForegroundColor Yellow
    Write-Host "   cd $TestDir" -ForegroundColor Gray
    Write-Host "   # Start backend and frontend as per README.md" -ForegroundColor Gray
    
    $continue = Read-Host "`nPress Enter when application is running, or 'skip' to skip functionality test"
    
    if ($continue.ToLower() -ne "skip") {
        try {
            & ".\test-functionality.ps1"
            $exitCode = $LASTEXITCODE
            if ($exitCode -eq 0) {
                $testResults += "✅ Functionality Test: PASSED"
                Write-Host "`n✅ Functionality test completed successfully" -ForegroundColor Green
            } else {
                $testResults += "❌ Functionality Test: FAILED"
                $totalErrors++
                Write-Host "`n❌ Functionality test failed" -ForegroundColor Red
            }
        } catch {
            $testResults += "❌ Functionality Test: ERROR"
            $totalErrors++
            Write-Host "`n❌ Functionality test error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        $testResults += "⏭️  Functionality Test: SKIPPED"
        Write-Host "`n⏭️  Functionality test skipped by user" -ForegroundColor Yellow
    }
} elseif ($SkipFunctionality) {
    $testResults += "⏭️  Functionality Test: SKIPPED"
    Write-Host "`n⏭️  Functionality test skipped (parameter)" -ForegroundColor Yellow
} else {
    $testResults += "⏭️  Functionality Test: SKIPPED (Installation failed)"
    Write-Host "`n⏭️  Functionality test skipped due to installation failure" -ForegroundColor Yellow
}

# Cleanup if requested and all tests passed
if ($CleanupAfter -and $totalErrors -eq 0) {
    Write-Host "`n🧹 Cleaning up test directory..." -ForegroundColor Yellow
    if (Test-Path $TestDir) {
        Remove-Item $TestDir -Recurse -Force
        Write-Host "✅ Test directory cleaned up" -ForegroundColor Green
    }
}

# Final Summary
Write-Host "`n" + "=" * 60
Write-Host "📊 Complete Test Suite Results" -ForegroundColor Cyan
Write-Host "=" * 60

foreach ($result in $testResults) {
    Write-Host $result
}

Write-Host "`n📈 Summary:" -ForegroundColor Cyan
if ($totalErrors -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED! The ATS system is ready for deployment." -ForegroundColor Green
    Write-Host "`nThe installation process works correctly and the application" -ForegroundColor Green
    Write-Host "can be successfully deployed following the README.md instructions." -ForegroundColor Green
} else {
    Write-Host "❌ $totalErrors test(s) failed. Issues need to be resolved." -ForegroundColor Red
    Write-Host "`nPlease review the failed tests and update documentation" -ForegroundColor Red
    Write-Host "or fix issues before proceeding with deployment." -ForegroundColor Red
}

Write-Host "`n📁 Test artifacts:" -ForegroundColor Cyan
if (Test-Path $TestDir) {
    Write-Host "   • Test installation: $TestDir (preserved for review)"
} else {
    Write-Host "   • Test installation: Cleaned up"
}

Write-Host "`n📖 Usage Examples:" -ForegroundColor Cyan
Write-Host "   .\run-all-tests.ps1 -GroqApiKey 'gsk_your_key_here'"
Write-Host "   .\run-all-tests.ps1 -TestDir 'my-test' -CleanupAfter"
Write-Host "   .\run-all-tests.ps1 -SkipFunctionality"

exit $totalErrors