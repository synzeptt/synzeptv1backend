from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from models import Conversation, Memory
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ConversationItem
from services.ai_service import generate_ai_response

router = APIRouter()


@router.get("/", response_model=list[ConversationItem])
def get_conversation(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.timestamp.asc())
        .all()
    )


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Persist user message
    user_msg = Conversation(user_id=user.id, role="user", message=request.message)
    db.add(user_msg)
    db.commit()

    try:
        response_text = generate_ai_response(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Simple memory extraction: if user mentions "goal" or "idea" we'll store it.
    memory_saved = False
    lowered = request.message.lower()
    if "goal" in lowered:
        memory = Memory(user_id=user.id, type="goal", content=request.message)
        db.add(memory)
        memory_saved = True
    elif "idea" in lowered:
        memory = Memory(user_id=user.id, type="idea", content=request.message)
        db.add(memory)
        memory_saved = True

    if memory_saved:
        db.commit()

    # Persist assistant response
    assistant_msg = Conversation(user_id=user.id, role="assistant", message=response_text)
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(response=response_text, memory_extracted=memory_saved)
