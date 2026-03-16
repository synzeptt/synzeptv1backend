from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db import models
from app.db.session import get_db
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate

router = APIRouter()


@router.get("/", response_model=ProfileRead)
def get_profile(user=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/", response_model=ProfileRead)
def create_profile(
    profile_in: ProfileCreate, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    # Check if profile already exists
    existing = db.query(models.UserProfile).filter(models.UserProfile.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = models.UserProfile(user_id=user.id, **profile_in.dict(exclude_unset=True))
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/", response_model=ProfileRead)
def update_profile(
    profile_in: ProfileUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in profile_in.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
