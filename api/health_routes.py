from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend API is running"
    }

@router.get("/test")
async def test_endpoint():
    return {
        "status": "success",
        "message": "Test endpoint working",
        "data": {
            "timestamp": "2024-01-07",
            "service": "vgreen-backend"
        }
    }
