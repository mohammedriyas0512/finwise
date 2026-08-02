"""
Standalone launcher for the FinWise desktop/server executable.

When bundled with PyInstaller this script:
  * locates the built frontend (dist/) that is shipped alongside the binary,
  * ensures the database + tables exist,
  * starts the FastAPI/uvicorn server,
  * opens the default browser to the app,
  * keeps running until Ctrl+C or window close.
"""
from __future__ import annotations

import os
import sys
import io
import logging
import webbrowser
import threading
import time

# ---------------------------------------------------------------------------
# CRITICAL FIX: PyInstaller on Windows nulls sys.stdout/sys.stderr when built
# with --windowed (or even with a hidden console). uvicorn's DefaultFormatter
# calls sys.stderr.isatty() during logging.dictConfig, which raised:
#   AttributeError: 'NoneType' object has no attribute 'isatty'
#   ValueError: Unable to configure formatter 'default'
# We (1) restore real streams and (2) swap in a safe formatter that never
# touches a None stream, so the app launches cleanly on any machine.
# ---------------------------------------------------------------------------
def _ensure_real_streams() -> None:
    """Point stdout/stderr at a file (or the console) when frozen/None."""
    if not getattr(sys, "frozen", False):
        return
    if sys.stdout is None or not hasattr(sys.stdout, "write"):
        try:
            sys.stdout = open(os.devnull, "w")
        except Exception:
            sys.stdout = io.StringIO()
    if sys.stderr is None or not hasattr(sys.stderr, "write"):
        try:
            sys.stderr = open(os.devnull, "w")
        except Exception:
            sys.stderr = io.StringIO()


def _patch_uvicorn_formatter() -> None:
    """Make uvicorn's log formatters None-safe (no isatty on a None stream).

    In uvicorn, ``ColourizedFormatter.__init__`` calls ``sys.stdout.isatty()``
    and ``DefaultFormatter.should_use_colors`` calls ``sys.stderr.isatty()``.
    Under PyInstaller --windowed (or a hidden console) those streams are None,
    which raised the original ``AttributeError``. We patch the base class's
    ``__init__`` (fixes DefaultFormatter + AccessFormatter + ColourizedFormatter)
    and ``DefaultFormatter.should_use_colors`` so neither ever touches a None
    stream. Colors are simply disabled when a TTY isn't available.
    """
    try:
        import uvicorn.logging as _ul

        if getattr(_ul.ColourizedFormatter, "_finwise_patched", False):
            return

        _orig_ctor = logging.Formatter.__init__

        def _safe_colourized_init(self, fmt=None, datefmt=None, style="%", use_colors=None):
            # Decide color usage without ever calling isatty() on a None stream.
            if use_colors in (True, False):
                self.use_colors = bool(use_colors)
            else:
                _use = False
                try:
                    so = getattr(sys, "stdout", None)
                    if so is not None and hasattr(so, "isatty") and so.isatty():
                        _use = True
                except Exception:
                    _use = False
                self.use_colors = _use
            # Call the stock Formatter ctor directly, skipping uvicorn's isatty line.
            _orig_ctor(self, fmt=fmt, datefmt=datefmt, style=style)

        def _safe_should_use_colors(self):
            return getattr(self, "use_colors", False)

        _ul.ColourizedFormatter.__init__ = _safe_colourized_init
        _ul.DefaultFormatter.should_use_colors = _safe_should_use_colors
        _ul.ColourizedFormatter._finwise_patched = True
    except Exception:
        # If uvicorn is unavailable or already patched, ignore - _ensure_real_streams
        # is the primary guard.
        pass


_ensure_real_streams()
_patch_uvicorn_formatter()

# Make sure PyInstaller's bundled modules are importable.
if getattr(sys, "frozen", False):
    # Running inside the PyInstaller bundle.
    BASE = os.path.dirname(sys.executable)
    # Frontend is bundled INSIDE the one-file exe (added via --add-data), so it
    # lives under the PyInstaller extraction dir (_MEIPASS). Fall back to a
    # sibling folder for older/side-by-side builds.
    _meipass = getattr(sys, "_MEIPASS", BASE)
    _candidates = [
        os.path.join(_meipass, "frontend", "dist"),
        os.path.join(BASE, "frontend", "dist"),
    ]
    FRONTEND_DIST = next((p for p in _candidates if os.path.isdir(p)), _candidates[0])
else:
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FRONTEND_DIST = os.path.join(BASE, "frontend", "dist")

# Ensure the backend package is importable.
BACKEND = os.path.join(BASE, "backend") if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

import uvicorn  # noqa: E402

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))


def _lan_ip() -> str:
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def open_browser() -> None:
    url = f"http://127.0.0.1:{PORT}/"
    time.sleep(2.5)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def _port_in_use(host: str, port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Probe the SAME address uvicorn will bind. We deliberately do NOT set
        # SO_REUSEADDR here: we want the probe to fail exactly when uvicorn would.
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def _pick_port(host: str, preferred: int) -> int:
    """Return the preferred port, or the next free one if it's taken."""
    for candidate in range(preferred, preferred + 20):
        if not _port_in_use(host, candidate):
            return candidate
    return preferred  # give up gracefully; uvicorn will surface the error


def main() -> None:
    # Warm up DB / tables / seed (best effort).
    try:
        from app.database.database import create_tables, SessionLocal
        from app.services.seed_service import seed_default_categories, seed_admin
        create_tables()
        with SessionLocal() as db:
            seed_default_categories(db)
            seed_admin(db)
    except Exception as exc:  # pragma: no cover
        print(f"[FinWise] startup setup warning: {exc}")

    global PORT
    if _port_in_use(HOST, PORT):
        new_port = _pick_port(HOST, PORT + 1)
        print(f"[FinWise] Port {PORT} is already in use (another FinWise may be running).")
        print(f"[FinWise] Switching to free port {new_port}.")
        PORT = new_port

    lan = _lan_ip()
    print(f"[FinWise] Starting server at http://127.0.0.1:{PORT}/")
    print(f"[FinWise] On this network (phone/other PC): http://{lan}:{PORT}/")
    print("[FinWise] Open that URL, then use 'Install app' / 'Add to Home Screen'.")
    if not os.environ.get("FINWISE_NO_AUTOBROWSE"):
        threading.Thread(target=open_browser, daemon=True).start()

    if getattr(sys, "frozen", False):
        # Serve the bundled frontend (handled inside app.main via FRONTEND_DIST lookup).
        os.environ["FINWISE_FRONTEND_DIST"] = FRONTEND_DIST

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False, log_level="info")


if __name__ == "__main__":
    main()
