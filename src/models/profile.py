from typing import Optional
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
import re


class ProfileBase(BaseModel):
    
    @classmethod
    def validate_phone_format(cls, phone: str) -> None:
        """Validate phone number format"""
        if not re.match(r"^\+?1?\d{9,15}$", phone):
            raise PydanticCustomError(
                'invalid_phone',
                'Phone number must be between 9-15 digits and can start with +',
                {}
            )
    
    @classmethod
    def validate_name_format(cls, name: str) -> None:
        """Validate name format"""
        if len(name.strip()) < 2:
            raise PydanticCustomError(
                'name_too_short',
                'Name must be at least 2 characters long',
                {}
            )
        if not re.match(r"^[a-zA-Z\s]+$", name.strip()):
            raise PydanticCustomError(
                'invalid_name',
                'Name must contain only letters and spaces',
                {}
            )


class CreateProfile(ProfileBase):
    name: str
    phone: str
    branch: str
    semester: int
   

    @field_validator("name")
    @classmethod
    def name_validator(cls, v: str) -> str:
        cls.validate_name_format(v)
        return v.strip()
    
    @field_validator("phone")
    @classmethod
    def phone_validator(cls, v: str) -> str:
        cls.validate_phone_format(v)
        return v
    
    @field_validator("semester")
    @classmethod
    def semester_validator(cls, v: int) -> int:
        if v < 1 or v > 8:
            raise PydanticCustomError(
                'invalid_semester',
                'Semester must be between 1 and 8',
                {}
            )
        return v
    
    @field_validator("branch")
    @classmethod
    def branch_validator(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise PydanticCustomError(
                'branch_too_short',
                'Branch must be at least 2 characters long',
                {}
            )
        return v.strip()


class UpdateProfile(ProfileBase):
    name: Optional[str] = None
    phone: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    
    @field_validator("name")
    @classmethod
    def name_validator(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cls.validate_name_format(v)
            return v.strip()
        return v
    
    @field_validator("phone")
    @classmethod
    def phone_validator(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cls.validate_phone_format(v)
        return v
    
    @field_validator("semester")
    @classmethod
    def semester_validator(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 8):
            raise PydanticCustomError(
                'invalid_semester',
                'Semester must be between 1 and 8',
                {}
            )
        return v
    
    @field_validator("branch")
    @classmethod
    def branch_validator(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) < 2:
                raise PydanticCustomError(
                    'branch_too_short',
                    'Branch must be at least 2 characters long',
                    {}
                )
            return v.strip()
        return v


class ProfileResponse(BaseModel):
    s_id: str
    name: str
    phone: str
    branch: str
    semester: int
    institute_id: str
    student_id: str
    email: str