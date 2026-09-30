from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.home import HomePlannerRequest
from app.schemas.recommendation import ApiResponse
from app.services.recommendation_engine import recommendation_engine
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Home Interior Planner"])

@router.post("/generate-home", response_model=ApiResponse, summary="Generate smart home interior budget plan")
async def generate_home_plan(
    req: HomePlannerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Intelligently allocate user's home budget across selected rooms
    and generate personalized furniture/decor recommendations.
    """
    if req.budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be greater than zero."
        )

    if not req.rooms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select at least one room."
        )

    try:
        result = await recommendation_engine.process_home_plan(req, current_user, db)
        return ApiResponse(
            success=True,
            data=result,
            message="Home interior plan generated successfully!"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to process home plan: {str(e)}"
        )
