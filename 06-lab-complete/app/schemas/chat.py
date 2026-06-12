from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import NavigationInfo
from app.schemas.facility import Facility, FacilityType


ResponseType = Literal["success", "clarification", "fallback", "fast_track"]


class UserContext(BaseModel):
    has_child: bool = False


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=500)
    current_zone: str = Field(min_length=1)
    language: str = Field(default="vi", min_length=2, max_length=5)
    user_context: UserContext = Field(default_factory=UserContext)


class IntentExtractionResult(BaseModel):
    intent_type: Literal["facility_search", "correction", "out_of_scope"]
    facility_type: FacilityType | None = None
    current_zone: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    priority: Literal["normal", "urgent"] = "normal"
    needs_clarification: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class SessionState(BaseModel):
    last_intent: IntentExtractionResult | None = None
    last_selected_facility: Facility | None = None
    current_zone: str | None = None
    has_child: bool = False


class RuleCheckResult(BaseModel):
    normalized_message: str
    forced_facility_type: FacilityType | None = None
    is_emergency: bool = False
    is_out_of_scope: bool = False
    blocked: bool = False
    block_reason: str | None = None


class ChatResponse(BaseModel):
    type: ResponseType
    action: str
    message: str
    selected_facility: Facility | None = None
    alternatives: list[Facility] = Field(default_factory=list)
    navigation: NavigationInfo | None = None
    cross_sell_facilities: list[Facility] = Field(default_factory=list)
    reason_summary: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
