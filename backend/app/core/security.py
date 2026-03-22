"""
Security layer for Legal AI Analyzer.

Provides:
  - Rate limiting (per-IP sliding window, in-memory)
  - Security headers (CSP, HSTS, X-Frame-Options, etc.)
  - Request ID injection (for tracing)
  - Slow-down detection (too many 4xx responses from same IP)
  - Input sanitization helpers
  - File validation helpers
"""
from __future__ import annotations

import re
import time
import uuid
import hashlib
import logging
from collections import defaultdict, deque
from typing import Callable, Dict, Deque

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import settings

logger = logging.getLogger("lexanalyze.security")

# ── Allowed MIME types for uploads ────────────────────────────────
ALLOWED_MIME_TYPES = {"application/pdf"}

# PDF magic bytes
PDF_MAGIC = b"%PDF-"

# Maximum question / text input lengths
MAX_QUESTION_LEN = 500
MAX_TEXT_INPUT_LEN = 10_000


# ══════════════════════════════════════════════════════════════════
#  Rate Limiter (sliding window, in-memory)
# ══════════════════════════════════════════════════════════════════

class _SlidingWindow:
    """Thread-safe sliding-window counter for a single IP."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self._timestamps: Deque[float] = deque()

    def is_allowed(self) -> bool:
        now = time.monotonic()
        cutoff = now - self.window

        # Purge expired timestamps
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

        if len(self._timestamps) >= self.limit:
            return False

        self._timestamps.append(now)
        return True

    def remaining(self) -> int:
        now = time.monotonic()
        cutoff = now - self.window
        active = sum(1 for t in self._timestamps if t >= cutoff)
        return max(0, self.limit - active)

    def reset_at(self) -> float:
        """Epoch seconds when the oldest request expires."""
        if self._timestamps:
            return time.time() + (self._timestamps[0] - time.monotonic() + self.window)
        return time.time() + self.window


class RateLimiter:
    """
    Per-IP rate limiter with two tiers:
      - global:  N requests / minute across all endpoints
      - upload:  stricter limit for /upload (expensive endpoint)
    """

    def __init__(self):
        # {ip: _SlidingWindow}
        self._global:  Dict[str, _SlidingWindow] = defaultdict(
            lambda: _SlidingWindow(
                limit=settings.rate_limit_global,
                window_seconds=60,
            )
        )
        self._upload: Dict[str, _SlidingWindow] = defaultdict(
            lambda: _SlidingWindow(
                limit=settings.rate_limit_upload,
                window_seconds=60,
            )
        )
        # Track 4xx counts per IP to detect abuse
        self._abuse: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=20)
        )

    def check_global(self, ip: str) -> tuple[bool, int, float]:
        """Returns (allowed, remaining, reset_at)."""
        win = self._global[ip]
        allowed = win.is_allowed()
        return allowed, win.remaining(), win.reset_at()

    def check_upload(self, ip: str) -> tuple[bool, int, float]:
        win = self._upload[ip]
        allowed = win.is_allowed()
        return allowed, win.remaining(), win.reset_at()

    def record_abuse(self, ip: str) -> None:
        self._abuse[ip].append(time.monotonic())

    def is_abusive(self, ip: str) -> bool:
        """True if IP sent >= 10 error responses in the last 60 s."""
        now = time.monotonic()
        recent = [t for t in self._abuse[ip] if now - t < 60]
        return len(recent) >= 10


# Module-level singleton
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    return _rate_limiter


# ══════════════════════════════════════════════════════════════════
#  Security Headers Middleware
# ══════════════════════════════════════════════════════════════════

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to every response and injects a unique
    X-Request-ID for request tracing.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Attach a unique ID to this request
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response: Response = await call_next(request)

        # ── Security headers ──────────────────────────────────────
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Only set HSTS in production (not on localhost)
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Content-Security-Policy — tight for an API (no HTML served)
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; "
            "frame-ancestors 'none';"
        )

        # Never cache sensitive API responses
        if request.url.path not in ("/health", "/"):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, private"
            )
            response.headers["Pragma"] = "no-cache"

        return response


# ══════════════════════════════════════════════════════════════════
#  Rate Limiting Middleware
# ══════════════════════════════════════════════════════════════════

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Enforces per-IP rate limits and detects abusive clients.
    Returns 429 with Retry-After header when the limit is exceeded.
    """

    # Paths that bypass rate limiting (health checks, docs)
    _EXEMPT = {"/health", "/", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self._EXEMPT:
            return await call_next(request)

        ip = _get_client_ip(request)
        rl = get_rate_limiter()

        # ── Abuse check ───────────────────────────────────────────
        if rl.is_abusive(ip):
            logger.warning("Abusive IP blocked: %s", ip)
            return _rate_limit_response(
                retry_after=60,
                detail="Too many errors. Your IP has been temporarily blocked.",
            )

        # ── Upload-specific limit ─────────────────────────────────
        if request.url.path.startswith("/upload"):
            allowed, remaining, reset_at = rl.check_upload(ip)
            if not allowed:
                retry = max(1, int(reset_at - time.time()))
                logger.warning("Upload rate limit hit: %s", ip)
                return _rate_limit_response(
                    retry_after=retry,
                    detail=(
                        f"Upload limit reached "
                        f"({settings.rate_limit_upload}/min). "
                        f"Please wait {retry}s."
                    ),
                )

        # ── Global limit ──────────────────────────────────────────
        allowed, remaining, reset_at = rl.check_global(ip)
        if not allowed:
            retry = max(1, int(reset_at - time.time()))
            logger.warning("Global rate limit hit: %s", ip)
            return _rate_limit_response(
                retry_after=retry,
                detail=(
                    f"Rate limit exceeded "
                    f"({settings.rate_limit_global}/min). "
                    f"Please wait {retry}s."
                ),
            )

        response: Response = await call_next(request)

        # Record abuse on 4xx (except 401/403 which are normal auth flows)
        if 400 <= response.status_code < 500 and response.status_code not in (401, 403):
            rl.record_abuse(ip)

        # Expose rate-limit headers
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_global)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_at))

        return response


