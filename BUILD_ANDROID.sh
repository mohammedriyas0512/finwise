#!/usr/bin/env bash
#
# FinWise for Android, via Termux.
#
# This builds a portable one-file FinWise executable that runs inside Termux on
# any Android phone/tablet - no root, no Play Store needed. The React frontend
# is served by the same FastAPI server, so there is nothing else to install.
#
# One-time setup on your phone:
#   1. Install "Termux" from F-Droid (https://f-droid.org/packages/com.termux/)
#      - NOT the Play Store version (it is outdated).
#   2. In Termux, allow storage and install tooling:
#         termux-setup-storage
#         pkg update && pkg upgrade -y
#         pkg install -y python clang libjpeg-turbo zlib make \
#                       nodejs-lts git openssl termux-api
#   3. Copy this whole FinWise/ folder onto the phone (e.g. into
#      ~/storage/downloads/FinWise, or git clone it).
#
# Then run this script from inside the FinWise folder:
#         cd FinWise
#         bash BUILD_ANDROID.sh
#
# It will build frontend/dist, create a venv, pip install requirements + the
# PyInstaller-free launcher, and then start the server.
#
# To open FinWise on the phone:
#   - Same device: http://127.0.0.1:8000/  (or use the "Install app" option in
#     the browser menu to add it to your home screen - it is a PWA).
#   - From another device on the same Wi-Fi, use the phone's LAN IP:
#         hostname -I     # shows e.g. 192.168.1.23
#         then open http://192.168.1.23:8000/ on the other device.
#
# Optional: keep the screen awake while FinWise runs:
#         termux-wake-lock

set -u

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT" || exit 1

echo "[FinWise] Building frontend..."
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
    npm install
fi
npm run build
cd "$ROOT"

echo "[FinWise] Setting up Python venv..."
PY="$ROOT/backend/venv/bin/python"
if [ ! -x "$PY" ]; then
    python3 -m venv "$ROOT/backend/venv"
fi
"$PY" -m pip install -q --upgrade pip
"$PY" -m pip install -q -r "$ROOT/backend/requirements.txt"

echo "[FinWise] Starting server (http://127.0.0.1:8000/)..."
( command -v termux-wake-lock >/dev/null && termux-wake-lock ) || true
HOST="${HOST:-0.0.0.0}" PORT="${PORT:-8000}" "$PY" "$ROOT/backend/run.py"
