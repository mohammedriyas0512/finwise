#!/usr/bin/env bash
#
# Build a portable native one-file executable for Linux / macOS / Android(Termux).
#
# Run from the FinWise root:
#     bash BUILD_LINUX.sh
#
# Output: backend/dist_finwise/FinWise  (a single portable binary - copy it
# anywhere, the database is created next to it on first run).
#
# Requirements: python3, venv, nodejs (for the frontend build), and the system
# packages needed to build wheels (gcc/clang, libjpeg, zlib, openssl).

set -u

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT" || exit 1

echo "[FinWise] Building frontend..."
cd "$ROOT/frontend"
[ -d node_modules ] || npm install
npm run build
cd "$ROOT"

echo "[FinWise] Preparing build venv..."
VENV="$ROOT/.build_venv"
PY="$VENV/bin/python"
if [ ! -x "$PY" ]; then
    python3 -m venv "$VENV"
fi
"$PY" -m pip install -q --upgrade pip
"$PY" -m pip install -q -r "$ROOT/backend/requirements.txt" pyinstaller

echo "[FinWise] Running PyInstaller (this can take a few minutes)..."
cd "$ROOT/backend"
HOST=127.0.0.1 "$PY" build_exe.py

echo
echo "=== Build complete ==="
echo "Executable: $ROOT/backend/dist_finwise/FinWise"
echo "Run it, then open http://127.0.0.1:8000/"
