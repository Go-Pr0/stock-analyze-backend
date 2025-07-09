from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.research import router as research_router
from api.auth import router as auth_router
from database import engine, Base

# Create database tables
if engine:
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Research API", version="2.0.0")

# Enable CORS for frontend communication
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

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

@app.get("/")
async def root():
    return {"message": "Stock Research API v2.0 with Authentication is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected" if engine else "not configured"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)