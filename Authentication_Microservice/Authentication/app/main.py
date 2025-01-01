import threading
from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from app.grpc_server import serve
from app.api.main import api_router
from app.core.db import engine, Base
from app.services.wait_for_postgres import wait_for_postgres

# Initialize FastAPI app
app = FastAPI(title="Dodgygeezers Auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_grpc_server():
    """
    Starts the gRPC server in a separate thread to handle authentication requests.
    
    This function runs the gRPC server in a daemon thread, allowing the main 
    FastAPI application to handle HTTP requests concurrently.
    """
    try:
        threading.Thread(target=serve, daemon=True).start()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting gRPC server: {str(e)}")

# Wait for PostgreSQL to be ready before starting the app
wait_for_postgres()


# Create all database tables in Supabase
Base.metadata.create_all(bind=engine)

# Include the API routes
app.include_router(api_router)

# Start gRPC server in a separate thread
start_grpc_server()

# Root endpoint
@app.get("/")
def read_root():
    """
    Root endpoint to check if the server is running.

    Returns:
        dict: A message indicating the server is up and running.
    """
    return {"message": "Welcome to the Dodgygeezers Auth"}
