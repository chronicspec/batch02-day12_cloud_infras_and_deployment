from app.schemas.chat import IntentExtractionResult
from app.schemas.facility import Facility
from app.services.facility_service import FacilityService


class QueryEngine:
    def __init__(self, facility_service: FacilityService) -> None:
        self.facility_service = facility_service

    def query(self, intent: IntentExtractionResult) -> list[Facility]:
        return self.facility_service.find_candidates(
            facility_type=intent.facility_type,
            current_zone=intent.current_zone,
            constraints=intent.constraints,
            strict=True,
        )

    def fallback(self, intent: IntentExtractionResult) -> list[Facility]:
        return self.facility_service.find_candidates(
            facility_type=intent.facility_type,
            current_zone=intent.current_zone,
            constraints=intent.constraints,
            strict=False,
        )
