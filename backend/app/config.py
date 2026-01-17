from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL database URL, e.g. postgresql+psycopg2://user:password@localhost:5432/honeyshield
    DATABASE_URL: str = "postgresql+psycopg2://honeyshield:honeyshield@localhost:5432/honeyshield"

    # FastAPI app settings
    API_PREFIX: str = "/api"
    BACKEND_BASE_URL: str = "http://127.0.0.1:8000"

    # Honeypot settings
    HONEYPOT_LISTEN_HOST: str = "0.0.0.0"
    HONEYPOT_LISTEN_PORT: int = 2222

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
