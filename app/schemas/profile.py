from typing import List, Optional

from pydantic import BaseModel


class ProfileCreate(BaseModel):
    focus_areas: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    challenges: Optional[List[str]] = None


class ProfileRead(BaseModel):
    user_id: int
    focus_areas: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    challenges: Optional[List[str]] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    focus_areas: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    challenges: Optional[List[str]] = None
