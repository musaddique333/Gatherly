from fastapi import FastAPI
from app.api.main import api_router

app = FastAPI(title="Dodgygeezers Auth")

# Include the API routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Dodgygeezers Auth"}
