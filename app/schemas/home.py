from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RoomItemDetail(BaseModel):
    name: str
    quantity: int = Field(default=1, ge=1)
    preferred_style: Optional[str] = "Modern"
    preferred_material: Optional[str] = "Wood"
    color_preference: Optional[str] = "Neutral"
    priority: str = Field(default="Medium", pattern="^(High|Medium|Low)$")

class HomePlannerRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Total budget in currency amount")
    currency: str = Field(default="INR", description="Currency symbol/code")
    home_type: str = Field(default="Apartment", description="Apartment, House, Studio, Villa, Other")
    rooms: List[str] = Field(..., min_length=1, description="Selected rooms to furnish")
    room_items: Optional[Dict[str, List[RoomItemDetail]]] = Field(
        default_factory=dict, 
        description="Detailed items per room"
    )
    overall_style: str = Field(
        default="Modern", 
        description="Modern, Minimalist, Traditional, Luxury, Scandinavian, Industrial, Budget Friendly"
    )
    budget_allocation_preference: str = Field(
        default="Balanced",
        description="Balanced, Essentials First, Lowest Cost, Premium Focus"
    )
    additional_requirements: Optional[str] = Field(
        default=None,
        description="Free text preferences or notes"
    )

class HomeRecommendationResult(BaseModel):
    planner: str = "home"
    budget: float
    allocated_budget: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    estimated_total: float
    remaining_budget: float
    summary: str
    is_fallback: bool = False
