import time
import logging
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError  # Use ServerSelectionTimeoutError instead of ConnectionError
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_mongo():
    """
    Wait for MongoDB to become available by continuously attempting to connect.

    This function tries to establish a connection to the MongoDB database.
    If the connection fails, it retries every 5 seconds until successful.

    Raises:
        TimeoutError: If MongoDB cannot be reached within a reasonable time.
    """
    db_host = settings.MONGO_HOST
    db_port = settings.MONGO_PORT
    db_user = settings.MONGO_USERNAME
    db_password = settings.MONGO_PASSWORD

    max_retries = 30  # Max number of retries before giving up
    retries = 0

    while retries < max_retries:
        try:
            # Create a MongoDB client and attempt to connect
            client = MongoClient(
                f"mongodb://{db_user}:{db_password}@{db_host}:{db_port}",
                serverSelectionTimeoutMS=5000  # Timeout after 5 seconds if not connected
            )
            # Check if the client is connected by pinging the server
            client.admin.command('ping')
            logger.info("MongoDB is ready!")
            return  # Exit the function if the connection is successful
        except ServerSelectionTimeoutError as e:  # Use ServerSelectionTimeoutError
            retries += 1
            logger.warning(f"MongoDB is not ready yet, retrying... (Attempt {retries}/{max_retries})")
            time.sleep(5)  # Wait before retrying

    # If maximum retries are exceeded, raise an exception
    logger.error("MongoDB is not ready after multiple attempts.")
    raise TimeoutError("MongoDB is not available after multiple retries.")
