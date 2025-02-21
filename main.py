import sys
import os
import uvicorn
from fastapi import FastAPI
from app.api import endpoints, embeddings, scoring

app = FastAPI()

# Include API routers
app.include_router(endpoints.router)
app.include_router(embeddings.router)
app.include_router(scoring.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
