from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class JewelryPlannerRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Total budget in currency amount")
    currency: str = Field(default="INR", description="Currency symbol/code")
    occasion: str = Field(..., description="Wedding, Engagement, Birthday, Party, Festival, Office, Casual, Gift")
    jewelry_type: str = Field(default="Any", description="Necklace, Earrings, Bracelet, Ring, Bangles, Set, Any")
    preferred_style: str = Field(default="Elegant", description="Traditional, Modern, Minimal, Elegant, Luxury, Statement, Fusion")
    preferred_material: str = Field(default="Any", description="Gold, Silver, Artificial, Imitation, Diamond Look, Any")
    preferred_color: str = Field(default="Any", description="Gold, Silver, Rose Gold, Multi-color, Any")
    outfit_description: Optional[str] = Field(default=None, description="Description of outfit, colors, pattern, neckline")
    image_url: Optional[str] = Field(default=None, description="Path to uploaded outfit image if provided")

class OutfitAnalysis(BaseModel):
    dominant_colors: List[str] = Field(default_factory=list)
    style: str = "Modern / Elegant"
    recommended_tones: List[str] = Field(default_factory=list)
    interpretation: str = ""

class JewelryRecommendationResult(BaseModel):
    planner: str = "jewelry"
    budget: float
    outfit_analysis: OutfitAnalysis
    recommendations: List[Dict[str, Any]]
    estimated_total: float
    remaining_budget: float
    summary: str
    is_fallback: bool = False
