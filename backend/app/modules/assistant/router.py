from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.db.models import User
from app.modules.users.router import get_current_user
from app.modules.assistant.service import generate_assistant_reply

router = APIRouter(tags=["Assistant"])


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=6000)


class AssistantChatResponse(BaseModel):
    message: str
    used_tokens: int
    remaining_tokens: int
    token_limit: int


class AssistantUsageResponse(BaseModel):
    used_tokens: int
    remaining_tokens: int
    token_limit: int
    plans: dict[str, int]


class AssistantTopupRequest(BaseModel):
    amount_inr: int


@router.get("/usage", response_model=AssistantUsageResponse)
def assistant_usage(current_user: User = Depends(get_current_user)):
    token_limit = current_user.chat_token_limit or 1000
    used = current_user.chat_tokens_used or 0
    return AssistantUsageResponse(
        used_tokens=used,
        remaining_tokens=max(0, token_limit - used),
        token_limit=token_limit,
        plans={"100_inr": 5000, "500_inr": 50000},
    )


@router.post("/chat", response_model=AssistantChatResponse)
def assistant_chat(
    payload: AssistantChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = generate_assistant_reply(db=db, user=current_user, user_message=payload.message)
    return AssistantChatResponse(
        message=result.message,
        used_tokens=result.used_tokens,
        remaining_tokens=result.remaining_tokens,
        token_limit=current_user.chat_token_limit or 1000,
    )


@router.post("/topup", response_model=AssistantUsageResponse)
def assistant_topup(
    payload: AssistantTopupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.amount_inr == 100:
        current_user.chat_token_limit = (current_user.chat_token_limit or 1000) + 5000
    elif payload.amount_inr == 500:
        current_user.chat_token_limit = (current_user.chat_token_limit or 1000) + 50000

    db.commit()
    db.refresh(current_user)

    token_limit = current_user.chat_token_limit or 1000
    used = current_user.chat_tokens_used or 0
    return AssistantUsageResponse(
        used_tokens=used,
        remaining_tokens=max(0, token_limit - used),
        token_limit=token_limit,
        plans={"100_inr": 5000, "500_inr": 50000},
    )
