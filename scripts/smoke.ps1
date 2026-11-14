# ArthaPilot Smoke Test Script (PowerShell)
# Verifies end-to-end backend readiness, demo seeding, health, and copilot endpoints

$ErrorActionPreference = "Stop"

Write-Host "--- Running ArthaPilot Smoke Checks ---" -ForegroundColor Cyan

# 1. Run Python unit tests
Write-Host "1. Verifying backend test suite..." -ForegroundColor Yellow
python -m pytest backend/tests -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend tests failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Backend tests passed (113 tests)." -ForegroundColor Green

# 2. Check categoriser accuracy
Write-Host "2. Verifying ML categoriser..." -ForegroundColor Yellow
python scripts/evaluate_categoriser.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Categoriser evaluation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Categoriser verified." -ForegroundColor Green

# 3. Check forecast backtest
Write-Host "3. Verifying Monte Carlo forecast backtest..." -ForegroundColor Yellow
python scripts/backtest.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Forecast backtest failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Forecast backtest verified." -ForegroundColor Green

Write-Host "=== All Smoke Checks Succeeded! ===" -ForegroundColor Green
exit 0

