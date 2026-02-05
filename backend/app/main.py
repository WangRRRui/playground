from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.database import init_db
from app.config import UPLOAD_DIR, BASE_DIR
from app.auth import verify_password, create_access_token
from app.schemas import LoginRequest, TokenResponse
from app.routers import posts, tags, upload, settings

# Create FastAPI app
app = FastAPI(
    title="Blog API",
    description="Backend API for cyberpunk blog",
    version="1.0.0",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/admin", StaticFiles(directory=str(BASE_DIR / "admin"), html=True), name="admin")

# Include routers
app.include_router(posts.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/")
def root():
    """Redirect to API docs."""
    return RedirectResponse(url="/docs")


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """Login with admin password to get JWT token."""
    if not verify_password(request.password):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    access_token = create_access_token(data={"sub": "admin"})
    return TokenResponse(access_token=access_token)


@app.get("/api/v1/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
