from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from app.api import users, jobs, candidates
from app.db.base import Base
from app.db.session import engine
from app.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create tables (in production, we use Alembic migrations instead)
if settings.ENVIRONMENT != "production":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TalentLens API",
    description="Resume screening application API",
    version="1.0.0",
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc"
)

# Configure CORS
allowed_origins = ["*"] if settings.ENVIRONMENT == "development" else [
    "https://talentlens.onrender.com",
    "https://talentlens-frontend.onrender.com",
    # Add your frontend URLs here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["talentlens-api.onrender.com", "*.onrender.com"]
    )

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])


@app.get("/")
async def root():
    return {"message": "Welcome to TalentLens API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}