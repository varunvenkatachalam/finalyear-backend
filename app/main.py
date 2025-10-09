from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .core.config import settings
from .api.endpoints import router as api_router
from .models.database import create_tables  # Add this import

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered event content generator for college events",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Event AI Generator API",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "generate_email": f"{settings.API_V1_STR}/generate-email",
            "generate_poster": f"{settings.API_V1_STR}/generate-poster",
            "generate_invitation": f"{settings.API_V1_STR}/generate-invitation"
        }
    }

@app.on_event("startup")
async def startup_event():
    print("🚀 Event AI Generator API starting up...")
    # Initialize database tables
    create_tables()
    print(f"📝 Documentation available at: http://localhost:8000/docs")

# Create static directory for generated images
os.makedirs("static/generated", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")