from app.adapters.llm_adapter import LLMAdapter
from app.schemas.chat import ChatResponse, ResponseType
from app.schemas.common import NavigationInfo
from app.schemas.facility import Facility


class ResponseService:
    def __init__(self, llm_adapter: LLMAdapter | None = None) -> None:
        self.llm_adapter = llm_adapter or LLMAdapter()

    def build_response(
        self,
        *,
        response_type: ResponseType,
        action: str,
        reason_summary: str,
        confidence: float,
        selected_facility: Facility | None = None,
        alternatives: list[Facility] | None = None,
        cross_sell_facilities: list[Facility] | None = None,
        navigation: NavigationInfo | None = None,
        fallback_message: str,
    ) -> ChatResponse:
        alternatives = alternatives or []
        cross_sell_facilities = cross_sell_facilities or []
        message = self._try_llm_message(
            response_type=response_type,
            action=action,
            reason_summary=reason_summary,
            confidence=confidence,
            selected_facility=selected_facility,
            alternatives=alternatives,
            cross_sell_facilities=cross_sell_facilities,
            navigation=navigation,
        )

        return ChatResponse(
            type=response_type,
            action=action,
            message=message or fallback_message,
            selected_facility=selected_facility,
            alternatives=alternatives,
            cross_sell_facilities=cross_sell_facilities,
            navigation=navigation,
            reason_summary=reason_summary,
            confidence=confidence,
        )

    def _try_llm_message(
        self,
        *,
        response_type: ResponseType,
        action: str,
        reason_summary: str,
        confidence: float,
        selected_facility: Facility | None,
        alternatives: list[Facility],
        cross_sell_facilities: list[Facility],
        navigation: NavigationInfo | None,
    ) -> str | None:
        payload = {
            "response_type": response_type,
            "action": action,
            "reason_summary": reason_summary,
            "confidence": confidence,
            "selected_facility": selected_facility.model_dump() if selected_facility else None,
            "alternatives": [item.model_dump() for item in alternatives],
            "cross_sell_facilities": [item.model_dump() for item in cross_sell_facilities],
            "navigation": navigation.model_dump() if navigation else None,
        }
        return self.llm_adapter.generate_response(payload)
