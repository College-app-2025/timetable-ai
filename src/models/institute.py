from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr, SecretStr
from pydantic_core import PydanticCustomError
from datetime import datetime
import re


class Userbase(BaseModel): 
    @classmethod    
    def validate_email_format(cls, email: EmailStr):
        if not email.endswith("@gmail.com"):
            raise PydanticCustomError(
                'invalid_email_domain',
                'Email must be from @gmail.com domain',
                {}
            )

    @classmethod
    def validate_password_logic(cls, password: str) -> None:
        """Shared password validation logic"""
        if len(password) < 6:
            raise PydanticCustomError(
                'password_too_short',
                'Password must be at least 6 characters long',
                {}
            )
        
        if not re.search(r"[A-Z]", password):
            raise PydanticCustomError(
                'password_missing_uppercase',
                'Password must contain at least one uppercase letter',
                {}
            )
        
        if not re.search(r"[a-z]", password):
            raise PydanticCustomError(
                'password_missing_lowercase', 
                'Password must contain at least one lowercase letter',
                {}
            )
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise PydanticCustomError(
                'password_missing_special',
                'Password must contain at least one special character',
                {}
            )

class CreateInstitute(Userbase):
    institute_id: str
    name : str
    type : str
    address : str
    phone : str
    email : EmailStr
    password : SecretStr

    @field_validator("email")
    @classmethod
    def email_validator(cls, e: EmailStr) -> EmailStr:
        cls.validate_email_format(e)
        return e

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: SecretStr) -> SecretStr:
        cls.validate_password_logic(v.get_secret_value())
        return v
    

class UpdateInstitute(Userbase):
    institute_id: Optional[str]
    name : Optional[str]
    type : Optional[str]
    address : Optional[str]
    phone : Optional[str]
    email : Optional[EmailStr]
    password : Optional[SecretStr]

    @field_validator("email")
    @classmethod
    def email_validator(cls, e: Optional[EmailStr]) -> Optional[EmailStr]:
        if e is not None:
            cls.validate_email_format(e)
        return e

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        if v is not None:
            cls.validate_password_logic(v.get_secret_value())
        return v

class LoginInstitute(Userbase):
    email: EmailStr
    password: SecretStr

    @field_validator("email")
    @classmethod
    def email_validator(cls, e: EmailStr) -> EmailStr:
        cls.validate_email_format(e)
        return e

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: SecretStr) -> SecretStr:
        cls.validate_password_logic(v.get_secret_value())
        return v

class ChangePasswordRequest(Userbase):
    old_password: SecretStr
    new_password: SecretStr

    @field_validator("old_password")
    @classmethod
    def old_password_validator(cls, v: SecretStr) -> SecretStr:
        cls.validate_password_logic(v.get_secret_value())
        return v

    @field_validator("new_password")
    @classmethod
    def new_password_validator(cls, v: SecretStr) -> SecretStr:
        cls.validate_password_logic(v.get_secret_value())
        return v    


class CreateClassroom(BaseModel):
    institute_id: str
    room_id: str
    capacity: int
    type: str  # "lecture" | "lab" | other
    building: str
    floor: int

    @field_validator("capacity")
    @classmethod
    def capacity_validator(cls, v: int) -> int:
        if v <= 0:
            raise PydanticCustomError('invalid_capacity', 'Capacity must be positive', {})
        return v

    @field_validator("type")
    @classmethod
    def type_validator(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise PydanticCustomError('invalid_type', 'Type cannot be empty', {})
        return v.strip()


class UpdateClassroom(BaseModel):
    capacity: Optional[int] = None
    type: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None

    @field_validator("capacity")
    @classmethod
    def capacity_validator(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise PydanticCustomError('invalid_capacity', 'Capacity must be positive', {})
        return v


class CreateSubject(BaseModel):
    institute_id: str
    subject_code: str
    name: str
    semester: int
    branch: str
    type: str  # "theory" | "lab" | "project"
    hours_per_week: int

    @field_validator("semester")
    @classmethod
    def semester_validator(cls, v: int) -> int:
        if v < 1 or v > 8:
            raise PydanticCustomError('invalid_semester', 'Semester must be between 1 and 8', {})
        return v

    @field_validator("hours_per_week")
    @classmethod
    def hours_validator(cls, v: int) -> int:
        if v < 1 or v > 12:
            raise PydanticCustomError('invalid_hours', 'Hours per week must be 1-12', {})
        return v


class UpdateSubject(BaseModel):
    name: Optional[str] = None
    semester: Optional[int] = None
    branch: Optional[str] = None
    type: Optional[str] = None
    hours_per_week: Optional[int] = None

    @field_validator("semester")
    @classmethod
    def semester_validator(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 8):
            raise PydanticCustomError('invalid_semester', 'Semester must be between 1 and 8', {})
        return v

    @field_validator("hours_per_week")
    @classmethod
    def hours_validator(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 12):
            raise PydanticCustomError('invalid_hours', 'Hours per week must be 1-12', {})
        return v



