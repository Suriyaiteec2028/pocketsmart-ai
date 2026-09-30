from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.recommendation import RecommendationPlan
from app.models.saved import SavedRecommendation
from app.schemas.recommendation import ApiResponse, SaveRecommendationRequest
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("", response_model=ApiResponse, summary="List all recommendation plans for the current user")
def list_user_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all plans created by current user."""
    plans = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.user_id == current_user.id)
        .order_by(RecommendationPlan.created_at.desc())
        .all()
    )
    data = [
        {
            "id": p.id,
            "planner_type": p.planner_type,
            "title": p.title,
            "budget": p.budget,
            "estimated_total": p.estimated_total,
            "remaining_budget": p.remaining_budget,
            "currency": p.currency,
            "is_fallback": p.is_fallback,
            "created_at": p.created_at.isoformat(),
            "summary": p.result_data.get("summary", "") if p.result_data else ""
        }
        for p in plans
    ]
    return ApiResponse(success=True, data=data, message="Plans retrieved successfully")

@router.get("/{plan_id}", response_model=ApiResponse, summary="Get details of a specific plan")
def get_recommendation_details(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve complete recommendation plan ensuring user ownership."""
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation plan not found or access denied."
        )

    return ApiResponse(
        success=True,
        data={
            "id": plan.id,
            "planner_type": plan.planner_type,
            "title": plan.title,
            "budget": plan.budget,
            "estimated_total": plan.estimated_total,
            "remaining_budget": plan.remaining_budget,
            "currency": plan.currency,
            "input_data": plan.input_data,
            "result_data": plan.result_data,
            "is_fallback": plan.is_fallback,
            "created_at": plan.created_at.isoformat()
        },
        message="Recommendation plan retrieved"
    )

@router.post("/{plan_id}/save", response_model=ApiResponse, summary="Save an individual recommendation item to favorites")
def save_recommendation_item(
    plan_id: int,
    req: SaveRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save an item from a recommendation plan for the current user."""
    # Verify plan belongs to user
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated recommendation plan not found."
        )

    # Check if already saved
    existing = (
        db.query(SavedRecommendation)
        .filter(
            SavedRecommendation.user_id == current_user.id,
            SavedRecommendation.recommendation_plan_id == plan_id,
            SavedRecommendation.item_name == req.item_name
        )
        .first()
    )
    if existing:
        return ApiResponse(
            success=True,
            data={"id": existing.id, "saved": True},
            message="Item is already in your saved recommendations."
        )

    saved_item = SavedRecommendation(
        user_id=current_user.id,
        recommendation_plan_id=plan_id,
        item_name=req.item_name,
        item_category=req.item_category,
        platform=req.platform,
        estimated_price=req.estimated_price,
        recommendation_data=req.recommendation_data
    )
    db.add(saved_item)
    db.commit()
    db.refresh(saved_item)

    return ApiResponse(
        success=True,
        data={"id": saved_item.id, "saved": True},
        message=f"'{req.item_name}' saved to your collection!"
    )

@router.delete("/saved/{item_id}", response_model=ApiResponse, summary="Delete a saved recommendation item")
def delete_saved_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a saved recommendation item."""
    item = (
        db.query(SavedRecommendation)
        .filter(SavedRecommendation.id == item_id, SavedRecommendation.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved item not found."
        )

    db.delete(item)
    db.commit()
    return ApiResponse(success=True, data=None, message="Saved item removed.")

@router.delete("/{plan_id}", response_model=ApiResponse, summary="Delete an entire recommendation plan")
def delete_recommendation_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a plan and all its associated saved items."""
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or access denied."
        )

    db.delete(plan)
    db.commit()
    return ApiResponse(success=True, data=None, message="Plan deleted successfully.")

@router.post("/{plan_id}/reuse", response_model=ApiResponse, summary="Get original parameters to reuse/repopulate a plan")
def reuse_recommendation_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve original input data so the UI can populate the appropriate planner."""
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or access denied."
        )

    target_routes = {
        "home": "/home-planner",
        "party": "/party-planner",
        "jewelry": "/jewelry-planner"
    }

    return ApiResponse(
        success=True,
        data={
            "planner_type": plan.planner_type,
            "target_url": target_routes.get(plan.planner_type, "/dashboard"),
            "input_data": plan.input_data
        },
        message="Plan data ready for reuse."
    )
