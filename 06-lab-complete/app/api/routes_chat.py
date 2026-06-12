from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.orchestrator import ChatOrchestrator

router = APIRouter(tags=["chat"])


@lru_cache
def get_orchestrator() -> ChatOrchestrator:
    return ChatOrchestrator()


@router.post("/chat", response_model=ChatResponse)
def create_chat_response(
    payload: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> ChatResponse:
    try:
        return orchestrator.handle_chat(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
