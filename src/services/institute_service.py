from typing import Dict, Any, Optional, List
from src.utils.prisma import db
from src.utils.logger_config import get_logger
from src.services.token_service import TokenService
from prisma.errors import UniqueViolationError
from src.models.institute import (
    CreateInstitute,
    UpdateInstitute,
    LoginInstitute,
    ChangePasswordRequest,
    CreateClassroom,
    UpdateClassroom,
    CreateSubject,
    UpdateSubject
)
import bcrypt


logger = get_logger("institute_service")


class NotFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class UserAlreadyExistError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"User with email {self.value} already exist")

class InvalidCredentialsError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Password {self.value} is not valid")

class UserNotFoundError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"User with {self.value} dosen't exist")


class InstituteService:
    def __init__(self):
        self.token_service = TokenService()
        logger.info("InstituteService initialized")

    # Password methods (same as student/teacher pattern)
    @staticmethod
    def hash_password(password: str) -> str:
        """Password hashing method"""
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        logger.debug("Password hashed successfully")
        return hashed_pw

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Password verification method"""
        try:
            result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            logger.debug(f"Password verification result: {'success' if result else 'failed'}")  
            return result
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

    # Hardcoded admin emails list (you can modify this)
    ALLOWED_ADMIN_EMAILS = [
        "admin1@gmail.com",
        "admin2@gmail.com", 
        "admin3@gmail.com"
    ]

    def is_admin_email(self, email: str) -> bool:
        """Check if email is in hardcoded admin list"""
        return email in self.ALLOWED_ADMIN_EMAILS

    # Institute Management
    async def create_institute(self, payload: CreateInstitute) -> Dict[str, Any]:
        try:
            # Check if email is in admin list
            if not self.is_admin_email(payload.email):
                raise ValueError("Email not authorized for admin access")
            
            logger.info(f"Creating institute account for: {payload.email}")
            
            hashed_password = self.hash_password(payload.password.get_secret_value())
            
            created = await db.institute.create(data={
                "institute_id": payload.institute_id,
                "name": payload.name,
                "type": payload.type,
                "address": payload.address,
                "phone": payload.phone,
                "email": payload.email,
                "password": hashed_password,
            })
            return {"institute_id": created.institute_id, "message": "Institute created successfully"}
        except UniqueViolationError:
            raise UserAlreadyExistError(payload.email)
        except Exception as e:
            logger.error(f"Institute creation failed for {payload.email}: {str(e)}")
            raise

    async def update_institute(self, institute_id: str, payload: UpdateInstitute) -> Dict[str, Any]:
        update_data = {}
        if payload.name is not None:
            update_data["name"] = payload.name
        if payload.type is not None:
            update_data["type"] = payload.type
        if payload.address is not None:
            update_data["address"] = payload.address
        if payload.phone is not None:
            update_data["phone"] = payload.phone
        if payload.email is not None:
            update_data["email"] = payload.email
        if payload.password is not None:
            update_data["password"] = self.hash_password(payload.password.get_secret_value())

        updated = await db.institute.update(where={"institute_id": institute_id}, data=update_data)
        return {"institute_id": updated.institute_id, "message": "Institute updated successfully"}

    async def delete_institute(self, institute_id: str) -> Dict[str, str]:
        await db.institute.delete(where={"institute_id": institute_id})
        return {"message": "Institute deleted successfully"}

    async def get_institute_by_id(self, institute_id: str) -> Dict[str, Any]:
        institute = await db.institute.find_unique(where={"institute_id": institute_id})
        if not institute:
            raise NotFoundError("Institute not found")
        return {
            "institute_id": institute.institute_id,
            "name": institute.name,
            "type": institute.type,
            "address": institute.address,
            "phone": institute.phone,
            "email": institute.email,
            "created_at": institute.created_at,
            "updated_at": institute.updated_at
        }

    async def get_institute_by_email(self, email: str) -> Dict[str, Any]:
        institute = await db.institute.find_unique(where={"email": email})
        if not institute:
            raise UserNotFoundError(email)
        return {
            "institute_id": institute.institute_id,
            "name": institute.name,
            "type": institute.type,
            "address": institute.address,
            "phone": institute.phone,
            "email": institute.email,
            "created_at": institute.created_at,
            "updated_at": institute.updated_at
        }

    # Login with password verification
    async def login_institute_detailed(self, login_data: LoginInstitute) -> Dict[str, Any]:
        try:
            logger.info(f"Login attempt for institute: {login_data.email}")
            
            institute = await db.institute.find_unique(where={"email": login_data.email})
            if not institute:
                logger.warning(f"Login attempt for non-existent institute: {login_data.email}")
                raise UserNotFoundError(login_data.email)
            
            if not self.verify_password(login_data.password.get_secret_value(), institute.password):
                logger.warning(f"Invalid password attempt for: {login_data.email}")
                raise InvalidCredentialsError("entered")
            
            token_data = {"sub": institute.institute_id, "email": login_data.email, "role": "institute"}
            access_token = await self.token_service.create_access_token(token_data)
            refresh_token = await self.token_service.create_refresh_token(token_data)

            logger.info(f"Successful login for institute: {login_data.email}")

            return {
                "message": "Authentication Successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "institute_id": institute.institute_id
            }
        
        except (UserNotFoundError, InvalidCredentialsError) as e:
            logger.warning(f"Login failed for {login_data.email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected login error for {login_data.email}: {str(e)}")
            raise InvalidCredentialsError("Authentication failed")

    # Change password
    async def change_password(self, institute_id: str, password_data: ChangePasswordRequest) -> Dict[str, str]:
        try:
            logger.info(f"Password change request for institute: {institute_id}")
            
            institute = await db.institute.find_unique(where={"institute_id": institute_id})
            if not institute:
                raise UserNotFoundError(institute_id)
            
            if not self.verify_password(password_data.old_password.get_secret_value(), institute.password):
                logger.warning(f"Invalid old password for password change: {institute_id}")
                raise InvalidCredentialsError("Current password is incorrect")
            
            new_hashed_password = self.hash_password(password_data.new_password.get_secret_value())
            await db.institute.update(
                where={"institute_id": institute_id},
                data={"password": new_hashed_password}
            )
            
            logger.info(f"Password changed successfully for institute: {institute_id}")
            return {"message": "Password changed successfully"}
            
        except Exception as e:
            logger.error(f"Password change failed for {institute_id}: {str(e)}")
            raise

    # JWT Token methods for institute
    async def create_institute_token(self, institute_id: str) -> str:
        return self.token_service.create_access_token(data={"institute_id": institute_id, "role": "institute"})

    async def get_current_institute_from_token(self, token: str) -> Dict[str, Any]:
        payload = self.token_service.verify_token(token)
        if payload.get("role") != "institute":
            raise ValueError("Invalid token role")
        institute_id = payload.get("institute_id")
        if not institute_id:
            raise ValueError("Institute ID not found in token")
        return await self.get_institute_by_id(institute_id)

    # Students
    async def delete_student(self, s_id: str) -> Dict[str, str]:
        await db.student.delete(where={"s_id": s_id})
        return {"message": "Student deleted"}

    # Teachers
    async def delete_teacher(self, p_id: str) -> Dict[str, str]:
        await db.teacher.delete(where={"p_id": p_id})
        return {"message": "Teacher deleted"}

    # Classrooms (infrastructure)
    async def add_classroom(self, payload: CreateClassroom) -> Dict[str, Any]:
        try:
            created = await db.classroom.create(data={
                "institute_id": payload.institute_id,
                "room_id": payload.room_id,
                "capacity": payload.capacity,
                "type": payload.type,
                "building": payload.building,
                "floor": payload.floor,
            })
            return {"id": created.id, "message": "Classroom added"}
        except UniqueViolationError:
            return {"message": "Classroom already exists"}

    async def update_classroom(self, classroom_id: str, payload: UpdateClassroom) -> Dict[str, Any]:
        updated = await db.classroom.update(where={"id": classroom_id}, data={
            **({"capacity": payload.capacity} if payload.capacity is not None else {}),
            **({"type": payload.type} if payload.type is not None else {}),
            **({"building": payload.building} if payload.building is not None else {}),
            **({"floor": payload.floor} if payload.floor is not None else {}),
        })
        return {"id": updated.id, "message": "Classroom updated"}

    async def delete_classroom(self, classroom_id: str) -> Dict[str, str]:
        await db.classroom.delete(where={"id": classroom_id})
        return {"message": "Classroom deleted"}

    async def list_classrooms(self, institute_id: str) -> List[Dict[str, Any]]:
        rooms = await db.classroom.find_many(where={"institute_id": institute_id})
        return [
            {
                "id": r.id,
                "room_id": r.room_id,
                "capacity": r.capacity,
                "type": r.type,
                "building": r.building,
                "floor": r.floor,
            } for r in rooms
        ]

    # Subjects (Academic structure)
    async def add_subject(self, payload: CreateSubject) -> Dict[str, Any]:
        try:
            created = await db.subject.create(data={
                "institute_id": payload.institute_id,
                "subject_code": payload.subject_code,
                "name": payload.name,
                "semester": payload.semester,
                "branch": payload.branch,
                "type": payload.type,
                "credits": payload.hours_per_week,  # mapping hours to credits if you don't have hours
            })
            return {"id": created.id, "message": "Subject added"}
        except UniqueViolationError:
            return {"message": "Subject already exists"}

    async def update_subject(self, subject_id: str, payload: UpdateSubject) -> Dict[str, Any]:
        updated = await db.subject.update(where={"id": subject_id}, data={
            **({"name": payload.name} if payload.name is not None else {}),
            **({"semester": payload.semester} if payload.semester is not None else {}),
            **({"branch": payload.branch} if payload.branch is not None else {}),
            **({"type": payload.type} if payload.type is not None else {}),
            **({"credits": payload.hours_per_week} if payload.hours_per_week is not None else {}),
        })
        return {"id": updated.id, "message": "Subject updated"}

    async def delete_subject(self, subject_id: str) -> Dict[str, str]:
        await db.subject.delete(where={"id": subject_id})
        return {"message": "Subject deleted"}

    async def list_subjects(self, institute_id: str, semester: Optional[int] = None, branch: Optional[str] = None) -> List[Dict[str, Any]]:
        where: Dict[str, Any] = {"institute_id": institute_id}
        if semester is not None:
            where["semester"] = semester
        if branch is not None:
            where["branch"] = branch

        subs = await db.subject.find_many(where=where)
        return [
            {
                "id": s.id,
                "subject_code": s.subject_code,
                "name": s.name,
                "semester": s.semester,
                "branch": s.branch,
                "type": s.type,
                "hours_per_week": s.credits,
            } for s in subs
        ]


institute_service = InstituteService()


