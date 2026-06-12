from app.config import get_settings
from app.engines.query_engine import QueryEngine
from app.engines.rule_engine import RuleEngine
from app.schemas.chat import ChatRequest, ChatResponse, IntentExtractionResult
from app.services.facility_service import FacilityService
from app.services.intent_service import IntentService
from app.services.navigation_service import NavigationService
from app.services.ranking_service import RankingService
from app.services.response_service import ResponseService
from app.services.session_service import SessionService
from app.utils.validators import validate_chat_request


class ChatOrchestrator:
    def __init__(
        self,
        rule_engine: RuleEngine | None = None,
        intent_service: IntentService | None = None,
        facility_service: FacilityService | None = None,
        ranking_service: RankingService | None = None,
        navigation_service: NavigationService | None = None,
        response_service: ResponseService | None = None,
        session_service: SessionService | None = None,
    ) -> None:
        self.rule_engine = rule_engine or RuleEngine()
        self.intent_service = intent_service or IntentService()
        self.facility_service = facility_service or FacilityService()
        self.query_engine = QueryEngine(self.facility_service)
        self.ranking_service = ranking_service or RankingService()
        self.navigation_service = navigation_service or NavigationService()
        self.response_service = response_service or ResponseService()
        self.session_service = session_service or SessionService()
        self.settings = get_settings()

    def handle_chat(self, payload: ChatRequest) -> ChatResponse:
        request = validate_chat_request(payload)
        self._validate_current_zone(request.current_zone)
        session_state = self.session_service.get(request.session_id)
        rule_result = self.rule_engine.evaluate(request.message)

        if rule_result.blocked:
            return self.response_service.build_response(
                response_type="clarification",
                action="reject_input",
                reason_summary="rule_engine_blocked",
                confidence=1.0,
                fallback_message=rule_result.block_reason or "Input bị chặn.",
            )

        if rule_result.is_out_of_scope:
            return self.response_service.build_response(
                response_type="clarification",
                action="out_of_scope",
                reason_summary="out_of_scope_request",
                confidence=1.0,
                fallback_message=(
                    "Prototype này hiện chỉ hỗ trợ tìm restaurant, toilet, first-aid, "
                    "rest area, drinking water, locker, souvenir, lost & found và ticket support gần nhất trong công viên."
                ),
            )

        if rule_result.is_emergency:
            facility = self._select_first_aid(request.current_zone)
            navigation = (
                self.navigation_service.build_navigation(request.current_zone, facility)
                if facility
                else None
            )
            response = self.response_service.build_response(
                response_type="fast_track",
                action="go_to_first_aid",
                reason_summary="emergency_keyword_detected",
                confidence=1.0,
                selected_facility=facility,
                navigation=navigation,
                fallback_message=(
                    "Ưu tiên sơ cứu ngay. Vui lòng tới điểm first-aid gần nhất ngay. "
                    f"{navigation.direction_text if navigation else ''}"
                ).strip(),
            )
            self.session_service.save(
                request.session_id,
                intent=None,
                selected_facility=facility,
                current_zone=request.current_zone,
                has_child=request.user_context.has_child,
            )
            return response

        intent = self.intent_service.extract_intent(
            message=rule_result.normalized_message,
            current_zone=request.current_zone,
            user_context=request.user_context,
            session_state=session_state,
            forced_facility_type=rule_result.forced_facility_type,
        )

        if intent.intent_type == "out_of_scope" or intent.facility_type is None:
            return self.response_service.build_response(
                response_type="clarification",
                action="out_of_scope",
                reason_summary="intent_not_supported",
                confidence=0.3,
                fallback_message=(
                    "Prototype này hiện chỉ hỗ trợ tìm restaurant, toilet, first-aid, "
                    "rest area, drinking water, locker, souvenir, lost & found và ticket support gần nhất trong công viên."
                ),
            )

        candidates = self.query_engine.query(intent)
        ranked = self.ranking_service.rank(
            candidates,
            current_zone=request.current_zone,
            constraints=intent.constraints,
        )

        if not ranked:
            return self._build_fallback_response(request, intent)

        selected = ranked[0]
        navigation = self.navigation_service.build_navigation(request.current_zone, selected)
        
        cross_sell_facilities = self._build_cross_sell_facilities(selected)

        if navigation.distance_m > self.settings.low_confidence_distance_m:
            response = self.response_service.build_response(
                response_type="clarification",
                action="confirm_far_result",
                selected_facility=selected,
                alternatives=ranked[1:3],
                cross_sell_facilities=cross_sell_facilities,
                navigation=navigation,
                reason_summary="nearest_match_exceeds_low_confidence_threshold",
                confidence=0.62,
                fallback_message=(
                    f"Em tìm thấy {selected.name}, nhưng điểm này cách khoảng "
                    f"{navigation.distance_m}m. Anh có muốn đi điểm này không?"
                ),
            )
            self._save_session(request, intent, selected)
            return response

        response = self.response_service.build_response(
            response_type="success",
            action="show_facility",
            selected_facility=selected,
            alternatives=ranked[1:3],
            cross_sell_facilities=cross_sell_facilities,
            navigation=navigation,
            reason_summary="deterministic_backend_ranked_best_candidate",
            confidence=intent.confidence,
            fallback_message=(
                f"Điểm phù hợp nhất là {selected.name}. Cách anh khoảng "
                f"{navigation.distance_m}m, đi bộ tầm {navigation.walk_time_min} phút."
            ),
        )
        self._save_session(request, intent, selected)
        return response

    def _build_fallback_response(
        self,
        request: ChatRequest,
        intent: IntentExtractionResult,
    ) -> ChatResponse:
        fallback_candidates = self.query_engine.fallback(intent)
        ranked_fallback = self.ranking_service.rank(
            fallback_candidates,
            current_zone=request.current_zone,
            constraints={},
        )
        ranked_fallback = self._ensure_fallback_limit(
            ranked_fallback,
            current_zone=request.current_zone,
            limit=3,
        )

        response = self.response_service.build_response(
            response_type="fallback",
            action="show_nearest_alternatives",
            alternatives=ranked_fallback[:3],
            reason_summary="no_exact_match_returned_nearest_alternatives",
            confidence=0.45,
            fallback_message=(
                "Em chưa tìm được kết quả khớp hoàn toàn. Dưới đây là 3 điểm gần nhất để anh chọn nhanh."
            ),
        )
        self._save_session(request, intent, None)
        return response

    def _ensure_fallback_limit(
        self,
        candidates,
        current_zone: str,
        limit: int,
    ):
        deduped: list = []
        seen_ids: set[str] = set()

        for facility in candidates:
            if facility.id in seen_ids:
                continue
            deduped.append(facility)
            seen_ids.add(facility.id)
            if len(deduped) >= limit:
                return deduped

        for facility in self.facility_service.fallback_nearest(current_zone, limit=limit):
            if facility.id in seen_ids:
                continue
            deduped.append(facility)
            seen_ids.add(facility.id)
            if len(deduped) >= limit:
                break

        return deduped

    def _select_first_aid(self, current_zone: str):
        candidates = self.facility_service.find_candidates(
            facility_type="first_aid",
            current_zone=current_zone,
            constraints={},
            strict=False,
        )
        ranked = self.ranking_service.rank(candidates, current_zone, {})
        return ranked[0] if ranked else None

    def _build_cross_sell_facilities(self, selected):
        utility_types = {"toilet", "drinking_water", "rest_area"}
        if selected.type in utility_types | {"first_aid"}:
            return []

        utilities = [
            facility
            for facility in self.facility_service.get_facilities()
            if facility.id != selected.id
            and facility.type in utility_types
            and selected.zone_id in facility.distance_map
        ]

        utilities.sort(
            key=lambda facility: (
                facility.zone_id != selected.zone_id,
                facility.distance_map[selected.zone_id],
                not facility.is_open,
            )
        )

        cross_sell: list = []
        seen_types: set[str] = set()
        for facility in utilities:
            if facility.type in seen_types:
                continue
            cross_sell.append(facility)
            seen_types.add(facility.type)
            if len(cross_sell) >= 2:
                break

        return cross_sell

    def _validate_current_zone(self, current_zone: str) -> None:
        zone_ids = {zone.id for zone in self.facility_service.loader.load_zones()}
        if current_zone not in zone_ids:
            raise ValueError(f"Unknown current_zone: {current_zone}")

    def _save_session(
        self,
        request: ChatRequest,
        intent: IntentExtractionResult | None,
        selected,
    ) -> None:
        self.session_service.save(
            request.session_id,
            intent=intent,
            selected_facility=selected,
            current_zone=request.current_zone,
            has_child=request.user_context.has_child,
        )
