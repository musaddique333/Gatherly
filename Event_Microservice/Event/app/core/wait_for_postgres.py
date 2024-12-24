import psycopg2
import time
from psycopg2 import OperationalError
from app.core.config import settings
import os

def wait_for_postgres():
    db_host =  settings.DB_HOST
    db_port = settings.DB_PORT
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_name = settings.DB_NAME

    while True:
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                dbname=db_name
            )
            conn.close()
            print("PostgreSQL is ready!")
            break
        except OperationalError:
            print("PostgreSQL is not ready yet, retrying...")
            time.sleep(5)
