#!/usr/bin/env bash
#
# FinWise launcher for Linux / macOS / Android (Termux).
#
# Usage:
#   ./START_FinWise.sh            # runs from source using the bundled venv, or
#                                 # the FinWise executable if it exists for this
#                                 # platform, else a system python3.
#
# The app is fully portable: copy the whole FinWise/ folder anywhere (incl. a
# USB stick) and run this script. Database/uploads/exports live next to it.

set -u

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT" || exit 1

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

# 1) Prefer a native one-file executable if it was built for this platform.
#    (On Linux this would be backend/dist_finwise/FinWise.)
EXE="$ROOT/backend/dist_finwise/FinWise"
if [ -x "$EXE" ]; then
    echo "[FinWise] Starting native executable..."
    "$EXE" &
    sleep 3
    ( command -v xdg-open >/dev/null && xdg-open "http://$HOST:$PORT/" ) \
        || ( command -v open >/dev/null && open "http://$HOST:$PORT/" ) \
        || echo "[FinWise] Open http://$HOST:$PORT/ in your browser."
    wait
    exit 0
fi

# 2) Otherwise run from source with the bundled venv (Windows-first layout).
PY="$ROOT/backend/venv/bin/python"
if [ ! -x "$PY" ]; then
    PY=python3
fi

if [ "$PY" = "python3" ] && ! command -v python3 >/dev/null 2>&1; then
    echo "[FinWise] python3 not found. Install Python 3.11+ and re-run." >&2
    exit 1
fi

echo "[FinWise] Installing/updating dependencies (first run only)..."
( "$PY" -m venv "$ROOT/backend/venv" >/dev/null 2>&1 ; true )
VENV_PY="$ROOT/backend/venv/bin/python"
[ -x "$VENV_PY" ] && PY="$VENV_PY"
"$PY" -m pip install -q -r "$ROOT/backend/requirements.txt" || \
    echo "[FinWise] pip install failed - ensure internet access on first run." >&2

echo "[FinWise] Starting server at http://$HOST:$PORT/ ..."
HOST="$HOST" PORT="$PORT" "$PY" "$ROOT/backend/run.py" &
SVPID=$!
sleep 3
( command -v xdg-open >/dev/null && xdg-open "http://$HOST:$PORT/" ) \
    || ( command -v open >/dev/null && open "http://$HOST:$PORT/" ) \
    || echo "[FinWise] Open http://$HOST:$PORT/ in your browser."
wait "$SVPID"
