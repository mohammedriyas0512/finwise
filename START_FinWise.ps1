# FinWise launcher for Windows (PowerShell).
#
# Runs FinWise.exe with its console window hidden. You can double-click this
# file (or run it from a terminal). The app still works if you run FinWise.exe
# directly - the console will just be visible (which is fine and shows logs).
#
# Because the executable is built WITHOUT --windowed, sys.stdout/stderr stay
# valid, so uvicorn's formatter no longer crashes with the "isatty" error.

$ErrorActionPreference = 'SilentlyContinue'

# Resolve the directory this script lives in (project root).
$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Exe  = Join-Path $Root 'backend\dist_finwise\FinWise.exe'

if (-not (Test-Path $Exe)) {
    Write-Host "[FinWise] FinWise.exe not found at:`n  $Exe`n`nBuild it first:" -ForegroundColor Yellow
    Write-Host "  cd backend && python build_exe.py" -ForegroundColor Cyan
    Write-Host "`nOr run from source with START_FinWise.bat / START_FinWise.sh" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}

# Launch hidden. The server logs are written to backend/dist_finwise/logs/.
Write-Host "[FinWise] Starting... open http://127.0.0.1:8000/ in your browser." -ForegroundColor Green
Start-Process -FilePath $Exe -WindowStyle Hidden

# Give the server a moment, then open the browser.
Start-Sleep -Seconds 3
Start-Process 'http://127.0.0.1:8000/'
