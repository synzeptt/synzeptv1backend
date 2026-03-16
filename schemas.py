"""Pydantic schemas for request validation."""

from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class IdeaCreate(BaseModel):
    title: str
    description: str


class IdeaResponse(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    title: str
    description: str


class GoalResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MemoryCreate(BaseModel):
    content: str
    memory_type: str


class MemoryResponse(BaseModel):
    id: int
    content: str
    memory_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    response: str
    memory_extracted: bool


class ConversationResponse(BaseModel):
    id: int
    message: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True