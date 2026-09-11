import os
import secrets
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, EmailStr, HttpUrl, computed_field
from pydantic_settings import SettingsConfigDict

# Point to the project root where .env exists
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='../.env',
        env_ignore_empty=True,
        extra="ignore"
    )

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY_2: str = secrets.token_urlsafe(24)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # App
    API_V1_STR: str = '/fast/v1'
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    PROJECT_VERSION: str
    DEBUG: bool
    ENVIRONMENT: Literal['development', 'production', 'testing'] = 'development'
    SERVER_HOST: str = 'http://localhost:8000'
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # Database
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Superuser
    SUPER_USER_EMAIL: EmailStr
    SUPER_USER_PASSWORD: str
    SUPER_USER_NAME: str
    SUPER_USER_ROLE: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=f"/{self.POSTGRES_DB}"
        )

    # Email
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str| None = None
    FRONTEND_HOST: str

    @property
    def email_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)


settings = Settings()