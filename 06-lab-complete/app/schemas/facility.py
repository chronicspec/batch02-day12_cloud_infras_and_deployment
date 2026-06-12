from typing import Literal

from pydantic import BaseModel, Field


FacilityType = Literal[
    "restaurant",
    "toilet",
    "first_aid",
    "rest_area",
    "locker",
    "drinking_water",
    "souvenir",
    "lost_found",
    "ticket_support",
]


class Facility(BaseModel):
    id: str
    name: str
    type: FacilityType
    zone_id: str
    tags: list[str] = Field(default_factory=list)
    kid_friendly: bool = False
    is_open: bool = True
    crowd_level: Literal["low", "medium", "high"] = "medium"
    wait_time_min: int = Field(default=0, ge=0)
    distance_map: dict[str, int] = Field(default_factory=dict)
    walk_time_map: dict[str, int] = Field(default_factory=dict)
    amenities: list[str] = Field(default_factory=list)
    description: str
    lat: float | None = None
    lng: float | None = None


class Zone(BaseModel):
    id: str
    name: str
    description: str


class PathMap(BaseModel):
    from_zone: str
    to_zone: str
    direction_text: str


class FacilityListResponse(BaseModel):
    items: list[Facility]
    total: int = Field(ge=0)
