from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from the appropriate .env file
env_file = ".env.development" if os.getenv("ENV") == "development" else ".env.production"
load_dotenv(env_file)

if os.getenv("ENV") == "development":
    from .dev_ui import print_ui
    print_ui()

class Settings(BaseSettings):
    # JWT env variables
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    # Database env variables
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")

    # Email verification env variables
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM")

    @property
    def SUPABASE_DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()
