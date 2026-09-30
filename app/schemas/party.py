from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PartyPlannerRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Total party budget")
    currency: str = Field(default="INR", description="Currency code")
    event_type: str = Field(..., description="Birthday, Wedding, Engagement, Anniversary, Corporate Event, Baby Shower, Get Together, Other")
    guest_count: int = Field(..., gt=0, description="Number of expected guests")
    event_date: Optional[str] = Field(default=None, description="Event date (YYYY-MM-DD)")
    venue_type: str = Field(default="Hall", description="Home, Hall, Hotel, Outdoor, Restaurant, Not Decided")
    location: Optional[str] = Field(default="City Center", description="City / area")
    catering_preference: str = Field(default="Vegetarian", description="Vegetarian, Non-Vegetarian, Both, Snacks Only, Full Meal")
    decoration_level: str = Field(default="Standard", description="Basic, Standard, Premium")
    entertainment: str = Field(default="Music", description="None, Basic, Music, DJ, Live Performance, Custom")
    need_accommodation: bool = Field(default=False, description="Whether hotel/guest rooms are needed")
    room_count: Optional[int] = Field(default=0, ge=0, description="Number of accommodation rooms if needed")
    additional_requirements: Optional[str] = Field(default=None, description="Special notes or themes")

class PartyRecommendationResult(BaseModel):
    planner: str = "party"
    budget: float
    allocated_budget: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    estimated_total: float
    remaining_budget: float
    summary: str
    event_summary: Dict[str, Any]
    is_fallback: bool = False
