from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.init_db import init_db
from app.routes import auth, home, party, jewelry, recommendations, history, pages
from app.schemas.recommendation import ApiResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    yield

app = FastAPI(
    title="PocketSmart AI",
    description="Your Smart Budget & Recommendation Assistant – AI-powered budgeting and personalized recommendations for Home Interiors, Parties & Events, and Jewelry Styling.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and uploads directories
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# Health check & Startup verification
@app.get("/api/health", tags=["Health"], response_model=ApiResponse, summary="System health check")
def health_check():
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "gemini_configured": bool(settings.GEMINI_API_KEY),
            "model": settings.GEMINI_MODEL,
            "database": "connected"
        },
        message="PocketSmart AI service is operational"
    )

@app.get("/api/startup", tags=["Health"], response_model=ApiResponse, summary="Application startup check")
def startup_check():
    return ApiResponse(
        success=True,
        data={
            "app_name": settings.APP_NAME,
            "version": "1.0.0",
            "environment": settings.APP_ENV
        },
        message="Application startup verified"
    )

# Include all route modules
app.include_router(auth.router)
app.include_router(home.router)
app.include_router(party.router)
app.include_router(jewelry.router)
app.include_router(recommendations.router)
app.include_router(history.router)
app.include_router(pages.router)

# Friendly exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # If API route, return structured JSON
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "message": "An unexpected server error occurred. Please try again.",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )
    # If page route, redirect with friendly error or render
    return RedirectResponse(url="/dashboard?error=An+unexpected+error+occurred", status_code=status.HTTP_302_FOUND)
