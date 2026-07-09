import logging
import os
import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Business Management System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:8081,http://localhost:8080"

    # Environment
    ENVIRONMENT: str = "development"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Upload
    UPLOAD_DIR: str = "uploads"

    # Database
    DATABASE_URL: str = "postgresql://user:password@db:5432/business_db"

    # DIAN
    DIAN_ENVIRONMENT: str = "test"
    DIAN_CERT_PATH: str = ""
    DIAN_CERT_PASSWORD: str = ""

    # UVT 2026 (Colombia) - Valor Unidad de Valor Tributario
    UVT_VALUE: float = 49738.0

    # AI Integration
    GEMINI_API_KEY: str = ""

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-here":
            env = self.ENVIRONMENT
            if env == "production":
                raise ValueError(
                    "SECRET_KEY must be explicitly set in production. "
                    "Generate one with: openssl rand -hex 32"
                )
            elif env == "staging":
                raise ValueError(
                    "SECRET_KEY must be set in staging environment. "
                    "Use a strong random key, different from production."
                )
            else:
                self.SECRET_KEY = secrets.token_hex(32)
                logging.getLogger("app").warning(
                    "SECRET_KEY auto-generated for development. "
                    "Tokens will be invalid after restart. "
                    "Set SECRET_KEY in .env for persistence."
                )
        if len(self.SECRET_KEY) < 32:
            env = self.ENVIRONMENT
            if env in ("production", "staging"):
                raise ValueError(
                    f"SECRET_KEY too short ({len(self.SECRET_KEY)} chars). "
                    "Minimum 32 characters (64 recommended). "
                    "Generate one with: openssl rand -hex 32"
                )
            else:
                logging.getLogger("app").warning(
                    f"SECRET_KEY is too short ({len(self.SECRET_KEY)} chars). "
                    "Auto-generated tokens may be weak. Set a strong key in .env."
                )


settings = Settings()
