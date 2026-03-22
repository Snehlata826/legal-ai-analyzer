"""
Centralized application configuration using environment variables.
All settings are loaded once at startup from .env file.
"""
import os
from functools import lru_cache
from typing import List


class Settings:
    """
    Application settings — loaded from environment variables / .env file.
    Access via: from app.core.config import settings
    """

    # ── API ──────────────────────────────────────────────
    app_name: str = "Legal AI Analyzer"
    app_version: str = "2.0.0"
    debug: bool = False

    # ── Server ───────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8001

    # ── CORS ─────────────────────────────────────────────
    # Comma-separated origins, e.g. "http://localhost:5173,https://myapp.com"
    allowed_origins_raw: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ── Groq ─────────────────────────────────────────────
    groq_api_key: str = ""
    groq_default_model: str = "llama3-8b-8192"
    groq_max_tokens: int = 500
    groq_temperature: float = 0.3

    # ── Document processing ───────────────────────────────
    max_upload_size_mb: int = 10
    max_clauses_per_doc: int = 50
    clause_min_length: int = 20

    # ── Report storage ────────────────────────────────────
    report_output_dir: str = "temp_reports"

    # ── Security / Rate limiting ──────────────────────────
    # Max requests per IP per minute (all endpoints combined)
    rate_limit_global: int = 60
    # Max upload requests per IP per minute (expensive endpoint)
    rate_limit_upload: int = 5
    # Trusted reverse-proxy IPs (comma-separated) — skip rate limit for these
    trusted_proxies_raw: str = "127.0.0.1,::1"

    def __init__(self):
        # Pull every value from the real environment at instantiation time
        self.app_name = os.getenv("APP_NAME", self.app_name)
        self.app_version = os.getenv("APP_VERSION", self.app_version)
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", str(self.port)))

        self.allowed_origins_raw = os.getenv(
            "ALLOWED_ORIGINS", self.allowed_origins_raw
        )

        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.groq_default_model = os.getenv(
            "GROQ_DEFAULT_MODEL", self.groq_default_model
        )
        self.groq_max_tokens = int(
            os.getenv("GROQ_MAX_TOKENS", str(self.groq_max_tokens))
        )
        self.groq_temperature = float(
            os.getenv("GROQ_TEMPERATURE", str(self.groq_temperature))
        )

        self.max_upload_size_mb = int(
            os.getenv("MAX_UPLOAD_SIZE_MB", str(self.max_upload_size_mb))
        )
        self.max_clauses_per_doc = int(
            os.getenv("MAX_CLAUSES_PER_DOC", str(self.max_clauses_per_doc))
        )
        self.clause_min_length = int(
            os.getenv("CLAUSE_MIN_LENGTH", str(self.clause_min_length))
        )

        self.report_output_dir = os.getenv(
            "REPORT_OUTPUT_DIR", self.report_output_dir
        )

        self.rate_limit_global = int(
            os.getenv("RATE_LIMIT_GLOBAL", str(self.rate_limit_global))
        )
        self.rate_limit_upload = int(
            os.getenv("RATE_LIMIT_UPLOAD", str(self.rate_limit_upload))
        )
        self.trusted_proxies_raw = os.getenv(
            "TRUSTED_PROXIES", self.trusted_proxies_raw
        )

    @property
    def allowed_origins(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        return [
            o.strip()
            for o in self.allowed_origins_raw.split(",")
            if o.strip()
        ]

    @property
    def trusted_proxies(self) -> list:
        return [p.strip() for p in self.trusted_proxies_raw.split(",") if p.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    def validate(self) -> None:
        """
        Validate critical settings at startup.
        Raises ValueError if required config is missing.
        """
        if not self.groq_api_key:
            raise ValueError(
                "\n\n"
                "  ❌  GROQ_API_KEY is not set!\n"
                "  ─────────────────────────────────────────────\n"
                "  1. Get your FREE key at: https://console.groq.com\n"
                "  2. Copy backend/.env.example  →  backend/.env\n"
                "  3. Paste your key:  GROQ_API_KEY=gsk_...\n"
                "  4. Restart the server.\n"
            )

    def __repr__(self) -> str:
        key_preview = (
            f"{self.groq_api_key[:8]}..." if self.groq_api_key else "NOT SET"
        )
        return (
            f"Settings("
            f"version={self.app_version}, "
            f"debug={self.debug}, "
            f"model={self.groq_default_model}, "
            f"groq_key={key_preview}, "
            f"origins={self.allowed_origins}"
            f")"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.
    Called once; result is reused for the lifetime of the process.
    """
    return Settings()


# Module-level convenience alias — import this everywhere:
#   from app.core.config import settings
settings = get_settings()