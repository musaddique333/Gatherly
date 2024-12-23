from fastapi import FastAPI
import threading
from app.grpc_server import serve
from app.api.main import api_router
from app.core.db import engine, Base

app = FastAPI(title="Dodgygeezers Auth")

# Create all database tables in Supabase
Base.metadata.create_all(bind=engine)

# Include the API routes
app.include_router(api_router)

# Start gRPC server in a separate thread
threading.Thread(target=serve, daemon=True).start()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Dodgygeezers Auth"}
