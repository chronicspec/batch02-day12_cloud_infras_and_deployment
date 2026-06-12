from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"]


class NavigationInfo(BaseModel):
    from_zone: str
    to_zone: str
    distance_m: int = Field(ge=0)
    walk_time_min: int = Field(ge=0)
    direction_text: str


class ApiMessage(BaseModel):
    code: str
    detail: str
