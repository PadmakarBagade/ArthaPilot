from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./arthapilot.db"
    cors_origins: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000"
    data_dir: str = ""
    seed_demo: bool = True
    llm_provider: str = "none"
    llm_model: str = ""
    llm_base_url: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    claude_model: str = ""
    next_public_api_url: str = ""
    upload_max_size_mb: int = 10
    chat_rate_limit_per_min: int = 10
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> List[str]:
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def resolved_data_dir(self) -> Path:
        if self.data_dir:
            return Path(self.data_dir)
        # default to repo data directory
        return Path(__file__).resolve().parents[2] / "data"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
