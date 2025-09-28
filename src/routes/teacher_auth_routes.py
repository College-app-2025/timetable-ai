from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from uuid import uuid4
from typing import Dict, Any

from src.models.teacher_auth import CreateTeacher, UpdateTeacher, LoginTeacher, ChangePasswordRequest
from src.services.teacher_auth_service import (
    teacher_auth_service,
    UserAlreadyExistError,
    DifferentPasswordNeeded,
    UserNotFoundError,
    InvalidCredentialsError,
)
from src.services.token_service import token_service


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


@router.get('/status_of_teacher_auth_server')
async def status():
    return {"message": "teacher auth route is up"}


@router.post("/Teacher_Auth")
async def create_teacher_route(user: CreateTeacher):
    try:
        p_id = str(uuid4())
        await teacher_auth_service.create_teacher(p_id, user)

        token_data = {"sub": p_id, "email": user.email, "role": "teacher"}
        access_token = await token_service.create_access_token(token_data)
        refresh_token = await token_service.create_refresh_token(token_data)

        return JSONResponse({
            "Success": True,
            "message": "Authentication successful",
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    except UserAlreadyExistError as e:
        return JSONResponse({"message": str(e)}, status_code=409)


@router.put("/Teacher_Profile_Update")
async def update_teacher_endpoint(
    user: UpdateTeacher,
    current_teacher: Dict[str, Any] = Depends(get_current_teacher)
):
    try:
        p_id = current_teacher["sub"]
        await teacher_auth_service.update_teacher(p_id, user)
        return JSONResponse({"Success": True, "message": "Teacher profile updated successfully"})
    except DifferentPasswordNeeded as e:
        return JSONResponse({"message": str(e)}, status_code=409)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.post("/Teacher_Log_in")
async def teacher_login_endpoint(login: LoginTeacher):
    try:
        response = await teacher_auth_service.login_teacher_detailed(login)
        return response
    except UserNotFoundError as e:
        return JSONResponse({"message": str(e)}, status_code=404)
    except InvalidCredentialsError as e:
        return JSONResponse({"message": str(e)}, status_code=401)


@router.put("/Teacher_Change_Password")
async def change_password_endpoint(
    password_data: ChangePasswordRequest,
    current_teacher: Dict[str, Any] = Depends(get_current_teacher)
):
    try:
        p_id = current_teacher["sub"]
        response = await teacher_auth_service.change_password(p_id, password_data)
        return JSONResponse(response)
    except InvalidCredentialsError as e:
        return JSONResponse({"message": str(e)}, status_code=401)
    except UserNotFoundError as e:
        return JSONResponse({"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.delete("/Teacher_Delete_Account")
async def delete_teacher_endpoint(current_teacher: Dict[str, Any] = Depends(get_current_teacher)):
    try:
        p_id = current_teacher["sub"]
        response = await teacher_auth_service.delete_teacher(p_id)
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.post("/Teacher_Logout")
async def logout_teacher(refresh_token: str):
    try:
        response = await teacher_auth_service.logout_teacher(refresh_token)
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.get("/Current_Teacher")
async def get_current_teacher_info(current_teacher: Dict[str, Any] = Depends(get_current_teacher)):
    try:
        return JSONResponse(current_teacher)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


