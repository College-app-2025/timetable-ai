from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.models.auth import CreateStudent, UpdateStudent, LoginStudent, ChangePasswordRequest
from src.services import auth_service, token_service
from src.services.auth_service import UserAlreadyExistError, auth_service, DifferentPasswordNeeded, UserNotFoundError, InvalidCredentialsError
from src.services.token_service import token_service
from uuid import uuid4
from fastapi.responses import JSONResponse
from typing import Dict, Any


router = APIRouter()
security = HTTPBearer()


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


@router.get('/status_of_authentication_server')
async def status():
    return {
        "message": "user route is up"
    }


@router.post("/User_Auth")
async def create_user(user: CreateStudent):
    try:
        s_id = str(uuid4())
        await auth_service.create_student(s_id, user)

        token_data = {"sub": s_id, "email": user.email, "role":"student"}
        access_token = await token_service.create_access_token(token_data)
        refresh_token = await token_service.create_refresh_token(token_data)

        return JSONResponse({
            "Success": True,
            "message": "Authentication successful",
            "access_token" : access_token, 
            "refresh_token" : refresh_token
        })
    except UserAlreadyExistError as e:
        return JSONResponse({
            "message": str(e)
        }, status_code=409)


@router.put("/Profile_Update")
async def update_user_endpoint(
    user: UpdateStudent, 
    current_student: Dict[str, Any] = Depends(get_current_student)
):
    """
    Update current authenticated student's profile
    """
    try:
        s_id = current_student["sub"]  
        await auth_service.update_student(s_id, user)

        return JSONResponse({
            "Success": True,
            "message": "User profile updated successfully"
        })
    except DifferentPasswordNeeded as e:
        return JSONResponse({
            "message" : str(e)
        }, status_code=409)
    except Exception as e:
        return JSONResponse({
            "message": str(e)
        }, status_code=400)


@router.post("/User_Log_in")
async def user_login_endpoint(user_log_r : LoginStudent):
    try:
        response = await auth_service.login_student_detailed(user_log_r)
        return response
        
    except UserNotFoundError as e:
        return JSONResponse(
            {"message": str(e)},
            status_code=404   # Not Found
        )

    except InvalidCredentialsError as e:
        return JSONResponse(
            {"message": str(e)},
            status_code=401   # Unauthorized
        )


