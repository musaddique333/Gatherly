import psycopg2
import time
from psycopg2 import OperationalError
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_postgres():
    """
    Wait for PostgreSQL to become available by continuously attempting to connect.

    This function tries to establish a connection to the PostgreSQL database.
    If the connection fails, it retries every 5 seconds until successful.

    Raises:
        TimeoutError: If PostgreSQL cannot be reached within a reasonable time.
    """
    db_host = settings.DB_HOST
    db_port = settings.DB_PORT
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_name = settings.DB_NAME

    max_retries = 30  # Max number of retries before giving up
    retries = 0

    while retries < max_retries:
        try:
            # Attempt to connect to the PostgreSQL database
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                dbname=db_name
            )
            conn.close()
            logger.info("PostgreSQL is ready!")
            return  # Exit the function if the connection is successful
        except OperationalError as e:
            retries += 1
            logger.warning(f"PostgreSQL is not ready yet, retrying... (Attempt {retries}/{max_retries})")
            time.sleep(5)  # Wait before retrying

    # If maximum retries are exceeded, raise an exception
    logger.error("PostgreSQL is not ready after multiple attempts.")
    raise TimeoutError("PostgreSQL is not available after multiple retries.")