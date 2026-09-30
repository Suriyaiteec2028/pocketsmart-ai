from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, UserUpdateRequest
from app.schemas.recommendation import ApiResponse
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user, get_optional_current_user
from app.utils.validators import validate_email_format, validate_password_strength

router = APIRouter(prefix="/api", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse, summary="Register a new user account")
def register_user(req: UserRegisterRequest, response: Response, db: Session = Depends(get_db)):
    """Create a new user with validation and issue JWT token in cookie & response."""
    # 1. Validate email format
    if not validate_email_format(req.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address."
        )

    # 2. Check password strength and confirmation
    is_valid, msg = validate_password_strength(req.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    if req.password != req.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )

    # 3. Check for existing user
    existing = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in instead."
        )

    # 4. Hash password and persist user
    hashed = hash_password(req.password)
    user = User(
        name=req.name.strip(),
        email=req.email.lower().strip(),
        password_hash=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 5. Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "name": user.name},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Set secure cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # True in HTTPS production
    )

    user_data = UserResponse.model_validate(user).model_dump()
    return ApiResponse(
        success=True,
        data={"access_token": access_token, "user": user_data},
        message="Registration successful! Welcome to PocketSmart AI."
    )

@router.post("/login", response_model=ApiResponse, summary="Authenticate user and obtain JWT token")
def login_user(req: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate email & password, setting cookie and returning token."""
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 7 if req.remember_me else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "name": user.name},
        expires_delta=timedelta(minutes=expire_minutes)
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=expire_minutes * 60,
        samesite="lax",
        secure=False
    )

    user_data = UserResponse.model_validate(user).model_dump()
    return ApiResponse(
        success=True,
        data={"access_token": access_token, "user": user_data},
        message="Login successful. Redirecting to your dashboard..."
    )

@router.post("/logout", response_model=ApiResponse, summary="Clear user authentication session")
def logout_user(response: Response):
    """Clear access_token cookie."""
    response.delete_cookie(key="access_token")
    return ApiResponse(
        success=True,
        data=None,
        message="Successfully logged out."
    )

@router.get("/session-info", response_model=ApiResponse, summary="Retrieve current authenticated session details")
def get_session_info(current_user: User = Depends(get_current_user)):
    """Return profile info of the currently logged in user."""
    return ApiResponse(
        success=True,
        data={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat()
        },
        message="Session active"
    )

@router.get("/session-data", response_model=ApiResponse, summary="Retrieve session status without raising 401")
def get_session_data(optional_user: User = Depends(get_optional_current_user)):
    """Safe session checker for frontend navigation state."""
    if not optional_user:
        return ApiResponse(success=True, data={"authenticated": False}, message="Not authenticated")
    return ApiResponse(
        success=True,
        data={
            "authenticated": True,
            "user": {
                "id": optional_user.id,
                "name": optional_user.name,
                "email": optional_user.email
            }
        },
        message="Authenticated"
    )

@router.get("/token", summary="Get active JWT token from header or cookie")
def get_token(request: Request, current_user: User = Depends(get_current_user)):
    """Return active JWT token for API clients."""
    from app.utils.auth import extract_token_from_request
    token = extract_token_from_request(request)
    return {"access_token": token, "token_type": "bearer", "user_id": current_user.id}

@router.put("/profile", response_model=ApiResponse, summary="Update user profile details")
def update_profile(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update name or password for the current user."""
    if req.name and req.name.strip():
        current_user.name = req.name.strip()
    
    if req.new_password:
        if not req.current_password or not verify_password(req.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required and must be correct to change password."
            )
        is_valid, msg = validate_password_strength(req.new_password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        current_user.password_hash = hash_password(req.new_password)
    
    db.commit()
    db.refresh(current_user)
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user).model_dump(),
        message="Profile updated successfully!"
    )

