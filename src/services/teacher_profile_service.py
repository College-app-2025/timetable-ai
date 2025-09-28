from src.models.teacher_profile import CreateTeacherProfile, UpdateTeacherProfile, TeacherProfileResponse
from src.utils.prisma import db
from src.utils.logger_config import get_logger
from typing import Dict, Any, Optional
from src.services.teacher_auth_service import UserNotFoundError, ValidationError


logger = get_logger("teacher_profile")


class TeacherProfileNotFoundError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Profile for teacher {self.value} not found")


class TeacherProfileAlreadySetupError(Exception):
    def __init__(self, value: str):
        self.value = value
        super().__init__(f"Profile for teacher {self.value} is already set up")


class TeacherProfileService:
    def __init__(self):
        logger.info("TeacherProfileService initialized")

    async def setup_profile(self, p_id: str, profile_data: CreateTeacherProfile) -> Dict[str, Any]:
        try:
            logger.info(f"Setting up profile for teacher: {p_id}")

            teacher = await db.teacher.find_unique(where={"p_id": p_id})
            if not teacher:
                logger.error(f"Teacher not found: {p_id}")
                raise UserNotFoundError(p_id)

            if teacher.name != "__":
                logger.warning(f"Profile already set up for teacher: {p_id}")
                raise TeacherProfileAlreadySetupError(p_id)

            updated_teacher = await db.teacher.update(
                where={"p_id": p_id},
                data={
                    "name": profile_data.name,
                    "phone": profile_data.phone,
                    "department": profile_data.department,
                }
            )

            logger.info(f"Profile setup successfully for teacher: {p_id}")
            return {
                "p_id": updated_teacher.p_id,
                "name": updated_teacher.name,
                "phone": updated_teacher.phone,
                "department": updated_teacher.department,
                "message": "Profile setup successfully"
            }
        except (UserNotFoundError, TeacherProfileAlreadySetupError) as e:
            logger.warning(f"Profile setup failed for {p_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Profile setup failed for {p_id}: {str(e)}")
            raise

    async def update_profile(self, p_id: str, update_data: UpdateTeacherProfile) -> Dict[str, Any]:
        try:
            logger.info(f"Updating profile for teacher: {p_id}")

            teacher = await db.teacher.find_unique(where={"p_id": p_id})
            if not teacher:
                logger.error(f"Teacher not found: {p_id}")
                raise UserNotFoundError(p_id)

            update_fields = {}

            if update_data.name is not "__":
                update_fields["name"] = update_data.name
                logger.debug("Name updated in request")

            if update_data.phone is not "__":
                update_fields["phone"] = update_data.phone
                logger.debug("Phone updated in request")

            if update_data.department is not "__":
                update_fields["department"] = update_data.department
                logger.debug("Department updated in request")

            if not update_fields:
                logger.warning(f"No fields to update for teacher: {p_id}")
                raise ValidationError("No fields provided for update")

            updated_teacher = await db.teacher.update(
                where={"p_id": p_id},
                data=update_fields
            )

            logger.info(f"Profile updated successfully for teacher: {p_id}")
            return {
                "p_id": updated_teacher.p_id,
                "name": updated_teacher.name,
                "phone": updated_teacher.phone,
                "department": updated_teacher.department,
                "message": "Profile updated successfully"
            }
        except (UserNotFoundError, ValidationError) as e:
            logger.warning(f"Profile update failed for {p_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Profile update failed for {p_id}: {str(e)}")
            raise

    async def get_profile(self, p_id: str) -> TeacherProfileResponse:
        try:
            logger.info(f"Fetching profile for teacher: {p_id}")

            teacher = await db.teacher.find_unique(where={"p_id": p_id})
            if not teacher:
                logger.error(f"Teacher not found: {p_id}")
                raise UserNotFoundError(p_id)

            logger.info(f"Profile fetched successfully for teacher: {p_id}")
            return TeacherProfileResponse(
                p_id=teacher.p_id,
                name=teacher.name,
                phone=teacher.phone,
                department=teacher.department,
                proof_doc="Not_set_yet",
                institute_id=teacher.institute_id,
                teacher_id=teacher.teacher_id,
                email=teacher.email
            )
        except UserNotFoundError as e:
            logger.warning(f"Profile fetch failed for {p_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Profile fetch failed for {p_id}: {str(e)}")
            raise

    async def is_profile_complete(self, p_id: str) -> Dict[str, bool]:
        try:
            logger.debug(f"Checking profile completeness for teacher: {p_id}")
            teacher = await db.teacher.find_unique(where={"p_id": p_id})
            if not teacher:
                logger.error(f"Teacher not found: {p_id}")
                raise UserNotFoundError(p_id)

            is_complete = (
                teacher.name != "__" and
                teacher.phone != "__" and
                teacher.department != "__"
            )

            logger.debug(f"Profile completeness for {p_id}: {is_complete}")
            return {
                "p_id": p_id,
                "is_complete": is_complete,
                "profile_fields": {
                    "name_set": teacher.name != "__",
                    "phone_set": teacher.phone != "__",
                    "department_set": teacher.department != "__",
                }
            }
        except UserNotFoundError as e:
            logger.warning(f"Profile completeness check failed for {p_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Profile completeness check failed for {p_id}: {str(e)}")
            raise


teacher_profile_service = TeacherProfileService()



