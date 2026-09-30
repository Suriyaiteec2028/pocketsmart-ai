from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: str = ""
    error_code: Optional[str] = None

class RecommendationItemSchema(BaseModel):
    category: str
    product_name: str
    platform: str = "Amazon"
    estimated_price: float
    quantity: int = 1
    total_price: float
    reason: str
    priority: str = "Medium"
    product_url: Optional[str] = None
    image_url: Optional[str] = None

class SaveRecommendationRequest(BaseModel):
    item_name: str
    item_category: Optional[str] = None
    platform: Optional[str] = None
    estimated_price: Optional[float] = None
    recommendation_data: Dict[str, Any] = Field(default_factory=dict)

class SavedRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recommendation_plan_id: Optional[int]
    item_name: str
    item_category: Optional[str]
    platform: Optional[str]
    estimated_price: Optional[float]
    recommendation_data: Dict[str, Any]
    created_at: datetime

class RecommendationPlanSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    planner_type: str
    title: str
    budget: float
    estimated_total: float
    remaining_budget: float
    currency: str
    is_fallback: bool
    created_at: datetime
    summary: Optional[str] = None
