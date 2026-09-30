from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.recommendation import RecommendationPlan
from app.schemas.recommendation import ApiResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("", response_model=ApiResponse, summary="Fetch user planning history with filtering and sorting")
def get_user_history(
    planner_type: Optional[str] = Query(None, description="Filter by: home, party, jewelry or omit for all"),
    sort_by: str = Query("newest", description="newest, oldest, highest_budget, lowest_budget"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve history of recommendation plans strictly filtered by current user."""
    query = db.query(RecommendationPlan).filter(RecommendationPlan.user_id == current_user.id)

    # Filtering
    if planner_type and planner_type.lower() != "all":
        query = query.filter(RecommendationPlan.planner_type == planner_type.lower().strip())

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(RecommendationPlan.created_at.asc())
    elif sort_by == "highest_budget":
        query = query.order_by(RecommendationPlan.budget.desc())
    elif sort_by == "lowest_budget":
        query = query.order_by(RecommendationPlan.budget.asc())
    else:  # newest
        query = query.order_by(RecommendationPlan.created_at.desc())

    plans = query.all()

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
            "summary": p.result_data.get("summary", "") if p.result_data else "",
            "items_count": len(p.result_data.get("recommendations", [])) if p.result_data else 0
        }
        for p in plans
    ]

    return ApiResponse(
        success=True,
        data={
            "total_count": len(data),
            "plans": data
        },
        message="History loaded successfully"
    )

@router.delete("/{plan_id}", response_model=ApiResponse, summary="Delete history record")
def delete_history_item(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a plan history entry belonging to user."""
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found or unauthorized."
        )

    db.delete(plan)
    db.commit()
    return ApiResponse(success=True, data=None, message="History item deleted successfully.")
