"""
Chaquopy entry point: configures paths, then runs the FastAPI backend on
http://127.0.0.1:8000 inside a background thread.

The Java side calls ``init(files_dir, www_dir)`` before ``start()`` so that all
persistent data (SQLite DB, exports, secret key) lives in app-private storage
and the bundled frontend is served from the extracted asset copy.
"""
from __future__ import annotations

import os
import threading
from typing import Optional

_server_thread: Optional[threading.Thread] = None
_config_lock = threading.Lock()


def init(data_dir: str, frontend_dist: Optional[str] = None) -> None:
    """Set environment variables before any app module is imported."""
    os.environ["FINWISE_DATA_DIR"] = data_dir
    if frontend_dist is None:
        # The built React SPA is bundled alongside the Python sources and
        # extracted by Chaquopy. Locate it through the ``frontend`` package.
        try:
            import frontend
            frontend_dist = os.path.join(os.path.dirname(frontend.__file__), "dist")
        except ImportError:
            frontend_dist = None
    if frontend_dist:
        os.environ["FINWISE_FRONTEND_DIST"] = frontend_dist


def start(host: str = "127.0.0.1", port: int = 8000) -> bool:
    """Start uvicorn in a daemon thread. Safe to call multiple times."""
    global _server_thread
    with _config_lock:
        if _server_thread is not None and _server_thread.is_alive():
            return False

        def _run() -> None:
            import uvicorn
            from app.main import app

            uvicorn.run(app, host=host, port=port, log_level="info", access_log=False)

        _server_thread = threading.Thread(target=_run, name="finwise-server", daemon=True)
        _server_thread.start()
        return True


def is_running() -> bool:
    return _server_thread is not None and _server_thread.is_alive()


def main() -> None:
    """Entry point used by Chaquopy when configured as the Python entry point."""
    start()
