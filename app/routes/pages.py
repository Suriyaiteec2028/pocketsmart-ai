from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.models.user import User
from app.models.recommendation import RecommendationPlan
from app.models.saved import SavedRecommendation
from app.utils.auth import get_optional_current_user
from app.utils.budget import format_currency

router = APIRouter(tags=["Frontend Pages"])
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# Register Jinja2 filter for currency formatting
templates.env.filters["currency"] = format_currency

def require_page_auth(request: Request, db: Session) -> User:
    """Helper to require authentication on web page routes, redirecting if missing."""
    user = get_optional_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login?msg=Please+log+in+to+continue"}
        )
    return user

@router.get("/", response_class=HTMLResponse, summary="Landing Page")
def landing_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": None,
            "app_name": settings.APP_NAME,
            "app_tagline": settings.APP_TAGLINE
        }
    )

@router.get("/login", response_class=HTMLResponse, summary="Login Screen")
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "user": None,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/register", response_class=HTMLResponse, summary="Registration Screen")
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "user": None,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/logout", summary="Logout handler")
def logout_page(request: Request):
    response = RedirectResponse(url="/login?msg=You+have+been+logged+out", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

@router.get("/testimonials", response_class=HTMLResponse, summary="Testimonials Page")
def testimonials_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="testimonials.html",
        context={
            "user": user,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/dashboard", response_class=HTMLResponse, summary="User Dashboard")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)

    # Fetch stats
    total_plans = db.query(RecommendationPlan).filter(RecommendationPlan.user_id == user.id).count()
    home_plans = db.query(RecommendationPlan).filter(RecommendationPlan.user_id == user.id, RecommendationPlan.planner_type == "home").count()
    party_plans = db.query(RecommendationPlan).filter(RecommendationPlan.user_id == user.id, RecommendationPlan.planner_type == "party").count()
    jewelry_plans = db.query(RecommendationPlan).filter(RecommendationPlan.user_id == user.id, RecommendationPlan.planner_type == "jewelry").count()
    saved_count = db.query(SavedRecommendation).filter(SavedRecommendation.user_id == user.id).count()

    recent_plans = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.user_id == user.id)
        .order_by(RecommendationPlan.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "app_name": settings.APP_NAME,
            "stats": {
                "total_plans": total_plans,
                "home_plans": home_plans,
                "party_plans": party_plans,
                "jewelry_plans": jewelry_plans,
                "saved_count": saved_count
            },
            "recent_plans": recent_plans
        }
    )

@router.get("/home-planner", response_class=HTMLResponse, summary="Home Interior Planner Screen")
def home_planner_page(request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    return templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={
            "user": user,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/home-recommendations/{plan_id}", response_class=HTMLResponse, summary="Home Recommendations Screen")
def home_recommendations_page(plan_id: int, request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == user.id)
        .first()
    )
    if not plan:
        return RedirectResponse(url="/dashboard?error=Plan+not+found", status_code=status.HTTP_302_FOUND)

    # Fetch saved items list for active highlights
    saved_items = (
        db.query(SavedRecommendation.item_name)
        .filter(SavedRecommendation.user_id == user.id, SavedRecommendation.recommendation_plan_id == plan_id)
        .all()
    )
    saved_names = {s[0] for s in saved_items}

    return templates.TemplateResponse(
        request=request,
        name="home_recommendations.html",
        context={
            "user": user,
            "plan": plan,
            "saved_names": saved_names,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/party-planner", response_class=HTMLResponse, summary="Party Planner Screen")
def party_planner_page(request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    return templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={
            "user": user,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/party-recommendations/{plan_id}", response_class=HTMLResponse, summary="Party Recommendations Screen")
def party_recommendations_page(plan_id: int, request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == user.id)
        .first()
    )
    if not plan:
        return RedirectResponse(url="/dashboard?error=Plan+not+found", status_code=status.HTTP_302_FOUND)

    saved_items = (
        db.query(SavedRecommendation.item_name)
        .filter(SavedRecommendation.user_id == user.id, SavedRecommendation.recommendation_plan_id == plan_id)
        .all()
    )
    saved_names = {s[0] for s in saved_items}

    return templates.TemplateResponse(
        request=request,
        name="party_recommendations.html",
        context={
            "user": user,
            "plan": plan,
            "saved_names": saved_names,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/jewelry-planner", response_class=HTMLResponse, summary="Jewelry Planner Screen")
def jewelry_planner_page(request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    return templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={
            "user": user,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/jewelry-recommendations/{plan_id}", response_class=HTMLResponse, summary="Jewelry Recommendations Screen")
def jewelry_recommendations_page(plan_id: int, request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == user.id)
        .first()
    )
    if not plan:
        return RedirectResponse(url="/dashboard?error=Plan+not+found", status_code=status.HTTP_302_FOUND)

    saved_items = (
        db.query(SavedRecommendation.item_name)
        .filter(SavedRecommendation.user_id == user.id, SavedRecommendation.recommendation_plan_id == plan_id)
        .all()
    )
    saved_names = {s[0] for s in saved_items}

    return templates.TemplateResponse(
        request=request,
        name="jewelry_recommendations.html",
        context={
            "user": user,
            "plan": plan,
            "saved_names": saved_names,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/history", response_class=HTMLResponse, summary="History Screen")
def history_page(request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "user": user,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/recommendation/{plan_id}", response_class=HTMLResponse, summary="Recommendation Details Screen")
def recommendation_details_page(plan_id: int, request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    plan = (
        db.query(RecommendationPlan)
        .filter(RecommendationPlan.id == plan_id, RecommendationPlan.user_id == user.id)
        .first()
    )
    if not plan:
        return RedirectResponse(url="/history?error=Plan+not+found", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request=request,
        name="recommendation_details.html",
        context={
            "user": user,
            "plan": plan,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/saved", response_class=HTMLResponse, summary="Saved Recommendations Screen")
def saved_page(request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    saved_items = (
        db.query(SavedRecommendation)
        .filter(SavedRecommendation.user_id == user.id)
        .order_by(SavedRecommendation.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        request=request,
        name="saved.html",
        context={
            "user": user,
            "saved_items": saved_items,
            "app_name": settings.APP_NAME
        }
    )

@router.get("/profile", response_class=HTMLResponse, summary="User Profile Screen")
def profile_page(request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    total_plans = db.query(RecommendationPlan).filter(RecommendationPlan.user_id == user.id).count()
    total_saved = db.query(SavedRecommendation).filter(SavedRecommendation.user_id == user.id).count()
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user": user,
            "stats": {
                "total_plans": total_plans,
                "total_saved": total_saved
            },
            "app_name": settings.APP_NAME
        }
    )

@router.get("/settings", response_class=HTMLResponse, summary="Settings Screen")
def settings_page(request: Request, db: Session = Depends(get_db)):
    user = require_page_auth(request, db)
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "user": user,
            "app_name": settings.APP_NAME
        }
    )

