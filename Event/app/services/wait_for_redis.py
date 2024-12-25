import redis
import time
from app.core.config import settings

def wait_for_redis():
    redis_host = settings.REDIS_HOST
    redis_port = settings.REDIS_PORT

    while True:
        try:
            client = redis.StrictRedis(host=redis_host, port=redis_port)
            client.ping()
            print("Redis is ready!")
            break
        except redis.ConnectionError:
            print("Redis is not ready yet, retrying...")
            time.sleep(5)
