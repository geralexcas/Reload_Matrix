import os
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
            if os.getenv("ENVIRONMENT", "development") == "production":
                raise ValueError(
                    "SECRET_KEY must be set in production. "
                    "Generate one with: openssl rand -hex 32"
                )


settings = Settings()
