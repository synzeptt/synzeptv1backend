from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from models import Goal
from app.db.session import get_db
from app.schemas.goal import GoalCreate, GoalRead

router = APIRouter()


@router.get("/", response_model=list[GoalRead])
def list_goals(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Goal).filter(Goal.user_id == user.id).order_by(Goal.created_at.desc()).all()


@router.post("/", response_model=GoalRead)
def create_goal(goal_in: GoalCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    goal = Goal(user_id=user.id, title=goal_in.title)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal
