from datetime import datetime
from pydantic import BaseModel


class ConversationItem(BaseModel):
    id: int
    role: str
    message: str
    timestamp: datetime

    class Config:
        orm_mode = True


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    memory_extracted: bool = False
