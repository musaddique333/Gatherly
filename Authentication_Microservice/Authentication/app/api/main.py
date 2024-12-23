from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI()

# Include the aggregated router from routes/__init__.py
app.include_router(api_router)