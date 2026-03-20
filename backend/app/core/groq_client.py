"""
Groq API client - Free, fast LLM API
Get your free key at: https://console.groq.com
"""
import os
from groq import Groq

_client = None


def get_groq_client() -> Groq:
    """Get or create Groq client singleton"""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not set in .env file. "
                "Get your free key at https://console.groq.com"
            )
        _client = Groq(api_key=api_key)
        print("[INFO] Groq client initialized")
    return _client


def call_groq(
    prompt: str,
    system: str = "You are a helpful legal document assistant.",
    max_tokens: int = 500,
    model: str = "llama3-8b-8192"
) -> str:
    """
    Call Groq API with a prompt.

    Free models available:
    - llama3-8b-8192     (fastest, good quality)
    - llama3-70b-8192    (best quality, slightly slower)
    - mixtral-8x7b-32768 (good for long documents)
    - gemma-7b-it        (Google's model)

    Args:
        prompt: User message
        system: System instruction
        max_tokens: Max response length
        model: Model to use

    Returns:
        Response text string
    """
    client = get_groq_client()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR] Groq API call failed: {e}")
        raise RuntimeError(f"Groq API error: {str(e)}")
