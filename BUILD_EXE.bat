@echo off
REM ============================================================
REM  FinWise - build the standalone Windows .exe
REM  1) builds the React frontend
REM  2) bundles backend + frontend into a single FinWise.exe
REM  Output: backend\dist_finwise\FinWise.exe (fully portable)
REM ============================================================
setlocal
cd /d "%~dp0"

echo [FinWise] Building frontend...
cd frontend
call npm install
call npm run build
cd ..

echo [FinWise] Building executable...
cd backend
if not exist "venv\Scripts\python.exe" (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt pyinstaller
) else (
    call venv\Scripts\activate
    pip install pyinstaller >nul 2>&1
)
python build_exe.py

echo.
echo [FinWise] Done. Executable at: backend\dist_finwise\FinWise.exe
pause
endlocal
