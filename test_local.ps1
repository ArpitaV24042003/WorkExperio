# PowerShell script to test WorkExperio locally
Write-Host "🧪 Testing WorkExperio Locally" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "1. Checking if backend server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ Backend server is running!" -ForegroundColor Green
    $serverRunning = $true
} catch {
    Write-Host "   ⚠️  Backend server is not running" -ForegroundColor Yellow
    Write-Host "   Starting backend server..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Please run in a separate terminal:" -ForegroundColor Cyan
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   python -m uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host ""
    $serverRunning = $false
}

if ($serverRunning) {
    Write-Host ""
    Write-Host "2. Running E2E tests..." -ForegroundColor Yellow
    Set-Location backend
    python run_e2e_tests.py
    $testExitCode = $LASTEXITCODE
    Set-Location ..
    
    if ($testExitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ All tests passed!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Some tests failed" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "⚠️  Cannot run tests - server not running" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Start backend: cd backend && python -m uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host "2. Then run this script again" -ForegroundColor White
}

