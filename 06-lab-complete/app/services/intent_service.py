import json

from app.adapters.llm_adapter import LLMAdapter
from app.schemas.chat import IntentExtractionResult, SessionState, UserContext
from app.schemas.facility import FacilityType
from app.utils.text_normalizer import normalize_for_matching


class IntentService:
    SPECIFIC_TAG_KEYWORDS: dict[str, tuple[str, ...]] = {
        "hotpot": ("lau", "lẩu"),
        "korean": ("han quoc", "hàn quốc", "korean"),
        "conveyor": ("bang chuyen", "băng chuyền"),
    }
    FACILITY_KEYWORDS: dict[FacilityType, tuple[str, ...]] = {
        "restaurant": (
            "nha hang",
            "quan an",
            "quan",
            "mon an",
            "an mon viet",
            "ăn món việt",
            "do an",
            "restaurant",
            "doi bung",
            "đói bụng",
            "an trua",
            "ăn trưa",
            "an toi",
            "ăn tối",
            "an sang",
            "ăn sáng",
        ),
        "toilet": (
            "toilet",
            "wc",
            "nha ve sinh",
            "restroom",
            "di ve sinh",
            "đi vệ sinh",
            "buon ve sinh",
            "buồn vệ sinh",
        ),
        "first_aid": (
            "phong y te",
            "so cuu",
            "first aid",
            "y te",
            "bac si",
            "bác sĩ",
            "tram y te",
            "trạm y tế",
        ),
        "rest_area": (
            "nghi chan",
            "rest area",
            "ghe nghi",
            "khu nghi",
            "ngoi nghi",
            "ngồi nghỉ",
            "met qua",
            "mệt quá",
        ),
        "locker": ("locker", "tu do", "gui do", "tủ đồ", "gửi đồ"),
        "drinking_water": (
            "nuoc uong",
            "drinking water",
            "nuoc loc",
            "mua nuoc",
            "mua nước",
            "refill",
            "khat",
            "khát",
            "khat nuoc",
            "khát nước",
        ),
        "souvenir": (
            "souvenir",
            "qua luu niem",
            "quà lưu niệm",
            "qua tang",
            "quà tặng",
            "mua qua",
            "mua quà",
        ),
        "lost_found": (
            "lost and found",
            "that lac",
            "thất lạc",
            "mat do",
            "mất đồ",
            "tim do",
            "tìm đồ",
            "quen do",
            "quên đồ",
            "roi do",
            "rơi đồ",
        ),
        "ticket_support": (
            "quay ve",
            "quầy vé",
            "ho tro ve",
            "hỗ trợ vé",
            "ticket support",
            "ticket counter",
            "quay ho tro",
            "quầy hỗ trợ",
            "mua ve",
            "mua vé",
            "ve o dau",
            "vé ở đâu",
            "doi ve",
            "đổi vé",
        ),
    }
    CORRECTION_NEARER = ("xa qua", "gan hon", "cho gan hon", "gần hơn")
    CORRECTION_KID = ("cho tre em", "mon cho tre em", "kids", "kid")
    CORRECTION_OPEN = ("con mo", "còn mở", "dang mo")

    def __init__(self, llm_adapter: LLMAdapter | None = None) -> None:
        self.llm_adapter = llm_adapter or LLMAdapter()

    def extract_intent(
        self,
        message: str,
        current_zone: str,
        user_context: UserContext,
        session_state: SessionState | None = None,
        forced_facility_type: FacilityType | None = None,
    ) -> IntentExtractionResult:
        session_state = session_state or SessionState()
        llm_result = self._try_llm(message)
        heuristic = self._heuristic_extract(
            message=message,
            current_zone=current_zone,
            user_context=user_context,
            session_state=session_state,
            forced_facility_type=forced_facility_type,
        )

        if llm_result is not None:
            if forced_facility_type:
                llm_result.facility_type = forced_facility_type
            llm_result.current_zone = current_zone
            self._merge_context_constraints(llm_result, user_context)
            if self._should_prefer_heuristic(llm_result, heuristic):
                return heuristic
            return llm_result

        return heuristic

    def _try_llm(self, message: str) -> IntentExtractionResult | None:
        for _ in range(2):
            raw = self.llm_adapter.extract_intent(message)
            if not raw:
                continue
            try:
                payload = json.loads(raw)
                return IntentExtractionResult.model_validate(payload)
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
        return None

    def _heuristic_extract(
        self,
        message: str,
        current_zone: str,
        user_context: UserContext,
        session_state: SessionState,
        forced_facility_type: FacilityType | None,
    ) -> IntentExtractionResult:
        match_text = normalize_for_matching(message)

        if self._is_correction(match_text) and session_state.last_intent:
            intent = session_state.last_intent.model_copy(deep=True)
            intent.intent_type = "correction"
            intent.current_zone = current_zone
            if any(keyword in match_text for keyword in self.CORRECTION_NEARER):
                intent.constraints["prefer_nearer"] = True
                if session_state.last_selected_facility:
                    intent.constraints["exclude_facility_ids"] = [
                        session_state.last_selected_facility.id
                    ]
            if any(keyword in match_text for keyword in self.CORRECTION_KID):
                intent.constraints["kid_friendly"] = True
            if any(keyword in match_text for keyword in self.CORRECTION_OPEN):
                intent.constraints["open_now"] = True
            intent.confidence = 0.84
            intent.needs_clarification = False
            self._merge_context_constraints(intent, user_context)
            return intent

        facility_type = forced_facility_type or self._detect_facility_type(match_text)
        if facility_type is None:
            return IntentExtractionResult(
                intent_type="out_of_scope",
                facility_type=None,
                current_zone=current_zone,
                constraints={},
                needs_clarification=True,
                confidence=0.25,
            )

        constraints = self._extract_constraints(match_text, user_context)
        return IntentExtractionResult(
            intent_type="facility_search",
            facility_type=facility_type,
            current_zone=current_zone,
            constraints=constraints,
            needs_clarification=False,
            confidence=0.78 if forced_facility_type is None else 0.92,
        )

    def _is_correction(self, match_text: str) -> bool:
        return any(keyword in match_text for keyword in self.CORRECTION_NEARER) or any(
            keyword in match_text for keyword in self.CORRECTION_KID + self.CORRECTION_OPEN
        )

    def _detect_facility_type(self, match_text: str) -> FacilityType | None:
        for facility_type, keywords in self.FACILITY_KEYWORDS.items():
            if any(keyword in match_text for keyword in keywords):
                return facility_type
        return None

    def _extract_constraints(
        self,
        match_text: str,
        user_context: UserContext,
    ) -> dict[str, object]:
        constraints: dict[str, object] = {}
        if "tre em" in match_text or "kid" in match_text or user_context.has_child:
            constraints["kid_friendly"] = True
        if (
            "chay" in match_text
            or "vegetarian" in match_text
            or "veggie" in match_text
        ):
            constraints["required_tags"] = ["vegetarian"]

        specific_tags = [
            tag
            for tag, keywords in self.SPECIFIC_TAG_KEYWORDS.items()
            if any(keyword in match_text for keyword in keywords)
        ]
        if specific_tags:
            required_tags = list(constraints.get("required_tags", []))
            required_tags.extend(tag for tag in specific_tags if tag not in required_tags)
            constraints["required_tags"] = required_tags

        if "it dong" in match_text or "ít đông" in match_text:
            constraints["prefer_low_crowd"] = True
        if "it cay" in match_text or "ít cay" in match_text:
            constraints.setdefault("free_text_preferences", [])
            free_text_preferences = list(constraints["free_text_preferences"])
            free_text_preferences.append("non_spicy")
            constraints["free_text_preferences"] = free_text_preferences
        if "gan" in match_text or "gần" in match_text:
            constraints["prefer_nearer"] = True
        return constraints

    def _merge_context_constraints(
        self,
        intent: IntentExtractionResult,
        user_context: UserContext,
    ) -> None:
        if user_context.has_child:
            intent.constraints.setdefault("kid_friendly", True)

    def _should_prefer_heuristic(
        self,
        llm_result: IntentExtractionResult,
        heuristic: IntentExtractionResult,
    ) -> bool:
        if heuristic.intent_type == "facility_search" and llm_result.intent_type == "out_of_scope":
            return True
        if (
            heuristic.intent_type == "facility_search"
            and llm_result.intent_type == "facility_search"
            and llm_result.facility_type != heuristic.facility_type
            and heuristic.confidence >= llm_result.confidence
        ):
            return True
        return False
