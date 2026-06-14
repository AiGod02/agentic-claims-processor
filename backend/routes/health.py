from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Plum Claims Processing API",
        "version": "1.0.0"
    }
