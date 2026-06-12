from app.schemas.chat import ChatRequest


def validate_chat_request(payload: ChatRequest) -> ChatRequest:
    if len(payload.message.strip()) == 0:
        raise ValueError("Message must not be empty.")
    return payload
