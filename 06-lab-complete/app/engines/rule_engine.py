from app.schemas.chat import ChatResponse, RuleCheckResult
from app.schemas.common import NavigationInfo
from app.schemas.facility import FacilityType
from app.utils.text_normalizer import normalize_for_matching, normalize_text


class RuleEngine:
    EMERGENCY_KEYWORDS = (
        "dut tay",
        "bi thuong",
        "chay mau",
        "so cuu",
        "cap cuu",
        "cuu thuong",
        "injury",
        "bleeding",
    )
    TOILET_KEYWORDS = ("toilet", "wc", "nha ve sinh", "restroom")
    OUT_OF_SCOPE_KEYWORDS = (
        "gia ve",
        "dat ve",
        "lich dien",
        "khach san",
        "weather",
        "thoi tiet",
    )
    INJECTION_PATTERNS = (
        "ignore previous",
        "system prompt",
        "developer message",
        "role:system",
        "bypass",
    )

    def evaluate(self, message: str) -> RuleCheckResult:
        normalized_message = normalize_text(message)
        match_text = normalize_for_matching(message)

        if any(pattern in match_text for pattern in self.INJECTION_PATTERNS):
            return RuleCheckResult(
                normalized_message=normalized_message,
                blocked=True,
                block_reason="Phát hiện nội dung không phù hợp cho prototype demo.",
            )

        if any(keyword in match_text for keyword in self.EMERGENCY_KEYWORDS):
            return RuleCheckResult(
                normalized_message=normalized_message,
                is_emergency=True,
                forced_facility_type="first_aid",
            )

        if any(keyword in match_text for keyword in self.TOILET_KEYWORDS):
            return RuleCheckResult(
                normalized_message=normalized_message,
                forced_facility_type="toilet",
            )

        if any(keyword in match_text for keyword in self.OUT_OF_SCOPE_KEYWORDS):
            return RuleCheckResult(
                normalized_message=normalized_message,
                is_out_of_scope=True,
            )

        return RuleCheckResult(normalized_message=normalized_message)

    def build_block_response(self, reason: str) -> ChatResponse:
        return ChatResponse(
            type="clarification",
            action="reject_input",
            message=reason,
            reason_summary="rule_engine_blocked",
            confidence=1.0,
        )

    def build_out_of_scope_response(self) -> ChatResponse:
        return ChatResponse(
            type="clarification",
            action="out_of_scope",
            message=(
                "Prototype này hiện chỉ hỗ trợ tìm restaurant, toilet, first-aid, "
                "rest area, drinking water, locker, souvenir, lost & found và ticket support gần nhất trong công viên."
            ),
            reason_summary="out_of_scope_request",
            confidence=1.0,
        )

    def build_fast_track_response(
        self,
        message: str,
        navigation: NavigationInfo | None,
    ) -> ChatResponse:
        direction_text = navigation.direction_text if navigation else "Di chuyển theo biển chỉ dẫn y tế gần nhất."
        return ChatResponse(
            type="fast_track",
            action="go_to_first_aid",
            message=(
                f"Ưu tiên sơ cứu ngay. {message} {direction_text}".strip()
            ),
            navigation=navigation,
            reason_summary="emergency_keyword_detected",
            confidence=1.0,
        )
