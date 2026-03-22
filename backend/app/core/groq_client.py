"""
Groq API client — uses centralised settings from config.py
Get your free key at: https://console.groq.com
"""
from groq import Groq

from .config import settings

_client: Groq | None = None


def get_groq_client() -> Groq:
    """Return (or lazily create) the Groq client singleton."""
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Copy backend/.env.example → backend/.env and add your key."
            )
        _client = Groq(api_key=settings.groq_api_key)
        print(f"[INFO] Groq client initialised (model: {settings.groq_default_model})")
    return _client


def call_groq(
    prompt: str,
    system: str = "You are a helpful legal document assistant.",
    max_tokens: int | None = None,
    model: str | None = None,
) -> str:
    """
    Call the Groq chat completion API.

    Args:
        prompt:     User message.
        system:     System instruction prepended to the conversation.
        max_tokens: Max response length (defaults to settings.groq_max_tokens).
        model:      Model override (defaults to settings.groq_default_model).

    Returns:
        Stripped response string.

    Raises:
        RuntimeError: If the Groq API call fails.
    """
    client = get_groq_client()

    _model = model or settings.groq_default_model
    _max_tokens = max_tokens or settings.groq_max_tokens

    try:
        response = client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=_max_tokens,
            temperature=settings.groq_temperature,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR] Groq API call failed (model={_model}): {e}")
        raise RuntimeError(f"Groq API error: {str(e)}")
