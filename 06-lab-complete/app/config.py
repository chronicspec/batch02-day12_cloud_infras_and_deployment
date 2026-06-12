from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VinWonders AI Assistant Prototype"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    data_dir: str = "data"
    llm_timeout_seconds: int = Field(default=15, ge=1)
    low_confidence_distance_m: int = Field(default=800, ge=1)
    llm_enabled: bool = False
    llm_provider: str = "auto"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_intent_model: str = ""
    llm_response_model: str = ""
    
    # Production Settings
    environment: str = "development"
    agent_api_key: str = "dev-key-change-me"
    rate_limit_per_minute: int = 20
    daily_budget_usd: float = 5.0
    redis_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
