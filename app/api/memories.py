from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from models import Memory
from app.db.session import get_db
from app.schemas.memory import MemoryCreate, MemoryRead

router = APIRouter()


@router.get("/", response_model=list[MemoryRead])
def list_memories(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Memory)
        .filter(Memory.user_id == user.id)
        .order_by(Memory.timestamp.desc())
        .all()
    )


@router.post("/", response_model=MemoryRead)
def create_memory(
    memory_in: MemoryCreate, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    memory = models.Memory(user_id=user.id, type=memory_in.type, content=memory_in.content)
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory
