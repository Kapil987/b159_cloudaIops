from __future__ import annotations

from dotenv import load_dotenv
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    servicenow_instance: str = Field(..., alias="SERVICENOW_INSTANCE")
    servicenow_username: str = Field(..., alias="SERVICENOW_USERNAME")
    servicenow_password: SecretStr = Field(..., alias="SERVICENOW_PASSWORD")
    servicenow_timeout_seconds: float = Field(30.0, alias="SERVICENOW_TIMEOUT_SECONDS")

    @field_validator("servicenow_instance")
    @classmethod
    def normalize_instance(cls, value: str) -> str:
        instance = value.strip().rstrip("/")
        if not instance:
            raise ValueError("SERVICENOW_INSTANCE cannot be empty")
        if not instance.startswith(("http://", "https://")):
            instance = f"https://{instance}"
        return instance


load_dotenv()
settings = Settings()
