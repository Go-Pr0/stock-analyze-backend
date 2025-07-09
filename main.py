from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.research import router as research_router
from api.auth import router as auth_router
from database import engine, Base
from models.user_models import User
from models.research_models import ResearchReport

# Create database tables (with error handling)
try:
    if engine:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Run startup migration for competitive analysis
        try:
            from startup_migration import check_and_migrate
            check_and_migrate()
        except Exception as migration_error:
            print(f"⚠️ Startup migration failed: {migration_error}")
            print("🔄 Service will continue, but competitive analysis may not work properly")
            
except Exception as e:
    print(f"⚠️ Database initialization failed: {e}")
    print("🔄 Service will continue without database (some features may be limited)")

app = FastAPI(title="Stock Research API", version="2.0.0")

# Enable CORS for frontend communication
# Default includes local development and Railway production URLs
default_origins = "http://localhost:5173,http://localhost:3000,http://localhost:80"
allowed_origins = os.getenv("ALLOWED_ORIGINS", default_origins).split(",")

# Add Railway frontend URL if provided
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(research_router)

@app.get("/api/health")
async def health_check():
    """Simple health check that doesn't depend on external services"""
    return {"status": "ok", "service": "backend"}

@app.get("/api/health/detailed")
async def detailed_health_check():
    """Detailed health check that includes database status"""
    return {"status": "ok", "database": "connected" if engine else "not configured"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)