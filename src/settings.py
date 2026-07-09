"""Centralized configuration loaded from environment and .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env or environment variables.

    Attributes:
        openrouter_api_key: API key for OpenRouter.
        openrouter_model: Model identifier to use for extraction.
        openrouter_base: Base URL for the OpenRouter API.
        data_raw_dir: Directory containing raw documentation files.
        data_processed_dir: Directory for extracted/validated triple output.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_base: str = "https://openrouter.ai/api/v1"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    data_raw_dir: str = "data/raw"
    data_processed_dir: str = "data/processed"


settings = Settings()
