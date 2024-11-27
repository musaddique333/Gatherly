from fastapi import FastAPI

app = FastAPI(title="Dodgygeezers Auth")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Dodgygeezers Video Service"}
