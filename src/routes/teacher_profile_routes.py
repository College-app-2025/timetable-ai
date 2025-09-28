from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import Dict, Any

from src.models.teacher_profile import CreateTeacherProfile, UpdateTeacherProfile
from src.services.teacher_profile_service import (
    teacher_profile_service,
    TeacherProfileAlreadySetupError,
    TeacherProfileNotFoundError,
)
from src.services.teacher_auth_service import UserNotFoundError
from src.services.teacher_auth_service import teacher_auth_service


router = APIRouter()
security = HTTPBearer()


async def get_current_teacher(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    try:
        token = credentials.credentials
        teacher_data = await teacher_auth_service.get_current_teacher_from_token(token)
        return teacher_data
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get('/status_of_teacher_profile_server')
async def status():
    return {"message": "teacher profile route is up"}


@router.post("/Teacher_Profile_Setup")
async def setup_profile_endpoint(profile_data: CreateTeacherProfile, current_teacher: Dict[str, Any] = Depends(get_current_teacher)):
    try:
        p_id = current_teacher["sub"]
        response = await teacher_profile_service.setup_profile(p_id, profile_data)
        return JSONResponse({
            "Success": True,
            "message": response["message"],
            "profile": {
                "name": response["name"],
                "phone": response["phone"],
                "department": response["department"],
            }
        })
    except TeacherProfileAlreadySetupError as e:
        return JSONResponse({"Success": False, "message": str(e)}, status_code=409)
    except UserNotFoundError as e:
        return JSONResponse({"Success": False, "message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"Success": False, "message": "Profile setup failed"}, status_code=500)


@router.put("/Teacher_Profile_Update")
async def update_profile_endpoint(update_data: UpdateTeacherProfile, current_teacher: Dict[str, Any] = Depends(get_current_teacher)):
    try:
        p_id = current_teacher["sub"]
        response = await teacher_profile_service.update_profile(p_id, update_data)
        return JSONResponse({
            "Success": True,
            "message": response["message"],
            "profile": {
                "p_id": response["p_id"],
                "name": response["name"],
                "phone": response["phone"],
                "department": response["department"],
            }
        })
    except UserNotFoundError as e:
        return JSONResponse({"Success": False, "message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"Success": False, "message": "Profile update failed"}, status_code=500)


@router.get("/Teacher_Profile_Get")
async def get_profile_endpoint(current_teacher: Dict[str, Any] = Depends(get_current_teacher)):
    try:
        p_id = current_teacher["sub"]
        profile = await teacher_profile_service.get_profile(p_id)
        return JSONResponse({
            "Success": True,
            "message": "Profile fetched successfully",
            "profile": {
                "p_id": profile.p_id,
                "name": profile.name,
                "phone": profile.phone,
                "department": profile.department,
                "institute_id": profile.institute_id,
                "teacher_id": profile.teacher_id,
                "email": profile.email
            }
        })
    except UserNotFoundError as e:
        return JSONResponse({"Success": False, "message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"Success": False, "message": "Profile fetch failed"}, status_code=500)


@router.get("/Teacher_Profile_Status")
async def check_profile_status_endpoint(current_teacher: Dict[str, Any] = Depends(get_current_teacher)):
    try:
        p_id = current_teacher["sub"]
        status = await teacher_profile_service.is_profile_complete(p_id)
        return JSONResponse({"Success": True, "message": "Profile status checked successfully", "status": status})
    except UserNotFoundError as e:
        return JSONResponse({"Success": False, "message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"Success": False, "message": "Profile status check failed"}, status_code=500)


@router.get("/Teacher_Profile_Get/{p_id}")
async def get_profile_by_id_endpoint(p_id: str):
    try:
        profile = await teacher_profile_service.get_profile(p_id)
        return JSONResponse({
            "Success": True,
            "message": "Profile fetched successfully",
            "profile": {
                "p_id": profile.p_id,
                "name": profile.name,
                "phone": profile.phone,
                "department": profile.department,
                "institute_id": profile.institute_id,
                "teacher_id": profile.teacher_id,
                "email": profile.email
            }
        })
    except UserNotFoundError as e:
        return JSONResponse({"Success": False, "message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"Success": False, "message": "Profile fetch failed"}, status_code=500)

