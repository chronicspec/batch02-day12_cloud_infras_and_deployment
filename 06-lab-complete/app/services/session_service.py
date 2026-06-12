from app.schemas.chat import IntentExtractionResult, SessionState
from app.schemas.facility import Facility


class SessionService:
    def __init__(self) -> None:
        self._store: dict[str, SessionState] = {}

    def get(self, session_id: str) -> SessionState:
        return self._store.get(session_id, SessionState())

    def save(
        self,
        session_id: str,
        *,
        intent: IntentExtractionResult | None,
        selected_facility: Facility | None,
        current_zone: str,
        has_child: bool,
    ) -> SessionState:
        state = SessionState(
            last_intent=intent,
            last_selected_facility=selected_facility,
            current_zone=current_zone,
            has_child=has_child,
        )
        self._store[session_id] = state
        return state