# ══════════════════════════════════════════════════════════════════
#  Request Logging Middleware
# ══════════════════════════════════════════════════════════════════

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured request/response logging with timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        ip = _get_client_ip(request)

        response: Response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000
        request_id = getattr(request.state, "request_id", "-")

        logger.info(
            "%s %s %s | %dms | ip=%s | req=%s",
            request.method,
            request.url.path,
            response.status_code,
            int(elapsed_ms),
            _anonymise_ip(ip),
            request_id,
        )

        return response


# ══════════════════════════════════════════════════════════════════
#  Input validation helpers  (used in routers)
# ══════════════════════════════════════════════════════════════════

def validate_question(text: str) -> str:
    """
    Sanitise and validate a Q&A question string.
    Raises HTTPException 400 on invalid input.
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    text = text.strip()

    if len(text) > MAX_QUESTION_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"Question too long. Maximum {MAX_QUESTION_LEN} characters.",
        )

    # Strip potentially dangerous characters but keep punctuation
    text = _strip_control_chars(text)

    # Reject obvious prompt-injection patterns
    _check_prompt_injection(text)

    return text


def validate_request_id(request_id: str) -> str:
    """Ensure request_id is a valid UUID4 string."""
    _UUID_RE = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    if not _UUID_RE.match(request_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid request_id format.",
        )
    return request_id


def validate_upload_file(filename: str, content: bytes, content_type: str) -> None:
    """
    Validate an uploaded file:
      - Extension must be .pdf
      - Content-Type must be application/pdf
      - File must start with PDF magic bytes
      - Must not be empty
    Raises HTTPException on failure.
    """
    if not filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only .pdf files are accepted.",
        )

    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type '{content_type}'. Only PDF is accepted.",
        )

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if not content.startswith(PDF_MAGIC):
        raise HTTPException(
            status_code=400,
            detail="File does not appear to be a valid PDF (bad magic bytes).",
        )


# ══════════════════════════════════════════════════════════════════
#  Private helpers
# ══════════════════════════════════════════════════════════════════

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now",
    r"disregard\s+(your\s+)?instructions",
    r"act\s+as\s+(if\s+you\s+are|a)",
    r"<\s*script",
    r"system\s*:",
    r"\[INST\]",
    r"###\s*instruction",
]

_INJECTION_RE = re.compile(
    "|".join(_INJECTION_PATTERNS),
    re.IGNORECASE,
)


def _check_prompt_injection(text: str) -> None:
    if _INJECTION_RE.search(text):
        raise HTTPException(
            status_code=400,
            detail="Input contains disallowed patterns.",
        )


def _strip_control_chars(text: str) -> str:
    """Remove ASCII control characters except newline and tab."""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)


def _get_client_ip(request: Request) -> str:
    """Extract real client IP, respecting common reverse-proxy headers."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first (leftmost) IP — that's the real client
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return "unknown"


def _anonymise_ip(ip: str) -> str:
    """Hash the IP for privacy-safe logging."""
    return hashlib.sha256(ip.encode()).hexdigest()[:12]


def _rate_limit_response(retry_after: int, detail: str) -> Response:
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={"detail": detail},
        headers={"Retry-After": str(retry_after)},
    )
