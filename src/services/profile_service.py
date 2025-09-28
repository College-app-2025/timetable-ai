from src.models.profile import CreateProfile, UpdateProfile, ProfileResponse
from src.utils.prisma import db
from src.utils.logger_config import get_logger 
from typing import Dict, Any, Optional
from src.services.auth_service import UserNotFoundError, ValidationError


logger = get_logger("student_profile")


class ProfileNotFoundError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Profile for student {self.value} not found")


class ProfileAlreadySetupError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Profile for student {self.value} is already set up")


class StudentProfileService:
    
    def __init__(self):
        logger.info("StudentProfileService initialized")
    
    
    async def setup_profile(self, s_id: str, profile_data: CreateProfile) -> Dict[str, Any]:
        """Setup student profile for the first time"""
        try:
            logger.info(f"Setting up profile for student: {s_id}")
            
            # Check if student exists
            student = await db.student.find_unique(where={"s_id": s_id})
            if not student:
                logger.error(f"Student not found: {s_id}")
                raise UserNotFoundError(s_id)
            
            # Check if profile is already set up (name is not default value)
            if student.name != "__":
                logger.warning(f"Profile already set up for student: {s_id}")
                raise ProfileAlreadySetupError(s_id)
            
            # Update student with profile data
            updated_student = await db.student.update(
                where={"s_id": s_id},
                data={
                    "name": profile_data.name,
                    "phone": profile_data.phone,
                    "branch": profile_data.branch,
                    "semester": profile_data.semester
                }
            )
            
            logger.info(f"Profile setup successfully for student: {s_id}")
            
            return {
                "s_id": updated_student.s_id,
                "name": updated_student.name,
                "phone": updated_student.phone,
                "branch": updated_student.branch,
                "semester": updated_student.semester,
                "message": "Profile setup successfully"
            }
            
        except (UserNotFoundError, ProfileAlreadySetupError) as e:
            logger.warning(f"Profile setup failed for {s_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Profile setup failed for {s_id}: {str(e)}")
            raise
    
    
    async def update_profile(self, s_id: str, update_data: UpdateProfile) -> Dict[str, Any]:
        """Update existing student profile"""
        try:
            logger.info(f"Updating profile for student: {s_id}")
            
            # Check if student exists
            student = await db.student.find_unique(where={"s_id": s_id})
            if not student:
                logger.error(f"Student not found: {s_id}")
                raise UserNotFoundError(s_id)
            
            # Build update fields dict
            update_fields = {}
            
            if update_data.name is not "__":
                update_fields["name"] = update_data.name
                logger.debug("Name updated in request")
            
            if update_data.phone is not "__":
                update_fields["phone"] = update_data.phone
                logger.debug("Phone updated in request")
            
            if update_data.branch is not "__":
                update_fields["branch"] = update_data.branch
                logger.debug("Branch updated in request")
            
            if update_data.semester is not 0:
                update_fields["semester"] = update_data.semester
                logger.debug("Semester updated in request")
            
            # Only update if there are fields to update
            if not update_fields:
                logger.warning(f"No fields to update for student: {s_id}")
                raise ValidationError("No fields provided for update")
            
            # Update student profile
            updated_student = await db.student.update(
                where={"s_id": s_id},
                data=update_fields
            )
            
            logger.info(f"Profile updated successfully for student: {s_id}")
            
            return {
                "s_id": updated_student.s_id,
                "name": updated_student.name,
                "phone": updated_student.phone,
                "branch": updated_student.branch,
                "semester": updated_student.semester,
                "message": "Profile updated successfully"
            }
            
        except (UserNotFoundError, ValidationError) as e:
            logger.warning(f"Profile update failed for {s_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Profile update failed for {s_id}: {str(e)}")
            raise
    
    
    async def get_profile(self, s_id: str) -> ProfileResponse:
        """Get student profile by student ID"""
        try:
            logger.info(f"Fetching profile for student: {s_id}")
            
            student = await db.student.find_unique(
                where={"s_id": s_id}
            )
            
            if not student:
                logger.error(f"Student not found: {s_id}")
                raise UserNotFoundError(s_id)
            
            logger.info(f"Profile fetched successfully for student: {s_id}")
            
            return ProfileResponse(
                s_id=student.s_id,
                name=student.name,
                phone=student.phone,
                branch=student.branch,
                semester=student.semester,
                institute_id=student.institute_id,
                student_id=student.student_id,
                email=student.email
            )
            
        except UserNotFoundError as e:
            logger.warning(f"Profile fetch failed for {s_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Profile fetch failed for {s_id}: {str(e)}")
            raise
    
    
    async def is_profile_complete(self, s_id: str) -> Dict[str, bool]:
        """Check if student profile is complete"""
        try:
            logger.debug(f"Checking profile completeness for student: {s_id}")
            
            student = await db.student.find_unique(where={"s_id": s_id})
            
            if not student:
                logger.error(f"Student not found: {s_id}")
                raise UserNotFoundError(s_id)
            
            # Profile is complete if name is not the default value and other fields are set
            is_complete = (
                student.name != "__" and 
                student.phone != "__" and 
                student.branch != "__" and 
                student.semester > 0
            )
            
            logger.debug(f"Profile completeness for {s_id}: {is_complete}")
            
            return {
                "s_id": s_id,
                "is_complete": is_complete,
                "profile_fields": {
                    "name_set": student.name != "__",
                    "phone_set": student.phone != "__",
                    "branch_set": student.branch != "__",
                    "semester_set": student.semester > 0
                }
            }
            
        except UserNotFoundError as e:
            logger.warning(f"Profile completeness check failed for {s_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Profile completeness check failed for {s_id}: {str(e)}")
            raise
    
    
    async def get_profile_by_email(self, email: str) -> Optional[ProfileResponse]:
        """Get student profile by email"""
        try:
            logger.debug(f"Fetching profile by email: {email}")
            
            student = await db.student.find_unique(
                where={"email": email}
            )
            
            if not student:
                logger.debug(f"Student not found with email: {email}")
                return None
            
            return ProfileResponse(
                s_id=student.s_id,
                name=student.name,
                phone=student.phone,
                branch=student.branch,
                semester=student.semester,
                institute_id=student.institute_id,
                student_id=student.student_id,
                email=student.email
            )
            
        except Exception as e:
            logger.error(f"Profile fetch by email failed: {str(e)}")
            return None


# Create service instance
profile_service = StudentProfileService()
