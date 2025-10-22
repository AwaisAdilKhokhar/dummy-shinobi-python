from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import json
from typing import List

from app.database import engine, Base
from app.config import get_settings
from app.api import auth, cameras, recordings, events, stream

settings = get_settings()

# Create directories
os.makedirs(settings.RECORDINGS_PATH, exist_ok=True)
os.makedirs(settings.STREAM_PATH, exist_ok=True)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Shinobi Clone API",
    description="Video Surveillance NVR System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(cameras.router, prefix="/api")
app.include_router(recordings.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(stream.router, prefix="/api")

# Mount static directories for streams and recordings
if os.path.exists(settings.STREAM_PATH):
    app.mount("/streams", StaticFiles(directory=settings.STREAM_PATH), name="streams")

if os.path.exists(settings.RECORDINGS_PATH):
    app.mount("/recordings", StaticFiles(directory=settings.RECORDINGS_PATH), name="recordings")


@app.get("/")
def read_root():
    return {
        "message": "Shinobi Clone API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now, can be extended for specific commands
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Utility function to broadcast events
async def broadcast_event(event_type: str, data: dict):
    """Broadcast event to all connected WebSocket clients."""
    message = {
        "type": event_type,
        "data": data
    }
    await manager.broadcast(message)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
