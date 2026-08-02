"""
Chaquopy entry point: configures paths, then runs the FastAPI backend on
http://127.0.0.1:8000 inside a background thread.

The Java side calls ``init(files_dir)`` before ``start()`` so that all
persistent data (SQLite DB, exports, secret key) lives in app-private storage
and the bundled frontend is served from the extracted asset copy.
"""
from __future__ import annotations

import os
import threading
import time
import urllib.request
from typing import Optional

_server_thread: Optional[threading.Thread] = None
_server_error: Optional[BaseException] = None
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


def start(host: str = "127.0.0.1", port: int = 8000, timeout: float = 30.0) -> bool:
    """Start uvicorn in a daemon thread and wait until /health responds.

    Raises the backend's exception if it fails to boot.
    """
    global _server_thread, _server_error
    with _config_lock:
        if _server_thread is not None and _server_thread.is_alive():
            return True
        _server_error = None

        def _run() -> None:
            global _server_error
            try:
                import uvicorn
                from app.main import app

                uvicorn.run(app, host=host, port=port, log_level="warning", access_log=False)
            except BaseException as exc:  # noqa: BLE001 - must surface any boot failure
                _server_error = exc

        _server_thread = threading.Thread(target=_run, name="finwise-server", daemon=True)
        _server_thread.start()

    deadline = time.time() + timeout
    while time.time() < deadline:
        if _server_error is not None:
            raise RuntimeError(f"FinWise backend failed to start: {_server_error}") from _server_error
        try:
            with urllib.request.urlopen(f"http://{host}:{port}/health", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:  # noqa: BLE001 - server not up yet
            time.sleep(0.25)
    raise RuntimeError(f"FinWise backend did not become ready within {timeout}s")


def is_running() -> bool:
    return _server_thread is not None and _server_thread.is_alive()


def main() -> None:
    """Entry point used by Chaquopy when configured as the Python entry point."""
    start()
