from pydantic_settings import BaseSettings
from typing import Optional
from datetime import date


class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    openai_org_id: Optional[str] = None
    serpapi_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    model_name: str = "gpt-4o-mini"
    google_model: str = "gemini-2.5-flash"
    anthropic_model: str = "claude-haiku-4-5"
    groq_model: str = "llama-3.3-70b-versatile"
    # Force a provider: "auto" | "anthropic" | "groq" | "google" | "openai" | "none".
    # "auto" precedence: anthropic > groq > google > openai. Set explicitly to avoid surprises.
    llm_provider: str = "auto"
    debug: bool = True

    # All deadline math (urgency, days-left) is computed against this fixed date so the
    # demo is deterministic and never shows past-due dates. Pinned just before the
    # earliest seed deadline (2026-01-15) so every opportunity is future-dated and the
    # nearest one reads as a genuine urgency signal. Override via DEMO_REFERENCE_DATE
    # env var, or set to null to fall back to the real system clock.
    demo_reference_date: Optional[date] = date(2026, 1, 5)

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Settings()


def reference_today() -> date:
    """The 'today' used for all deadline math. Falls back to the real date if unset."""
    return settings.demo_reference_date or date.today()