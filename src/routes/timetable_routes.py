"""
Timetable routes for the SIH Timetable Optimization System.
Integrates ML functionality with the main FastAPI application.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.services.institute_service import institute_service
from src.ml.api.routes import ml_router

router = APIRouter()
security = HTTPBearer()


async def get_current_institute(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current institute from JWT token."""
    token = credentials.credentials
    try:
        institute_data = await institute_service.get_current_institute_from_token(token)
        return institute_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# Include ML routes with prefix
router.include_router(ml_router, prefix="/ml", tags=["Timetable Optimization"])


@router.get('/timetable/status')
async def timetable_status():
    """Check timetable service status."""
    return {"message": "Timetable optimization service is running", "status": "healthy"}

