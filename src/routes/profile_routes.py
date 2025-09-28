from fastapi import APIRouter, Header, HTTPException, Depends
from src.models.profile import CreateProfile, UpdateProfile
from src.services.profile_service import profile_service, ProfileNotFoundError, ProfileAlreadySetupError
from src.services.auth_service import UserNotFoundError, ValidationError
from src.services.auth_service import auth_service
from fastapi.responses import JSONResponse
from src.services.token_service import token_service
from src.utils.logger_config import get_logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any


logger = get_logger("profile_routes")
router = APIRouter()
security = HTTPBearer()


@router.get('/status_of_profile_server')
async def status():
    return {
        "message": "profile route is up"
    }


async def get_current_student(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    
    try:
        token = credentials.credentials
        student_data = await auth_service.get_current_student_from_token(token)
        return student_data
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/Profile_Setup")
async def setup_profile_endpoint(profile_data: CreateProfile, current_student: Dict[str, Any] = Depends(get_current_student)):
    """Setup student profile for the first time"""
    try:
        s_id = current_student["sub"]  
        logger.info(f"Profile setup request for student: {s_id}")
        
        response = await profile_service.setup_profile(s_id, profile_data)
        
        return JSONResponse({
            "Success": True,
            "message": response["message"],
            "profile": {
                "name": response["name"],
                "phone": response["phone"],
                "branch": response["branch"],
                "semester": response["semester"]
            }
        })
        
    except ProfileAlreadySetupError as e:
        return JSONResponse({
            "Success": False,
            "message": str(e)
        }, status_code=409)
    
    except UserNotFoundError as e:
        return JSONResponse({
            "Success": False,
            "message": str(e)
        }, status_code=404)
    
    except Exception as e:
        logger.error(f"Profile setup failed: {str(e)}")
        return JSONResponse({
            "Success": False,
            "message": "Profile setup failed"
        }, status_code=500)


@router.put("/Profile_Update")
async def update_profile_endpoint(update_data: UpdateProfile, current_student: Dict[str, Any] = Depends(get_current_student)):
    """Update existing student profile"""
    try:
        s_id = current_student["sub"] 
        logger.info(f"Profile update request for student: {s_id}")
        
        response = await profile_service.update_profile(s_id, update_data)
        
        return JSONResponse({
            "Success": True,
            "message": response["message"],
            "profile": {
                "s_id": response["s_id"],
                "name": response["name"],
                "phone": response["phone"],
                "branch": response["branch"],
                "semester": response["semester"]
            }
        })
        
    except UserNotFoundError as e:
        return JSONResponse({
            "Success": False,
            "message": str(e)
        }, status_code=404)
    
    except ValidationError as e:
        return JSONResponse({
            "Success": False,
            "message": str(e)
        }, status_code=400)
    
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        return JSONResponse({
            "Success": False,
            "message": "Profile update failed"
        }, status_code=500)


@router.get("/Profile_Get")
async def get_profile_endpoint(current_student: Dict[str, Any] = Depends(get_current_student)):
    """Get current student's profile"""
    try:
        s_id = current_student["sub"] 
        logger.info(f"Profile fetch request for student: {s_id}")
        
        profile = await profile_service.get_profile(s_id)
        
        return JSONResponse({
            "Success": True,
            "message": "Profile fetched successfully",
            "profile": {
                "s_id": profile.s_id,
                "name": profile.name,
                "phone": profile.phone,
                "branch": profile.branch,
                "semester": profile.semester,
                "institute_id": profile.institute_id,
                "student_id": profile.student_id,
                "email": profile.email
            }
        })
        
    except UserNotFoundError as e:
        return JSONResponse({
            "Success": False,
            "message": str(e)
        }, status_code=404)
    
    except Exception as e:
        logger.error(f"Profile fetch failed: {str(e)}")
        return JSONResponse({
            "Success": False,
            "message": "Profile fetch failed"
        }, status_code=500)


@router.get("/Profile_Status")
async def check_profile_status_endpoint(current_student: Dict[str, Any] = Depends(get_current_student)):
    """Check if student profile is complete"""
    try:
        s_id = current_student["sub"] 
        logger.info(f"Profile status check for student: {s_id}")
        
        status = await profile_service.is_profile_complete(s_id)
        
        return JSONResponse({
            "Success": True,
            "message": "Profile status checked successfully",
            "status": status
        })
        
    except UserNotFoundError as e:
        return JSONResponse({
            "Success": False,
            "message": str(e)
        }, status_code=404)
    
    except Exception as e:
        logger.error(f"Profile status check failed: {str(e)}")
        return JSONResponse({
            "Success": False,
            "message": "Profile status check failed"
        }, status_code=500)


@router.get("/Profile_Get/{s_id}")
async def get_profile_by_id_endpoint(s_id: str):
    """Get student profile by ID (admin or public access)"""
    try:
        logger.info(f"Profile fetch request for student ID: {s_id}")
        
        profile = await profile_service.get_profile(s_id)
        
        return JSONResponse({
            "Success": True,
            "message": "Profile fetched successfully",
            "profile": {
                "s_id": profile.s_id,
                "name": profile.name,
                "phone": profile.phone,
                "branch": profile.branch,
                "semester": profile.semester,
                "institute_id": profile.institute_id,
                "student_id": profile.student_id,
                "email": profile.email
            }
        })
        
    except UserNotFoundError as e:
        return JSONResponse({
            "Success": False,
            "message": str(e)
        }, status_code=404)
    
    except Exception as e:
        logger.error(f"Profile fetch failed: {str(e)}")
        return JSONResponse({
            "Success": False,
            "message": "Profile fetch failed"
        }, status_code=500)