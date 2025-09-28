from typing import Optional
from pydantic import BaseModel, SecretStr, field_validator, EmailStr
from pydantic_core import PydanticCustomError
import re


class TeacherBase(BaseModel):
    @classmethod
    def validate_password_logic(cls, password: str) -> None:
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

    @classmethod
    def validate_email_format(cls, email: EmailStr):
        if not email.endswith("@gmail.com"):
            raise PydanticCustomError(
                'invalid_email_domain',
                'Email must be from @gmail.com domain',
                {}
            )


class CreateTeacher(TeacherBase):
    email: EmailStr
    institute_id: str
    teacher_id: str
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


class UpdateTeacher(TeacherBase):
    email: Optional[EmailStr] = None
    institute_id: Optional[str] = None
    teacher_id: Optional[str] = None
    password: Optional[SecretStr] = None

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


class LoginTeacher(TeacherBase):
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


class ChangePasswordRequest(TeacherBase):
    old_password: SecretStr
    new_password: SecretStr



