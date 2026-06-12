from app.schemas.facility import Facility


class RankingService:
    def rank(
        self,
        candidates: list[Facility],
        current_zone: str,
        constraints: dict[str, object],
    ) -> list[Facility]:
        return sorted(
            candidates,
            key=lambda facility: self._score(facility, current_zone, constraints),
            reverse=True,
        )

    def _score(
        self,
        facility: Facility,
        current_zone: str,
        constraints: dict[str, object],
    ) -> tuple[int, int, int, int, int, int]:
        distance = facility.distance_map.get(current_zone, 99_999)
        open_score = 1 if facility.is_open else 0
        kid_score = 1 if facility.kid_friendly else 0
        tag_score = 0
        required_tags = constraints.get("required_tags", [])
        if required_tags:
            tag_score = sum(
                1
                for tag in required_tags
                if tag in facility.tags or tag in facility.amenities
            )
        low_crowd_bonus = 1 if facility.crowd_level == "low" else 0
        wait_score = -facility.wait_time_min
        distance_score = -distance
        if constraints.get("prefer_nearer"):
            distance_score *= 2
        return (
            open_score,
            kid_score if constraints.get("kid_friendly") else 0,
            tag_score,
            low_crowd_bonus if constraints.get("prefer_low_crowd") else 0,
            distance_score,
            wait_score,
        )
