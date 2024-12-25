from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables based on the environment
env_file = ".env.development" if os.getenv("ENV") == "development" else ".env.production"
load_dotenv(env_file)

# Print UI if in development environment
if os.getenv("ENV") == "development":
    from .dev_ui import print_ui
    print_ui()

class Settings(BaseSettings):
    """
    Configuration settings class, loads environment variables for application settings.
    Inherits from BaseSettings for Pydantic data validation.
    """
    # JWT settings for authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    # Database connection settings
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")

    # Email settings for sending emails
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME")

    # Redis configuration for caching and task queueing
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")

    # gRPC configuration for the auth microservice
    AUTH_SERVICE_HOST: str = os.getenv("AUTH_SERVICE_HOST")
    AUTH_SERVICE_PORT: int = os.getenv("AUTH_SERVICE_PORT")

    @property
    def SUPABASE_DATABASE_URL(self) -> str:
        """
        Returns the database connection URL for Supabase using the environment variables.
        """
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def CELERY_BROKER(self) -> str:
        """
        Returns the celery broker connection URL for redis using the environment variables.
        """
        return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    
    @property
    def CELERY_BACKEND_URL(self) -> str:
        """
        Returns the celery backend connection URL for redis using the environment variables.
        """
        return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

    class Config:
        env_file = ".env" 

# Instantiate the settings object
settings = Settings()
