from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router, speech_router

app = FastAPI(
    title="Tianma Pathfinder API",
    version="0.1.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(
    router,
    prefix="/api",
)

app.include_router(
    speech_router,
    prefix="/api",
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "tianma-pathfinder",
    }