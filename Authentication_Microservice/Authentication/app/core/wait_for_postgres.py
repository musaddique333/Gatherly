import psycopg2
import time
from psycopg2 import OperationalError
import os

def wait_for_postgres():
    db_host =  os.getenv('POSTGRES_HOST')
    db_port = os.getenv('POSTGRES_PORT')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB')

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
