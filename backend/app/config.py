from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./arthapilot.db"
    anthropic_api_key: str = ""
    claude_model: str = ""
    llm_provider: str = ""
    next_public_api_url: str = ""
    upload_max_size_mb: int = 10

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
