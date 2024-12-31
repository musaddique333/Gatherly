from pymongo import AsyncMongoClient
from app.core.config import settings

# MongoDB client connection and database
client = AsyncMongoClient(settings.MONGODB_URL)

db = client["dodgygeezers"]
collection = db["room_messages"]
