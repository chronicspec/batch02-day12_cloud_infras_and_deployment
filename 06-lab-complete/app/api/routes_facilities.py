from fastapi import APIRouter, Depends, Query

from app.adapters.mock_data_loader import MockDataLoader
from app.schemas.facility import Facility, FacilityListResponse

router = APIRouter(tags=["facilities"])


def get_loader() -> MockDataLoader:
    return MockDataLoader()


@router.get("/facilities", response_model=FacilityListResponse)
def list_facilities(
    facility_type: str | None = Query(default=None),
    zone_id: str | None = Query(default=None),
    loader: MockDataLoader = Depends(get_loader),
) -> FacilityListResponse:
    facilities = loader.load_facilities()
    items: list[Facility] = []

    for facility in facilities:
        if facility_type and facility.type != facility_type:
            continue
        if zone_id and facility.zone_id != zone_id:
            continue
        items.append(facility)

    return FacilityListResponse(items=items, total=len(items))
