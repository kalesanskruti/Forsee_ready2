from typing import List, Optional, Union, Any
from pydantic import AnyHttpUrl, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    @model_validator(mode='after')
    def assemble_db_connection(self) -> 'Settings':
        if self.DATABASE_URL:
            return self
        
        if not all([self.POSTGRES_SERVER, self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
             # Fallback or error if neither URL nor params provided. 
             # For now, let's assume if URL is missing and params missing, we can't construct it.
             # But init_sqlite sets DATABASE_URL via env/file usually.
             pass
        else:
            self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        return self

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_GROUP_ID: str

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None

    PROMETHEUS_PORT: int = 9090
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra='ignore')

settings = Settings()
