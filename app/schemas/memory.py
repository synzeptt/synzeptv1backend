from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class MemoryType(str, Enum):
    idea = "idea"
    goal = "goal"
    project = "project"
    interest = "interest"
    insight = "insight"


class MemoryCreate(BaseModel):
    type: MemoryType
    content: str


class MemoryRead(BaseModel):
    id: int
    type: MemoryType
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True
