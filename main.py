"""Main entry point for the Synzept FastAPI application."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
import google.generativeai as genai

from app.api import auth, chat, profiles, memories, ideas, goals
from app.core.config import settings
from app.core import security
from services.ai_service import generate_ai_response
from models import Base, User, Idea, Goal, Memory, Conversation
from app.db.session import engine, get_db
from schemas import UserSignup, UserLogin, IdeaCreate, IdeaResponse, GoalCreate, GoalResponse, MemoryCreate, MemoryResponse, ChatRequest, ChatResponse, ConversationResponse


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


app = FastAPI(
    title="Synzept API",
    description="Synzept FastAPI backend API",
    version="0.1.0",
    lifespan=lifespan
)

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


@app.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        return {"error": "Email already registered"}
    hashed_password = security.hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not security.verify_password(user.password, db_user.password_hash):
        return {"error": "Invalid credentials"}
    return {"message": "Login successful", "user_id": db_user.id}


@app.post("/ideas", response_model=IdeaResponse)
def create_idea(idea: IdeaCreate, user_id: int, db: Session = Depends(get_db)):
    new_idea = Idea(user_id=user_id, title=idea.title, description=idea.description)
    db.add(new_idea)
    db.commit()
    db.refresh(new_idea)
    return new_idea


@app.get("/ideas", response_model=list[IdeaResponse])
def get_ideas(user_id: int, db: Session = Depends(get_db)):
    ideas = db.query(Idea).filter(Idea.user_id == user_id).all()
    return ideas


@app.get("/ideas/{idea_id}", response_model=IdeaResponse)
def get_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@app.delete("/ideas/{idea_id}")
def delete_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    db.delete(idea)
    db.commit()
    return {"message": "Idea deleted successfully"}


# Goals endpoints
@app.post("/goals", response_model=GoalResponse)
def create_goal(goal: GoalCreate, user_id: int, db: Session = Depends(get_db)):
    new_goal = Goal(user_id=user_id, title=goal.title, description=goal.description)
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


@app.get("/goals", response_model=list[GoalResponse])
def get_goals(user_id: int, db: Session = Depends(get_db)):
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    return goals


@app.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: int, status: str, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.status = status
    db.commit()
    db.refresh(goal)
    return goal


@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully"}


# Memories endpoints
@app.post("/memories", response_model=MemoryResponse)
def create_memory(memory: MemoryCreate, user_id: int, db: Session = Depends(get_db)):
    new_memory = Memory(user_id=user_id, content=memory.content, memory_type=memory.memory_type)
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    return new_memory


@app.get("/memories", response_model=list[MemoryResponse])
def get_memories(user_id: int, db: Session = Depends(get_db)):
    memories = db.query(Memory).filter(Memory.user_id == user_id).all()
    return memories


@app.delete("/memories/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    db.delete(memory)
    db.commit()
    return {"message": "Memory deleted successfully"}


# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        response_text = generate_ai_response(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI service error")
    
    # Store conversation
    conv = Conversation(user_id=request.user_id, message=request.message, response=response_text)
    db.add(conv)
    db.commit()
    return {"response": response_text, "memory_extracted": True}


@app.get("/conversations", response_model=list[ConversationResponse])
def get_conversations(user_id: int, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
    return conversations


@app.get("/")
async def root():
    return {"message": "Welcome to Synzept API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)