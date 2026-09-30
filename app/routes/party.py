from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.party import PartyPlannerRequest
from app.schemas.recommendation import ApiResponse
from app.services.recommendation_engine import recommendation_engine
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Party / Event Planner"])

@router.post("/generate-party", response_model=ApiResponse, summary="Generate party/event budget plan")
async def generate_party_plan(
    req: PartyPlannerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Intelligently divide event budget across venue, catering, decoration,
    entertainment, and optional accommodation.
    """
    if req.budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total budget must be greater than zero."
        )

    if req.guest_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest count must be at least 1."
        )

    try:
        result = await recommendation_engine.process_party_plan(req, current_user, db)
        return ApiResponse(
            success=True,
            data=result,
            message="Party budget plan generated successfully!"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to process party plan: {str(e)}"
        )
