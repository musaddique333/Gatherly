from fastapi import FastAPI
from app.api.main import api_router
from app.core.db import engine, Base

from app.core.wait_for_postgres import wait_for_postgres
wait_for_postgres()

app = FastAPI(title="Dodgygeezers Event")

# Create all database tables in Supabase
Base.metadata.create_all(bind=engine)

# Include the API routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Dodgygeezers Event"}
