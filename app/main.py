from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.api import auth, chat, profiles, memories, ideas, goals
from app.core.config import settings
from models import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Warning: Could not create database tables on startup: {e}")
        print("Tables will be created when the database is available.")

    yield

    # Shutdown
    # Add any cleanup code here if needed


app = FastAPI(title="Synzept API", version="0.1.0", lifespan=lifespan)

# CORS middleware (must be directly after app creation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return Response(status_code=200)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(profiles.router, prefix="/api/profile", tags=["profile"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(memories.router, prefix="/api/memories", tags=["memories"])
app.include_router(ideas.router, prefix="/api/ideas", tags=["ideas"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])


@app.get("/")
async def root():
    return {"message": "Welcome to Synzept API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
