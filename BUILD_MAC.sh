#!/usr/bin/env bash
#
# Build a native FinWise .app bundle for macOS.
#
# Run this ON A MAC (Apple Silicon or Intel). Windows/Linux cannot produce a
# Mach-O .app. If you don't have a Mac, push this repo to GitHub and let the
# included GitHub Actions workflow (.github/workflows/build-mac.yml) build the
# .app on a macOS runner and upload it as a downloadable artifact.
#
# Prereqs (brew):  brew install python node
# Usage:  bash BUILD_MAC.sh
# Output: backend/dist_finwise/FinWise.app  (copy to /Applications or anywhere)

set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

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

echo "[FinWise] Building one-file Mach-O binary (no --windowed -> no isatty crash)..."
cd "$ROOT/backend"
HOST=127.0.0.1 FINWISE_NO_AUTOBROWSE=1 "$PY" build_exe.py

echo "[FinWise] Packing FinWise.app bundle..."
"$PY" pack_mac_app.py

echo
echo "=== Done ==="
echo "App bundle: $ROOT/backend/dist_finwise/FinWise.app"
echo "Copy it to /Applications, or double-click to run, then open http://127.0.0.1:8000/"
