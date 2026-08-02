# FinWise — Portable / Movable App Guide

FinWise is fully **portable**: the whole `FinWise/` folder can be copied to any
location, another drive, or a USB stick and it will still run. The database,
uploads, exports and logs are always resolved relative to the app, and the
optional `.env` is auto-discovered.

There are three ways to run FinWise.

---

## 1. One-click launcher (dev / source mode)

Double-click **`START_FinWise.bat`** in the FinWise root.

- On first run it creates the Python virtual environment and installs
  dependencies automatically.
- It then starts the backend (which also serves the built React frontend) and
  opens your browser at http://127.0.0.1:8000/

Requires Python 3.11+ and (first time only) internet access to install packages.

---

## 2. Standalone Windows executable (.exe)

The single-file build bundles the backend **and** the frontend — no Python
needed on the target machine.

> Note: the executable is built as a normal console binary (not `--windowed`) on
> purpose. Under `--windowed`, PyInstaller nulls `sys.stdout`/`sys.stderr`, which
> made uvicorn's log formatter crash with
> `AttributeError: 'NoneType' object has no attribute 'isatty'`
> (`ValueError: Unable to configure formatter 'default'`). The shared `run.py`
> now restores valid streams and patches uvicorn's formatter, so it launches
> cleanly. Use `START_FinWise.ps1` (Windows) to launch with the console hidden.

To build it:

- Double-click **`BUILD_EXE.bat`**, or run from `backend/`:
  ```
  venv\Scripts\activate
  python build_exe.py
  ```

Output: **`backend\dist_finwise\FinWise.exe`**

The frontend is now bundled **inside** the exe, so it is a true single file.
Copy just **`FinWise.exe`** to any Windows PC/laptop or USB stick and
double-click: it starts the server, opens the browser, and creates
`database\finwise.db` next to the executable. Fully portable — move it anywhere.

For installing on phones/tablets, see **`INSTALL.md`**.

---

## 3. Manual dev mode (backend + frontend separately)

See the main `README.md` "Running (Development)" section for hot-reload dev
with the Vite dev server on port 5173.

---

## Default login

```
email:    admin@finwise.app
password: Admin@123456
```

## Configuration

Edit `.env` (in the FinWise root, or beside `FinWise.exe`). Relative SQLite
paths are resolved against the app folder, so they stay valid after moving.
To use PostgreSQL, set `DATABASE_URL=postgresql+psycopg://user:pass@host:5432/finwise`.
