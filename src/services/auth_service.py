from src.models.auth import CreateStudent, UpdateStudent, LoginStudent, ChangePasswordRequest
from src.utils.prisma import db
# from src.prisma_client.errors import UniqueViolationError
from prisma.errors import UniqueViolationError
import bcrypt
from src.services.token_service import token_service
from src.utils.logger_config import get_logger 
from typing import Dict, Any, Optional  
import uuid


logger = get_logger("student_auth")


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


class StudentAuthService:
    
    def __init__(self, verify_email_existence: bool = False):
        self.verify_email_existence = verify_email_existence
        logger.info("StudentAuthService initialized") 

    @staticmethod
    def hash_password(password: str) -> str:
        """ADD: Password hashing method"""
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

    
    async def create_student(self, s_id: str, user: CreateStudent):
            
        try:
            logger.info(f"Creating student account for: {user.email}")
            
            institute = await db.institute.find_unique(where={"id": user.institute_id})
            if not institute:
                logger.error(f"Institute not found: {user.institute_id}")
                raise ValidationError("Institute not found")
            
            hashed_password = self.hash_password(user.password.get_secret_value())

            created_student = await db.student.create(data={
                "s_id": s_id,  
                "institute_id": user.institute_id,
                "student_id": user.student_id,
                "email": user.email,
                "password": hashed_password
            })
            
            logger.info(f"Student created successfully: {user.email} with ID: {s_id}")
            
            return {
                "s_id": created_student.s_id,
                "email": created_student.email,
                "institute_id": created_student.institute_id,
                "student_id": created_student.student_id,
                "message": "Student account created successfully"
            }
            
        except UniqueViolationError:
            logger.warning(f"Duplicate student creation attempt: {user.email}")
            raise UserAlreadyExistError(user.email)
        except Exception as e:
            logger.error(f"Student creation failed for {user.email}: {str(e)}")
            raise
        
        
    async def login_student_detailed(self, login_data: LoginStudent):

        try:
            logger.info(f"Login attempt for: {login_data.email}")
            
            user_log = await self.get_student_by_email(login_data.email)
            s_id = user_log.s_id
            
            
            if not user_log:
                logger.warning(f"Login attempt for non-existent user: {login_data.email}")
                raise UserNotFoundError(login_data.email)
            
            
            if not self.verify_password(login_data.password.get_secret_value(), user_log.password):
                logger.warning(f"Invalid password attempt for: {login_data.email}")
                raise InvalidCredentialsError("entered")
            
            token_data = {"sub":s_id, "email": login_data.email, "role":"student"}
            access_token = await token_service.create_access_token(token_data)
            refresh_token = await token_service.create_refresh_token(token_data)

            logger.info(f"Successful login for: {login_data.email}")

            if user_log.name != "__":
                return {
                    "message": "Authentication Sucessfull",
                    "access_token": access_token,
                    "refresh_token" : refresh_token,
                    "isSetup" : True
                } 
            
            return {
                "message": "Authentication Sucessfull",
                "access_token": access_token,
                "refresh_token" : refresh_token,
                "isSetup" : False
                } 
        
        except (UserNotFoundError, InvalidCredentialsError) as e:
            logger.warning(f"Login failed for {login_data.email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected login error for {login_data.email}: {str(e)}")
            raise InvalidCredentialsError("Authentication failed")
    
    
    async def get_current_student_from_token(self, token: str):

         try:
            logger.debug("Extracting user from token")
        
            payload = await token_service.verify_access_token(token)
            s_id = payload.get("sub")
            role = payload.get("role")

            if role != "student":
                logger.error("No student found in token")
                raise InvalidCredentialsError("Invalid token format")
            
            student = await self.get_student_by_id(s_id)
            
            # user = await prisma.user.find_unique(where={'username': username})
            
            return {
                "username": s_id,
                "email": student.email,
                "institute_id": student.institute_id,
                "student_id": student.student_id,
                "is_active": True,
                "role": "student"
            }
         
         except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise
    
    async def update_student(self, s_id: str, update_data: UpdateStudent) -> Dict[str, Any]: 
        try:
            logger.info(f"Updating student: {s_id}")
            
            update_fields = {}
                
            if update_data.email is not None:
                update_fields["email"] = update_data.email

            if update_data.student_id is not None:
                update_fields["student_id"] = update_data.student_id

            if update_data.institute_id is not None:
                update_fields["institute_id"] = update_data.institute_id   
                
            if update_data.password is not None:
                update_fields["password"] = self.hash_password(update_data.password.get_secret_value())
                logger.debug("Password updated in request")

            updated_student = await db.student.update(
                where={"id": s_id}, 
                data=update_fields
            )
            
            logger.info(f"Student updated successfully: {s_id}")
            
            return {
                "institute_id": updated_student.institute_id,
                "email": updated_student.email,
                "student_id": updated_student.student_id,
                "message": "Student updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Student update failed for {s_id}: {str(e)}")
            raise


    async def change_password(self, s_id: str, password_data: ChangePasswordRequest) -> Dict[str, str]:
       
        try:
            logger.info(f"Password change request for: {s_id}")
            
            student = await self.get_student_by_id(s_id)
            if not student:
                raise UserNotFoundError(s_id)
            
            if not self.verify_password(password_data.old_password.get_secret_value(), student.password):
                logger.warning(f"Invalid old password for password change: {s_id}")
                raise InvalidCredentialsError("Current password is incorrect")
            
            new_hashed_password = self.hash_password(password_data.new_password.get_secret_value())
            await db.student.update(
                where={"id": s_id},
                data={
                    "password": new_hashed_password
                }
            )
            
            logger.info(f"Password changed successfully for: {s_id}")
            return {"message": "Password changed successfully"}
            
        except Exception as e:
            logger.error(f"Password change failed for {s_id}: {str(e)}")
            raise    
    
    
    async def delete_student(self, s_id: str) -> None:

         try:
            logger.info(f"Deleting student: {s_id}")

            await db.student.delete(where={
                "s_id": s_id
            })

            logger.info(f"Student deleted successfully: {s_id}")
            return {"message": "Student deleted successfully"}
         
         except Exception as e:
            logger.error(f"Student deletion failed for {s_id}: {str(e)}")
            raise


    async def get_student_by_id(self, s_id: str) :

        try:
            logger.info(f"Fetching student by ID: {s_id}")
            return await db.student.find_unique(where={
                "s_id": s_id
            })
            
        except Exception as e:
            logger.error(f"Student deletion failed for {s_id}: {str(e)}")
            raise
            
    
    async def get_student_by_email(self, email: str) :

        try:
            logger.debug(f"Fetching student by email: {email}")
            return await db.student.find_unique(where={
                "email": email
            })
        except Exception as e:
            logger.error(f"Get student by email failed: {str(e)}")
            return None
        

    async def logout_student(self, refresh_token: str) -> Dict[str, str]:
       
        try:
            logger.info("Student logout request")
            result = await token_service.revoke_refresh_token(refresh_token)
            if result:
                logger.info("Student logged out successfully")
                return {"message": "Logged out successfully"}
            else:
                logger.warning("Logout failed - token not found")
                return {"message": "Already logged out"}
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise
    

    

auth_service = StudentAuthService()