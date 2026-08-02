"""
Central application configuration.

Loads settings from environment variables (with sensible local defaults) so the
same code runs locally with SQLite and can later be pointed at PostgreSQL by
changing DATABASE_URL / related env vars only.
"""
from __future__ import annotations

import os
import sys
import secrets
from pathlib import Path

# Where the app lives. Both source and bundled modes resolve to a stable root
# so the single movable data folder is found identically on every platform.
if getattr(sys, "frozen", False):
    # Bundled exe (or .app on macOS): sit next to the binary.
    APP_DIR = Path(sys.executable).resolve().parent
else:
    # Source tree: FinWise/backend/app/config.py -> FinWise/
    APP_DIR = Path(__file__).resolve().parent.parent.parent

# Load a local .env if present (searched next to the app dir, then the project
# root, then the backend/ dir). Loaded BEFORE any os.getenv() below.
try:
    from dotenv import load_dotenv

    for _env in (APP_DIR / ".env", APP_DIR.parent / ".env",
                 Path(__file__).resolve().parent.parent / ".env"):
        if _env.is_file():
            load_dotenv(_env, override=False)
            break
except Exception:
    pass

# ---------------------------------------------------------------------------
# SINGLE MOVABLE DATA FOLDER
# All persistent state (SQLite db, uploads, exports, logs) lives under ONE
# directory -- "FinWiseData" by default -- so the whole app's data is movable
# in a single step (copy the folder / USB stick). Override with DATA_DIR.
# Defaults:
#   * DATA_DIR env set          -> use it (absolute or relative to APP_DIR)
#   * bundled (.exe/.app)       -> <next to binary>/FinWiseData
#   * source tree               -> <FinWise root>/FinWiseData
# ---------------------------------------------------------------------------
_data_env = os.getenv("DATA_DIR")
if _data_env:
    DATA_DIR = (APP_DIR / _data_env) if not Path(_data_env).is_absolute() else Path(_data_env)
else:
    DATA_DIR = APP_DIR / "FinWiseData"

DATABASE_DIR = DATA_DIR / "database"
UPLOAD_DIR = DATA_DIR / "uploads"
EXPORT_DIR = DATA_DIR / "exports"
LOG_DIR = DATA_DIR / "logs"

# The SQLite file is the heart of the movable database.
DB_FILE = DATABASE_DIR / "finwise.db"

# Create the whole tree in one shot (idempotent). Moving the app = moving this.
for _d in (DATA_DIR, DATABASE_DIR, UPLOAD_DIR, EXPORT_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def _get_env(key: str, default: str) -> str:
    return os.getenv(key, default)


# SQLAlchemy database URL ----------------------------------------------------
# Default to the single movable SQLite file. To migrate to PostgreSQL later,
# set DATABASE_URL="postgresql+psycopg://user:pass@host:5432/finwise" in .env.
DATABASE_URL = _get_env(
    "DATABASE_URL",
    f"sqlite:///{DB_FILE}",
)

# Make relative SQLite paths portable: resolve them against DATA_DIR so the
# database is found no matter what the current working directory is.
if DATABASE_URL.startswith("sqlite:///"):
    _raw = DATABASE_URL[len("sqlite:///"):]
    _p = Path(_raw)
    if not _p.is_absolute():
        _resolved = (DATA_DIR / _raw.lstrip(".\\/")).resolve()
        _resolved.parent.mkdir(parents=True, exist_ok=True)
        DATABASE_URL = f"sqlite:///{_resolved}"

# Security -------------------------------------------------------------------
SECRET_KEY = _get_env("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(_get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Password policy
PASSWORD_MIN_LENGTH = int(_get_env("PASSWORD_MIN_LENGTH", "8"))

# CORS / frontend ------------------------------------------------------------
FRONTEND_ORIGIN = _get_env("FRONTEND_ORIGIN", "*")

# Default admin seed (created on first startup if no users exist)
DEFAULT_ADMIN_EMAIL = _get_env("DEFAULT_ADMIN_EMAIL", "admin@finwise.app")
DEFAULT_ADMIN_PASSWORD = _get_env("DEFAULT_ADMIN_PASSWORD", "Admin@123456")
DEFAULT_ADMIN_NAME = _get_env("DEFAULT_ADMIN_NAME", "FinWise Admin")

# App behaviour
APP_NAME = "FinWise - Personal Finance Planner"
APP_VERSION = "1.0.0"
DEBUG = _get_env("DEBUG", "false").lower() == "true"

# Rate limiting (requests per window per IP)
RATE_LIMIT_PER_MINUTE = int(_get_env("RATE_LIMIT_PER_MINUTE", "120"))
