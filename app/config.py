from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ai-photo-telegram-bot"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    app_base_url: str = "http://localhost:8080"

    telegram_mode: str = Field(default="polling")
    telegram_bot_token: str
    telegram_webhook_url: str | None = None
    telegram_webhook_secret: str = "change_me_secret"

    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    log_level: str = "INFO"

    media_dir: Path = Path("./data/media")
    input_dir: Path = Path("./data/media/input")
    output_dir: Path = Path("./data/media/output")
    temp_dir: Path = Path("./data/media/temp")

    remove_bg_api_key: str = ""
    remove_bg_api_url: str = "https://api.remove.bg/v1.0/removebg"
    remove_bg_timeout_seconds: int = 60

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_api_url: str = "https://generativelanguage.googleapis.com/v1beta/models"
    gemini_timeout_seconds: int = 45

    max_history_items: int = 10
    template_seed_path: Path = Path("./app/prompt_templates/trend_templates.json")

    image_provider: str = "multi"
    image_provider_chain: str = "replicate,fal"
    image_provider_primary_by_mode: str = "avatar:replicate,poster:replicate,product:replicate,stickers:fal"

    admin_telegram_ids: str = ""

    replicate_api_token: str = ""
    replicate_model_ref: str = "black-forest-labs/flux-kontext-max"

    fal_key: str = ""
    fal_model_ref: str = "fal-ai/nano-banana/edit"

    @property
    def webhook_path(self) -> str:
        return "/api/webhook/telegram"

    @property
    def webhook_full_url(self) -> str:
        base = (self.telegram_webhook_url or self.app_base_url).rstrip("/")
        return f"{base}{self.webhook_path}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
