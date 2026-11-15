"""Settings: reads .env / env vars, validates, hides the password."""
from __future__ import annotations

from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env is looked up next to this file, not in the current working directory,
# so it works no matter where the Host launches the server from.
ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    servicenow_instance: str = Field(..., alias="SERVICENOW_INSTANCE")
    servicenow_username: str = Field(..., alias="SERVICENOW_USERNAME")
    servicenow_password: SecretStr = Field(..., alias="SERVICENOW_PASSWORD")
    servicenow_timeout_seconds: float = Field(30.0, alias="SERVICENOW_TIMEOUT_SECONDS")

    # Where this MCP server listens. Localhost by default: the server holds your ServiceNow
    # credentials and has no login of its own, so do not expose it 
    mcp_host: str = Field("127.0.0.1", alias="MCP_HOST")
    mcp_port: int = Field(8000, alias="MCP_PORT")

    @field_validator("servicenow_instance")
    @classmethod
    def normalize_instance(cls, value: str) -> str:
        instance = value.strip().rstrip("/")
        if not instance:
            raise ValueError("SERVICENOW_INSTANCE cannot be empty")
        if not instance.startswith(("http://", "https://")):
            instance = f"https://{instance}"
        return instance


settings = Settings()  # fails fast at startup if anything is missing
