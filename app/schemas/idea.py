from datetime import datetime
from pydantic import BaseModel


class IdeaCreate(BaseModel):
    title: str
    description: str | None = None


class IdeaRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    timestamp: datetime

    class Config:
        orm_mode = True
