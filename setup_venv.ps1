# PowerShell setup script for creating and activating a virtual environment

Write-Host "Creating virtual environment..." -ForegroundColor Green
python -m venv venv

Write-Host "`nVirtual environment created successfully!" -ForegroundColor Green
Write-Host "`nTo activate the virtual environment, run:" -ForegroundColor Yellow
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "`nThen install dependencies with:" -ForegroundColor Yellow
Write-Host "    pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host ""
