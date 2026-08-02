"""
Build a standalone Windows executable for FinWise.

Run from backend/ with the activated venv:
    python build_exe.py

Outputs dist_finwise/FinWise.exe which, when run, starts the FastAPI server
and serves the bundled React frontend, then opens the browser.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import PyInstaller.__main__  # noqa: F401  (ensures pyinstaller is importable)

HERE = Path(__file__).resolve().parent          # backend/
PROJECT = HERE.parent                           # FinWise/
FRONTEND_DIST = PROJECT / "frontend" / "dist"

# Output directory for the final bundle.
DIST = HERE / "dist_finwise"
BUILD = HERE / "build_finwise"
WORK = HERE / "work_finwise"

# Clean previous builds.
for p in (DIST, BUILD, WORK):
    if p.exists():
        shutil.rmtree(p, ignore_errors=True)

if not FRONTEND_DIST.exists():
    sys.exit("ERROR: frontend/dist not found. Run `npm run build` in frontend/ first.")

# PyInstaller --add-data uses os.pathsep as the SRC;DEST separator (';' on Win).
SEP = os.pathsep
add_frontend = f"{FRONTEND_DIST}{SEP}frontend/dist"

# Choose a platform-appropriate icon (macOS needs .icns; Windows uses .ico).
if sys.platform == "darwin":
    _cands = [HERE / "finwise.icns"]
elif sys.platform == "win32":
    _cands = [HERE / "finwise.ico"]
else:
    _cands = [HERE / "finwise.ico", HERE / "finwise.icns"]
icon = next((c for c in _cands if c.exists()), None)
icon_args = ["--icon", str(icon)] if icon else []

# Build the executable (true one-file). We deliberately do NOT use --windowed:
# under --windowed PyInstaller sets sys.stdout/sys.stderr to None, which makes
# uvicorn's DefaultFormatter crash with "'NoneType' has no attribute 'isatty'".
# Instead we build as a normal console binary (streams stay valid) and hide the
# console window from the launcher script instead (see START_FinWise.ps1 / .sh).
PyInstaller.__main__.run([
    "run.py",
    "--name", "FinWise",
    "--onefile",
    # NOTE: no --windowed / --noconsole on purpose (keeps streams valid).
    *icon_args,
    "--add-data", add_frontend,
    "--paths", str(HERE),
    "--hidden-import", "app",
    "--hidden-import", "app.main",
    "--hidden-import", "uvicorn.logging",
    "--hidden-import", "uvicorn.protocols.http.auto",
    "--hidden-import", "uvicorn.protocols.websockets.auto",
    "--hidden-import", "uvicorn.lifespan.on",
    "--collect-submodules", "app",
    "--distpath", str(DIST),
    "--specpath", str(BUILD),
    "--workpath", str(WORK),
    "--noconfirm",
])

# The frontend is now embedded in the exe, so nothing needs copying beside it.
exe_dir = DIST
print("\n=== Build complete ===")
print(f"Executable (single file): {exe_dir / 'FinWise.exe'}")
print("The React frontend is bundled INSIDE the exe — just copy FinWise.exe anywhere.")
print("Run FinWise.exe to launch the app; the database is created next to it on first run.")
