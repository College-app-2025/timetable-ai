from src.models.teacher_auth import CreateTeacher, UpdateTeacher, LoginTeacher, ChangePasswordRequest
from src.utils.prisma import db
from prisma.errors import UniqueViolationError
import bcrypt
from src.services.token_service import token_service
from src.utils.logger_config import get_logger
from typing import Dict, Any


logger = get_logger("teacher_auth")


class UserAlreadyExistError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"User with email {self.value} already exist")


class DifferentPasswordNeeded(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Password {self.value} is already in use")


class UserNotFoundError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"User with {self.value} dosen't exist")


class InvalidCredentialsError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Password {self.value} is not valid")


class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class TeacherAuthService:
    def __init__(self, verify_email_existence: bool = False):
        self.verify_email_existence = verify_email_existence
        logger.info("TeacherAuthService initialized")

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        logger.debug("Password hashed successfully")
        return hashed_pw

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            logger.debug(f"Password verification result: {'success' if result else 'failed'}")
            return result
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

    async def create_teacher(self, p_id: str, user: CreateTeacher):
        try:
            logger.info(f"Creating teacher account for: {user.email}")

            institute = await db.institute.find_unique(where={"id": user.institute_id})
            if not institute:
                logger.error(f"Institute not found: {user.institute_id}")
                raise ValidationError("Institute not found")

            hashed_password = self.hash_password(user.password.get_secret_value())

            created_teacher = await db.teacher.create(data={
                "p_id": p_id,
                "institute_id": user.institute_id,
                "teacher_id": user.teacher_id,
                "email": user.email,
                "password": hashed_password
            })

            logger.info(f"Teacher created successfully: {user.email} with ID: {p_id}")

            return {
                "p_id": created_teacher.p_id,
                "email": created_teacher.email,
                "institute_id": created_teacher.institute_id,
                "teacher_id": created_teacher.teacher_id,
                "message": "Teacher account created successfully"
            }

        except UniqueViolationError:
            logger.warning(f"Duplicate teacher creation attempt: {user.email}")
            raise UserAlreadyExistError(user.email)
        except Exception as e:
            logger.error(f"Teacher creation failed for {user.email}: {str(e)}")
            raise

    async def login_teacher_detailed(self, login_data: LoginTeacher):
        try:
            logger.info(f"Login attempt for: {login_data.email}")

            user_log = await self.get_teacher_by_email(login_data.email)
            if not user_log:
                logger.warning(f"Login attempt for non-existent user: {login_data.email}")
                raise UserNotFoundError(login_data.email)

            p_id = user_log.p_id

            if not self.verify_password(login_data.password.get_secret_value(), user_log.password):
                logger.warning(f"Invalid password attempt for: {login_data.email}")
                raise InvalidCredentialsError("entered")

            token_data = {"sub": p_id, "email": login_data.email, "role": "teacher"}
            access_token = await token_service.create_access_token(token_data)
            refresh_token = await token_service.create_refresh_token(token_data)

            logger.info(f"Successful login for: {login_data.email}")

            if user_log.name != "__":
                return {
                    "message": "Authentication Sucessfull",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "isSetup": True
                }

            return {
                "message": "Authentication Sucessfull",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "isSetup": False
            }

        except (UserNotFoundError, InvalidCredentialsError) as e:
            logger.warning(f"Login failed for {login_data.email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected login error for {login_data.email}: {str(e)}")
            raise InvalidCredentialsError("Authentication failed")

    async def get_current_teacher_from_token(self, token: str):
        try:
            logger.debug("Extracting user from token")
            payload = await token_service.verify_access_token(token)
            p_id = payload.get("sub")
            role = payload.get("role")

            if role != "teacher":
                logger.error("No teacher found in token")
                raise InvalidCredentialsError("Invalid token format")

            teacher = await self.get_teacher_by_id(p_id)

            return {
                "username": p_id,
                "email": teacher.email,
                "institute_id": teacher.institute_id,
                "teacher_id": teacher.teacher_id,
                "is_active": True,
                "role": "teacher"
            }
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise

    async def update_teacher(self, p_id: str, update_data: UpdateTeacher) -> Dict[str, Any]:
        try:
            logger.info(f"Updating teacher: {p_id}")

            update_fields = {}

            if update_data.email is not None:
                update_fields["email"] = update_data.email

            if update_data.teacher_id is not None:
                update_fields["teacher_id"] = update_data.teacher_id

            if update_data.institute_id is not None:
                update_fields["institute_id"] = update_data.institute_id

            if update_data.password is not None:
                update_fields["password"] = self.hash_password(update_data.password.get_secret_value())
                logger.debug("Password updated in request")

            updated_teacher = await db.teacher.update(
                where={"p_id": p_id},
                data=update_fields
            )

            logger.info(f"Teacher updated successfully: {p_id}")

            return {
                "institute_id": updated_teacher.institute_id,
                "email": updated_teacher.email,
                "teacher_id": updated_teacher.teacher_id,
                "message": "Teacher updated successfully"
            }
        except Exception as e:
            logger.error(f"Teacher update failed for {p_id}: {str(e)}")
            raise

    async def change_password(self, p_id: str, password_data: ChangePasswordRequest) -> Dict[str, str]:
        try:
            logger.info(f"Password change request for: {p_id}")
            teacher = await self.get_teacher_by_id(p_id)
            if not teacher:
                raise UserNotFoundError(p_id)

            if not self.verify_password(password_data.old_password.get_secret_value(), teacher.password):
                logger.warning(f"Invalid old password for password change: {p_id}")
                raise InvalidCredentialsError("Current password is incorrect")

            new_hashed_password = self.hash_password(password_data.new_password.get_secret_value())
            await db.teacher.update(
                where={"p_id": p_id},
                data={"password": new_hashed_password}
            )

            logger.info(f"Password changed successfully for: {p_id}")
            return {"message": "Password changed successfully"}
        except Exception as e:
            logger.error(f"Password change failed for {p_id}: {str(e)}")
            raise

    async def delete_teacher(self, p_id: str) -> None:
        try:
            logger.info(f"Deleting teacher: {p_id}")
            await db.teacher.delete(where={"p_id": p_id})
            logger.info(f"Teacher deleted successfully: {p_id}")
            return {"message": "Teacher deleted successfully"}
        except Exception as e:
            logger.error(f"Teacher deletion failed for {p_id}: {str(e)}")
            raise

    async def get_teacher_by_id(self, p_id: str):
        try:
            logger.info(f"Fetching teacher by ID: {p_id}")
            return await db.teacher.find_unique(where={"p_id": p_id})
        except Exception as e:
            logger.error(f"Teacher fetch failed for {p_id}: {str(e)}")
            raise

    async def get_teacher_by_email(self, email: str):
        try:
            logger.debug(f"Fetching teacher by email: {email}")
            return await db.teacher.find_unique(where={"email": email})
        except Exception as e:
            logger.error(f"Get teacher by email failed: {str(e)}")
            return None

    async def logout_teacher(self, refresh_token: str) -> Dict[str, str]:
        try:
            logger.info("Teacher logout request")
            result = await token_service.revoke_refresh_token(refresh_token)
            if result:
                logger.info("Teacher logged out successfully")
                return {"message": "Logged out successfully"}
            else:
                logger.warning("Logout failed - token not found")
                return {"message": "Already logged out"}
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise


teacher_auth_service = TeacherAuthService()



