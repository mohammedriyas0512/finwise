@echo off
REM ============================================================
REM  FinWise - one-click launcher (portable / movable)
REM  Runs the backend which also serves the built frontend,
REM  then opens your browser. Works from any folder location.
REM ============================================================
setlocal
cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo [FinWise] Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo [FinWise] Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

echo [FinWise] Starting FinWise...
REM Use the venv's python explicitly so the correct interpreter is always used.
"venv\Scripts\python.exe" run.py

REM If run.py exits (crash or Ctrl+C), keep the window open so the message
REM is readable instead of the window flashing and disappearing.
echo.
echo [FinWise] The server has stopped. Review any message above.
pause

endlocal
