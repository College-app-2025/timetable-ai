from typing import Optional
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
import re


class TeacherProfileBase(BaseModel):
    @classmethod
    def validate_phone_format(cls, phone: str) -> None:
        if not re.match(r"^\+?1?\d{9,15}$", phone):
            raise PydanticCustomError(
                'invalid_phone',
                'Phone number must be between 9-15 digits and can start with +',
                {}
            )

    @classmethod
    def validate_name_format(cls, name: str) -> None:
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


class CreateTeacherProfile(TeacherProfileBase):
    name: str
    phone: str
    department: str
   

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

    @field_validator("department")
    @classmethod
    def department_validator(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise PydanticCustomError(
                'department_too_short',
                'Department must be at least 2 characters long',
                {}
            )
        return v.strip()


class UpdateTeacherProfile(TeacherProfileBase):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
   

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

    @field_validator("department")
    @classmethod
    def department_validator(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) < 2:
                raise PydanticCustomError(
                    'department_too_short',
                    'Department must be at least 2 characters long',
                    {}
                )
            return v.strip()
        return v


class TeacherProfileResponse(BaseModel):
    p_id: str
    name: str
    phone: str
    department: str
    institute_id: str
    teacher_id: str
    email: str

