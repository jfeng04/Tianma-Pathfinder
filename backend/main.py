from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(
    title="Tianma Pathfinder API",
    version="0.1.0",
)

app.include_router(
    router,
    prefix="/api",
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "tianma-pathfinder",
    }