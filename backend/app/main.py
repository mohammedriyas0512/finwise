"""
FinWise FastAPI application entry point.

On startup it:
  * creates all database tables (idempotent),
  * seeds default categories + the first admin user,
  * mounts the built React frontend (if present) for single-binary serving.

Centralised exception handlers return consistent JSON error envelopes so the
frontend can render friendly error states.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.exc import IntegrityError

from app.api import api_router
from app.config import (
    APP_NAME,
    APP_VERSION,
    DEBUG,
    FRONTEND_ORIGIN,
)
from app.database.database import create_tables
from app.middleware.ratelimit import RateLimitMiddleware
from app.models import Base
from app.schemas import HealthResponse
from app.services.seed_service import seed_admin, seed_default_categories

logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("finwise")

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
# Allow override when bundled as a single executable (FinWise/backend/run.py sets this).
if os.getenv("FINWISE_FRONTEND_DIST"):
    FRONTEND_DIST = Path(os.environ["FINWISE_FRONTEND_DIST"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FinWise starting up — ensuring database schema exists...")
    create_tables()
    # Seed within a short-lived session.
    from app.database.database import SessionLocal

    with SessionLocal() as db:
        seed_default_categories(db)
        seed_admin(db)
    logger.info("Startup complete.")
    yield
    logger.info("FinWise shutting down.")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Secure full-stack personal finance management API.",
    lifespan=lifespan,
    debug=DEBUG,
)

# CORS ----------------------------------------------------------------------
if FRONTEND_ORIGIN == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in FRONTEND_ORIGIN.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True if FRONTEND_ORIGIN != "*" else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting --------------------------------------------------------------
app.add_middleware(RateLimitMiddleware)

# Routers --------------------------------------------------------------------
app.include_router(api_router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    return HealthResponse(status="ok", app_name=APP_NAME, version=APP_VERSION)


# Centralized error handling -------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    logger.warning("Integrity error: %s", exc)
    return JSONResponse(
        status_code=409,
        content={"detail": "A record with the same unique value already exists."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# Serve the built frontend (single binary) -----------------------------------
if FRONTEND_DIST.exists():
    from fastapi.responses import FileResponse

    index_file = FRONTEND_DIST / "index.html"

    # Static assets (hashed) served directly.
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets"), html=False),
        name="assets",
    )
    # Any non-API GET route falls back to index.html (SPA client-side routing).
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        # API paths should never reach here, but guard anyway.
        if full_path.startswith("api/") or full_path.startswith("docs"):
            raise HTTPException(status_code=404, detail="Not found")
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(index_file))
else:
    @app.get("/", tags=["System"])
    def root():
        return {
            "app": APP_NAME,
            "version": APP_VERSION,
            "docs": "/docs",
            "note": "Frontend build not found. Run `npm run build` in frontend/.",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
