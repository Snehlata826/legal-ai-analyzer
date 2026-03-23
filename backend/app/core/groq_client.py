"""
Groq API client — production-safe version (Groq 0.9.0 compatible)
Fixes:
- Proxy injection issue (Railway/httpx)
- Prevents 500 errors with fallback
"""

from groq import Groq
import os
from .config import settings

_client: Groq | None = None


def get_groq_client() -> Groq:
    """Return (or lazily create) the Groq client singleton."""
    global _client

    if _client is None:
        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it in your .env or Railway variables."
            )

        # 🚨 CRITICAL FIX: Remove proxy env vars (causes Groq crash)
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)

        # ✅ Initialize Groq client safely
        _client = Groq(api_key=settings.groq_api_key)

        print(f"[INFO] Groq client initialized (model: {settings.groq_default_model})")

    return _client


def call_groq(
    prompt: str,
    system: str = "You are a helpful legal document assistant.",
    max_tokens: int | None = None,
    model: str | None = None,
) -> str:
    """
    Call the Groq chat completion API with safe fallback.

    Returns:
        Response string (never crashes backend).
    """
    client = get_groq_client()

    _model = model or settings.groq_default_model
    _max_tokens = max_tokens or settings.groq_max_tokens

    try:
        response = client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=_max_tokens,
            temperature=settings.groq_temperature,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        # ❌ DO NOT crash backend
        print(f"[ERROR] Groq API call failed (model={_model}): {e}")

        # ✅ Safe fallback response
        return "AI service temporarily unavailable. Please try again later."