@router.put("/Change_Password")
async def change_password_endpoint(
    password_data: ChangePasswordRequest,
    current_student: Dict[str, Any] = Depends(get_current_student)
):
    """
    Change password for current authenticated student
    """
    try:
        s_id = current_student["sub"] 
        response = await auth_service.change_password(s_id, password_data)
        return JSONResponse(response)
    except InvalidCredentialsError as e:
        return JSONResponse({"message": str(e)}, status_code=401)
    except UserNotFoundError as e:
        return JSONResponse({"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.delete("/Delete_Account")
async def delete_student_endpoint(current_student: Dict[str, Any] = Depends(get_current_student)):
    """
    Delete current authenticated student's account
    """
    try:
        s_id = current_student["sub"]  # This is the s_id from token
        response = await auth_service.delete_student(s_id)
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.post("/User_Logout")
async def logout_user(refresh_token: str):
    try:
        response = await auth_service.logout_student(refresh_token)
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.get("/Current_Student")
async def get_current_student_info(current_student: Dict[str, Any] = Depends(get_current_student)):
    """
    Get current authenticated student's information
    """
    try:
        return JSONResponse(current_student)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.post("/Refresh_Token")
async def refresh_access_token(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    try:
        new_tokens = await token_service.refresh_token_rotation(refresh_token)
        return JSONResponse({
            "Success": True,
            "message": "Token refreshed successfully",
            **new_tokens
        })
    except HTTPException as e:
        return JSONResponse({"message": str(e.detail)}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


# Optional: Admin routes that might need s_id parameter (for admin functionality)
@router.get("/Admin_Get_Student/{s_id}")
async def admin_get_student(
    s_id: str,
    current_student: Dict[str, Any] = Depends(get_current_student)
):
    """
    Admin endpoint to get specific student (you can add admin role check here)
    """
    try:
        # You can add admin role verification here
        # if current_student["role"] != "admin":
        #     raise HTTPException(status_code=403, detail="Admin access required")
        
        student = await auth_service.get_student_by_id(s_id)
        if not student:
            return JSONResponse({"message": "Student not found"}, status_code=404)
            
        return JSONResponse({
            "s_id": student.s_id,
            "email": student.email,
            "institute_id": student.institute_id,
            "student_id": student.student_id
        })
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


# from fastapi import APIRouter
# from src.models.auth import CreateStudent, UpdateStudent, LoginStudent, ChangePasswordRequest
# from src.services import auth_service, token_service
# from src.services.auth_service import UserAlreadyExistError, auth_service, DifferentPasswordNeeded, UserNotFoundError, InvalidCredentialsError
# from src.services.token_service import token_service
# from uuid import uuid4
# from fastapi.responses import JSONResponse
# from fastapi import Header

# router = APIRouter()

# @router.get('/status_of_authentication_server')
# async def status():
#     return {
#         "message": "user route is up"
#     }

# @router.post("/User_Auth")
# async def create_user(user: CreateStudent):
#     try:
#         s_id = str(uuid4())
#         await auth_service.create_student(s_id, user)

#         token_data = {"sub": s_id, "email": user.email, "role":"student"}
#         access_token = await token_service.create_access_token(token_data)
#         refresh_token = await token_service.create_refresh_token(token_data)


#         return JSONResponse({
#             "Success": True,
#             "message": "Authentication successful",
#             "access_token" : access_token, 
#             "refresh_token" : refresh_token
#         })
#     except UserAlreadyExistError as e:
#         return JSONResponse({
#             "message": str(e)
#         }, status_code=409)
    

# @router.put("/Password_Update/{s_id}")
# async def update_user_endpoint(user: UpdateStudent, s_id :str):
#     try:
#         await auth_service.update_student(s_id, user)

#         return JSONResponse({
#             "Success": "True",
#             "message": "User password updated"
#         })
#     except DifferentPasswordNeeded as e:
#         return JSONResponse({
#             "message" : str(e)
#         }, status_code=409)
    

# @router.post("/User_Log_in")
# async def user_login_endpoint(user_log_r : LoginStudent):
#     try:
#         response = await auth_service.login_student_detailed(user_log_r)
#         return response
    
        
#     except UserNotFoundError as e:
#         return JSONResponse(
#             {"message": str(e)},
#             status_code=404   # Not Found
#         )

#     except InvalidCredentialsError as e:
#         return JSONResponse(
#             {"message": str(e)},
#             status_code=401   # Unauthorized
#         )


# @router.put("/Change_Password/{s_id}")
# async def change_password_endpoint(s_id: str, password_data: ChangePasswordRequest):
#     try:
#         response = await auth_service.change_password(s_id, password_data)
#         return JSONResponse(response)
#     except InvalidCredentialsError as e:
#         return JSONResponse({"message": str(e)}, status_code=401)
#     except UserNotFoundError as e:
#         return JSONResponse({"message": str(e)}, status_code=404)


# @router.delete("/Delete_User/{s_id}")
# async def delete_student_endpoint(s_id: str):
#     try:
#         response = await auth_service.delete_student(s_id)
#         return JSONResponse(response)
#     except Exception as e:
#         return JSONResponse({"message": str(e)}, status_code=400)


# @router.post("/User_Logout")
# async def logout_user(refresh_token: str):
#     try:
#         response = await auth_service.logout_student(refresh_token)
#         return JSONResponse(response)
#     except Exception as e:
#         return JSONResponse({"message": str(e)}, status_code=400)


# @router.get("/Current_Student")
# async def get_current_student(token: str = Header(...)):
#     try:
#         response = await auth_service.get_current_student_from_token(token)
#         return JSONResponse(response)
#     except InvalidCredentialsError as e:
#         return JSONResponse({"message": str(e)}, status_code=401)
