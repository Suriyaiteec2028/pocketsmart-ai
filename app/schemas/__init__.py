from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse
)
from app.schemas.recommendation import (
    ApiResponse,
    RecommendationItemSchema,
    SaveRecommendationRequest,
    SavedRecommendationResponse,
    RecommendationPlanSummary
)
from app.schemas.home import HomePlannerRequest, HomeRecommendationResult
from app.schemas.party import PartyPlannerRequest, PartyRecommendationResult
from app.schemas.jewelry import JewelryPlannerRequest, JewelryRecommendationResult, OutfitAnalysis

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "UserResponse",
    "TokenResponse",
    "ApiResponse",
    "RecommendationItemSchema",
    "SaveRecommendationRequest",
    "SavedRecommendationResponse",
    "RecommendationPlanSummary",
    "HomePlannerRequest",
    "HomeRecommendationResult",
    "PartyPlannerRequest",
    "PartyRecommendationResult",
    "JewelryPlannerRequest",
    "JewelryRecommendationResult",
    "OutfitAnalysis"
]
