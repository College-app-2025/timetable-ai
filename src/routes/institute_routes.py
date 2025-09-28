from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from src.models.institute import CreateInstitute, UpdateInstitute, LoginInstitute, ChangePasswordRequest, CreateClassroom, UpdateClassroom, CreateSubject, UpdateSubject
from src.services.institute_service import institute_service, NotFoundError, UserAlreadyExistError, InvalidCredentialsError, UserNotFoundError


router = APIRouter()
security = HTTPBearer()


# Institute authentication - JWT based
async def get_current_institute(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        institute_data = await institute_service.get_current_institute_from_token(token)
        return institute_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get('/status_of_institute_server')
async def status():
    return {"message": "institute route is up"}


# Institute Management Routes
@router.post('/Institute_Setup')
async def create_institute(payload: CreateInstitute):
    try:
        result = await institute_service.create_institute(payload)
        # Generate JWT token for the created institute
        token_data = {"sub": result["institute_id"], "email": payload.email, "role": "institute"}
        access_token = await institute_service.token_service.create_access_token(token_data)
        refresh_token = await institute_service.token_service.create_refresh_token(token_data)
        
        return JSONResponse({
            "Success": True,
            "message": "Institute created successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "institute_id": result["institute_id"]
        }, status_code=201)
    except UserAlreadyExistError as e:
        return JSONResponse({"message": str(e)}, status_code=409)
    except ValueError as e:
        return JSONResponse({"message": str(e)}, status_code=403)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.post('/Institute_Login')
async def institute_login(login_data: LoginInstitute):
    try:
        result = await institute_service.login_institute_detailed(login_data)
        return JSONResponse(result)
    except UserNotFoundError as e:
        return JSONResponse({"message": str(e)}, status_code=404)
    except InvalidCredentialsError as e:
        return JSONResponse({"message": str(e)}, status_code=401)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.put('/Institute_Update')
async def update_institute(payload: UpdateInstitute, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    institute_id = current_institute["institute_id"]
    result = await institute_service.update_institute(institute_id, payload)
    return JSONResponse(result)


@router.put('/Institute_Change_Password')
async def change_password(payload: ChangePasswordRequest, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    institute_id = current_institute["institute_id"]
    try:
        result = await institute_service.change_password(institute_id, payload)
        return JSONResponse(result)
    except InvalidCredentialsError as e:
        return JSONResponse({"message": str(e)}, status_code=401)
    except UserNotFoundError as e:
        return JSONResponse({"message": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)


@router.delete('/Institute_Delete')
async def delete_institute(current_institute: Dict[str, Any] = Depends(get_current_institute)):
    institute_id = current_institute["institute_id"]
    result = await institute_service.delete_institute(institute_id)
    return JSONResponse(result)


@router.get('/Current_Institute')
async def get_current_institute_info(current_institute: Dict[str, Any] = Depends(get_current_institute)):
    return JSONResponse(current_institute)


# Students / Teachers admin destructive actions
@router.delete('/Admin/Delete_Student/{s_id}')
async def admin_delete_student(s_id: str, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    result = await institute_service.delete_student(s_id)
    return JSONResponse(result)


@router.delete('/Admin/Delete_Teacher/{p_id}')
async def admin_delete_teacher(p_id: str, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    result = await institute_service.delete_teacher(p_id)
    return JSONResponse(result)


# Classrooms
@router.post('/Admin/Classroom')
async def add_classroom(payload: CreateClassroom, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    # Auto-fill institute_id from JWT token
    payload.institute_id = current_institute["institute_id"]
    result = await institute_service.add_classroom(payload)
    status_code = 200 if 'id' in result else 409 if result.get('message') == 'Classroom already exists' else 400
    return JSONResponse(result, status_code=status_code)


@router.put('/Admin/Classroom/{classroom_id}')
async def update_classroom(classroom_id: str, payload: UpdateClassroom, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    result = await institute_service.update_classroom(classroom_id, payload)
    return JSONResponse(result)


@router.delete('/Admin/Classroom/{classroom_id}')
async def delete_classroom(classroom_id: str, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    result = await institute_service.delete_classroom(classroom_id)
    return JSONResponse(result)


@router.get('/Admin/Classrooms')
async def list_classrooms(current_institute: Dict[str, Any] = Depends(get_current_institute)):
    institute_id = current_institute["institute_id"]
    result = await institute_service.list_classrooms(institute_id)
    return JSONResponse(result)


# Subjects
@router.post('/Admin/Subject')
async def add_subject(payload: CreateSubject, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    # Auto-fill institute_id from JWT token
    payload.institute_id = current_institute["institute_id"]
    result = await institute_service.add_subject(payload)
    status_code = 200 if 'id' in result else 409 if result.get('message') == 'Subject already exists' else 400
    return JSONResponse(result, status_code=status_code)


@router.put('/Admin/Subject/{subject_id}')
async def update_subject(subject_id: str, payload: UpdateSubject, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    result = await institute_service.update_subject(subject_id, payload)
    return JSONResponse(result)


@router.delete('/Admin/Subject/{subject_id}')
async def delete_subject(subject_id: str, current_institute: Dict[str, Any] = Depends(get_current_institute)):
    result = await institute_service.delete_subject(subject_id)
    return JSONResponse(result)


@router.get('/Admin/Subjects')
async def list_subjects(
    semester: Optional[int] = Query(default=None),
    branch: Optional[str] = Query(default=None),
    current_institute: Dict[str, Any] = Depends(get_current_institute)
):
    institute_id = current_institute["institute_id"]
    result = await institute_service.list_subjects(institute_id, semester, branch)
    return JSONResponse(result)


