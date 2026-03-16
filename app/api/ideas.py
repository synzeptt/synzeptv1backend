from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from models import Idea
from app.db.session import get_db
from app.schemas.idea import IdeaCreate, IdeaRead

router = APIRouter()


@router.get("/", response_model=list[IdeaRead])
def list_ideas(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Idea).filter(Idea.user_id == user.id).order_by(Idea.timestamp.desc()).all()


@router.post("/", response_model=IdeaRead)
def create_idea(idea_in: IdeaCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    idea = Idea(user_id=user.id, title=idea_in.title, description=idea_in.description)
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea
