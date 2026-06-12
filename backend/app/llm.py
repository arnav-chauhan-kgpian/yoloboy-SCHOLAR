from app.config import settings
from typing import Optional
import json
import re

_llm_cache = None


def _make_anthropic():
    if not settings.anthropic_api_key:
        return None
    from langchain_anthropic import ChatAnthropic
    # NOTE: do NOT pass temperature — Claude Opus 4.8/4.7 reject sampling params (400).
    # Omitting it lets ChatAnthropic skip the field entirely.
    return ChatAnthropic(
        model=settings.anthropic_model,
        anthropic_api_key=settings.anthropic_api_key,
        max_tokens=4096,
    )


def _make_groq():
    if not settings.groq_api_key:
        return None
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=settings.groq_model,
        temperature=0,
        groq_api_key=settings.groq_api_key,
    )


def _make_google():
    if not settings.google_api_key:
        return None
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=settings.google_model,
        temperature=0,
        google_api_key=settings.google_api_key,
    )


def _make_openai():
    if not settings.openai_api_key:
        return None
    from langchain_openai import ChatOpenAI
    kwargs = {
        "model": settings.model_name,
        "temperature": 0,
        "openai_api_key": settings.openai_api_key,
    }
    if settings.openai_org_id:
        kwargs["openai_organization"] = settings.openai_org_id
    return ChatOpenAI(**kwargs)


def get_llm_or_none() -> Optional[object]:
    """Return a chat model based on LLM_PROVIDER, else None (deterministic mode).

    provider="auto" detects by key with precedence anthropic > google > openai.
    An explicit provider only uses that provider's key — no surprise fallbacks.
    """
    global _llm_cache
    if _llm_cache is not None:
        return _llm_cache if _llm_cache is not False else None

    provider = (settings.llm_provider or "auto").lower()
    builders = {
        "anthropic": _make_anthropic,
        "groq": _make_groq,
        "google": _make_google,
        "openai": _make_openai,
    }

    try:
        if provider == "none":
            llm = None
        elif provider in builders:
            llm = builders[provider]()
        else:  # auto
            llm = _make_anthropic() or _make_groq() or _make_google() or _make_openai()
    except Exception:
        llm = None

    _llm_cache = llm if llm is not None else False
    return llm


def llm_available() -> bool:
    return get_llm_or_none() is not None


def parse_json_response(content) -> object:
    """Parse JSON from a chat model response, tolerating markdown code fences.

    Gemini (and sometimes others) wrap JSON in ```json ... ``` blocks despite
    instructions; this strips them before parsing.
    """
    if isinstance(content, list):
        # Some providers return content as a list of parts.
        content = "".join(part if isinstance(part, str) else part.get("text", "") for part in content)
    text = str(content).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)
