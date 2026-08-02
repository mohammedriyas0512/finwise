"""
Password hashing (PBKDF2) and JWT token helpers.

Pure-stdlib implementation (no bcrypt / python-jose) so it runs on Android
via Chaquopy without native wheels. Hashes are stored as:
    pbkdf2_sha256$<iterations>$<salt_hex>$<digest_hex>
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)

_PBKDF2_ITERATIONS = 260000


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def hash_password(password: str) -> str:
    """Return a PBKDF2-SHA256 hash for ``password``."""
    salt = hashlib.sha256(str(time.time_ns()).encode()).digest()[:16]
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Return True if ``password`` matches ``hashed`` (PBKDF2 format)."""
    if not hashed or not isinstance(hashed, str):
        return False
    if hashed.startswith("$2"):  # legacy bcrypt hash (pre-Android DBs)
        try:
            import bcrypt  # type: ignore

            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False
    try:
        _scheme, _iter, salt_hex, digest_hex = hashed.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return hmac.compare_digest(actual, expected)


def create_access_token(subject: str | int, role: str) -> str:
    """Create a signed HS256 JWT carrying the user id and role."""
    header = {"alg": ALGORITHM, "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": str(subject),
        "role": role,
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    signing_input = (
        _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")) + "."
        + _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    )
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return signing_input + "." + _b64url_encode(signature)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT. Returns the payload dict or None."""
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = header_b64 + "." + payload_b64
        expected = hmac.new(SECRET_KEY.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_decode(sig_b64)):
            return None
        payload = json.loads(_b64url_decode(payload_b64))
        if payload.get("exp") is not None and payload["exp"] < time.time():
            return None
        return payload
    except Exception:
        return None
