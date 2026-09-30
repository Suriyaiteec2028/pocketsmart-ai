from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.jewelry import JewelryPlannerRequest
from app.schemas.recommendation import ApiResponse
from app.services.recommendation_engine import recommendation_engine
from app.utils.auth import get_current_user
from app.utils.validators import validate_and_save_image

router = APIRouter(prefix="/api", tags=["Jewelry Budget Planner"])

@router.post("/upload-image", response_model=ApiResponse, summary="Upload outfit image for visual jewelry analysis")
async def upload_outfit_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Safely validate and save outfit image (JPG, PNG, WEBP up to configured size limit).
    Returns relative image URL for preview and planner submission.
    """
    try:
        contents = await file.read()
        image_url = validate_and_save_image(contents, file.filename or "outfit.jpg")
        return ApiResponse(
            success=True,
            data={"image_url": image_url},
            message="Image uploaded successfully."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {str(e)}"
        )

@router.post("/generate-jewelry", response_model=ApiResponse, summary="Generate multimodal jewelry recommendations")
async def generate_jewelry_plan(
    req: JewelryPlannerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze user's occasion, budget, outfit description and uploaded outfit image
    to generate matching jewelry recommendations.
    """
    if req.budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be greater than zero."
        )

    try:
        result = await recommendation_engine.process_jewelry_plan(req, current_user, db)
        return ApiResponse(
            success=True,
            data=result,
            message="Jewelry recommendations generated successfully!"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to process jewelry plan: {str(e)}"
        )
