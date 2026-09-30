import logging
from typing import Dict, Any, Union
from sqlalchemy.orm import Session

from app.models.recommendation import RecommendationPlan
from app.models.saved import SavedRecommendation
from app.models.user import User
from app.schemas.home import HomePlannerRequest
from app.schemas.party import PartyPlannerRequest
from app.schemas.jewelry import JewelryPlannerRequest
from app.services.home_service import HomeService
from app.services.party_service import PartyService
from app.services.jewelry_service import JewelryService

logger = logging.getLogger("pocketsmart.engine")

class RecommendationEngine:
    """Central engine orchestrating validations, planner services, persistence, and ranking."""

    @staticmethod
    async def process_home_plan(req: HomePlannerRequest, user: User, db: Session) -> Dict[str, Any]:
        """Process home interior planning request, generate plan, persist to DB, and return result."""
        result = await HomeService.generate_plan(req)
        
        # Save to database
        title = f"{req.overall_style} {req.home_type} Interior"
        plan_record = RecommendationPlan(
            user_id=user.id,
            planner_type="home",
            title=title,
            budget=result["budget"],
            estimated_total=result["estimated_total"],
            remaining_budget=result["remaining_budget"],
            currency=req.currency,
            input_data=req.model_dump(),
            result_data=result,
            is_fallback=result.get("is_fallback", False)
        )
        db.add(plan_record)
        db.commit()
        db.refresh(plan_record)

        result["plan_id"] = plan_record.id
        result["created_at"] = plan_record.created_at.isoformat()
        return result

    @staticmethod
    async def process_party_plan(req: PartyPlannerRequest, user: User, db: Session) -> Dict[str, Any]:
        """Process party planning request, generate plan, persist to DB, and return result."""
        result = await PartyService.generate_plan(req)

        title = f"{req.event_type} Celebration ({req.guest_count} Guests)"
        plan_record = RecommendationPlan(
            user_id=user.id,
            planner_type="party",
            title=title,
            budget=result["budget"],
            estimated_total=result["estimated_total"],
            remaining_budget=result["remaining_budget"],
            currency=req.currency,
            input_data=req.model_dump(),
            result_data=result,
            is_fallback=result.get("is_fallback", False)
        )
        db.add(plan_record)
        db.commit()
        db.refresh(plan_record)

        result["plan_id"] = plan_record.id
        result["created_at"] = plan_record.created_at.isoformat()
        return result

    @staticmethod
    async def process_jewelry_plan(req: JewelryPlannerRequest, user: User, db: Session) -> Dict[str, Any]:
        """Process jewelry styling request, generate plan, persist to DB, and return result."""
        result = await JewelryService.generate_plan(req)

        title = f"{req.preferred_style} Jewelry for {req.occasion}"
        plan_record = RecommendationPlan(
            user_id=user.id,
            planner_type="jewelry",
            title=title,
            budget=result["budget"],
            estimated_total=result["estimated_total"],
            remaining_budget=result["remaining_budget"],
            currency=req.currency,
            input_data=req.model_dump(),
            result_data=result,
            is_fallback=result.get("is_fallback", False)
        )
        db.add(plan_record)
        db.commit()
        db.refresh(plan_record)

        result["plan_id"] = plan_record.id
        result["created_at"] = plan_record.created_at.isoformat()
        return result

recommendation_engine = RecommendationEngine()
