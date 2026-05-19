from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional
import enum
import re


class UserRole(str, enum.Enum):
    owner = "owner"
    client = "client"


# CREATE
class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    role: UserRole

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain a number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain a special character")

        return value


# RESPONSE
class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


# CREATE
class ServiceCreate(BaseModel):
    service: str
    details: str
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)


# RESPONSE
class ServiceResponse(BaseModel):
    id: int
    user_id: int
    service: str
    details: str
    price: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# CREATE
class BookingCreate(BaseModel):
    service_id: int


class BookingResponse(BaseModel):
    id: int
    user_id: int
    service_id: int
    price: Decimal
    payment_status: str
    service: ServiceResponse
    user: UserResponse

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str
