from app.adapters.mock_data_loader import MockDataLoader
from app.schemas.common import NavigationInfo
from app.schemas.facility import Facility


class NavigationService:
    def __init__(self, loader: MockDataLoader | None = None) -> None:
        self.loader = loader or MockDataLoader()

    def build_navigation(
        self,
        current_zone: str,
        facility: Facility,
    ) -> NavigationInfo:
        direction_text = self._resolve_direction_text(current_zone, facility.zone_id)
        return NavigationInfo(
            from_zone=current_zone,
            to_zone=facility.zone_id,
            distance_m=facility.distance_map.get(current_zone, 0),
            walk_time_min=facility.walk_time_map.get(current_zone, 0),
            direction_text=direction_text,
        )

    def _resolve_direction_text(self, current_zone: str, target_zone: str) -> str:
        if current_zone == target_zone:
            return "Đi theo biển chỉ dẫn nội khu, điểm đến nằm ngay trong khu hiện tại."

        for path in self.loader.load_paths():
            if path.from_zone == current_zone and path.to_zone == target_zone:
                return path.direction_text
            if path.from_zone == target_zone and path.to_zone == current_zone:
                return path.direction_text

        return "Đi theo bản đồ công viên và biển chỉ dẫn gần nhất."
