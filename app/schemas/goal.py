from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class GoalStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class GoalCreate(BaseModel):
    title: str


class GoalRead(BaseModel):
    id: int
    title: str
    status: GoalStatus
    created_at: datetime

    class Config:
        orm_mode = True
