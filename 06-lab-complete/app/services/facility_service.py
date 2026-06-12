from app.adapters.mock_data_loader import MockDataLoader
from app.schemas.facility import Facility, FacilityType


class FacilityService:
    def __init__(self, loader: MockDataLoader | None = None) -> None:
        self.loader = loader or MockDataLoader()

    def get_facilities(self, zone_id: str | None = None) -> list[Facility]:
        facilities = self.loader.load_facilities()
        if zone_id:
            return [f for f in facilities if f.zone_id == zone_id]
        return facilities

    def find_candidates(
        self,
        facility_type: FacilityType | None,
        current_zone: str,
        constraints: dict[str, object],
        strict: bool,
    ) -> list[Facility]:
        facilities = self.loader.load_facilities()
        filtered = [
            facility
            for facility in facilities
            if facility_type is None or facility.type == facility_type
        ]

        if strict:
            filtered = [
                facility
                for facility in filtered
                if self._matches_constraints(facility, constraints)
            ]

        filtered = [
            facility
            for facility in filtered
            if current_zone in facility.distance_map
            and facility.id not in set(constraints.get("exclude_facility_ids", []))
        ]
        return filtered

    def fallback_nearest(
        self,
        current_zone: str,
        limit: int = 3,
    ) -> list[Facility]:
        facilities = [
            facility
            for facility in self.loader.load_facilities()
            if current_zone in facility.distance_map
        ]
        return sorted(
            facilities,
            key=lambda item: (item.distance_map[current_zone], not item.is_open),
        )[:limit]

    def _matches_constraints(
        self,
        facility: Facility,
        constraints: dict[str, object],
    ) -> bool:
        if constraints.get("kid_friendly") and not facility.kid_friendly:
            return False
        if constraints.get("open_now") and not facility.is_open:
            return False

        required_tags = constraints.get("required_tags", [])
        if required_tags:
            if not all(tag in facility.tags or tag in facility.amenities for tag in required_tags):
                return False
        return True
