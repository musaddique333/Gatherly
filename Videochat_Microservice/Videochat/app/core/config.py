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
    # MongoDB connection settings
    MONGO_USERNAME: str =  os.getenv("MONGO_USERNAME")
    MONGO_PASSWORD: str =  os.getenv("MONGO_PASSWORD")
    MONGO_PORT: int =  os.getenv("MONGO_PORT")
    MONGO_HOST: str =  os.getenv("MONGO_HOST")
    MONGO_DB: str = os.getenv("MONGO_DB")
    MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION")
    ENCRYPTION_KEY: str =  os.getenv("ENCRYPTION_KEY")

    @property
    def MONGODB_URL(self) -> str:
        """
        Returns the celery backend connection URL for mongodb using the environment variables.
        """
        return f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/"

    class Config:
        env_file = ".env" 

# Instantiate the settings object
settings = Settings()