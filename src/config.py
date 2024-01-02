from __future__ import annotations
from typing import Any, List, Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings

from constants import Environment


class Config(BaseSettings):
    DATABASE_URL: str = "sqlite:///databases/efdatabase.db"
    SITE_DOMAIN: str = "charan-ef-test.com"

    ENVIRONMENT: Environment = Environment.PRODUCTION

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_ORIGINS_REGEX: Optional[str] = None
    CORS_HEADERS: List[str] = ["*"]

    APP_VERSION: str = "0.1"


settings = Config()

app_configs: dict[str, Any] = {"title": "App API"}
# if settings.ENVIRONMENT.is_deployed:
#     app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs