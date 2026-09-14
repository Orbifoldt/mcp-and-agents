import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


class AzureLlmConfig(BaseModel):
    """Configuration for an Azure-hosted language model deployment."""

    model_config = ConfigDict(frozen=True)

    deployment_name: Literal["paygo-gpt-5.6-luna"] = "paygo-gpt-5.6-luna"
    name: Literal["gpt-5.6-luna"] = "gpt-5.6-luna"
    api_version: Literal["2024-12-01-preview"] = "2024-12-01-preview"


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a .env file."""

    llm_endpoint: str
    azure_tenant_id: str
    azure_npa_client_id: str
    azure_npa_client_secret: SecretStr
    gpt_5_6_luna: AzureLlmConfig = AzureLlmConfig()

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide application settings instance."""

    env_file = Path(os.getenv("SETTINGS_ENV_FILE", DEFAULT_ENV_FILE))
    if not env_file.is_absolute():
        env_file = PROJECT_ROOT / env_file

    return Settings(_env_file=env_file)


settings = get_settings()
