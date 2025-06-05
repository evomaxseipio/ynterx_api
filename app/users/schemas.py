from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr


class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    language: str | None = Field(default="en", max_length=10)
    user_role_id: int
    is_active: bool = True


class UserCreate(UserBase):
    password: constr(min_length=8)
    person_id: UUID


class UserUpdate(BaseModel):
    username: constr(min_length=3, max_length=50) | None = None
    email: EmailStr | None = None
    language: str | None = None
    is_active: bool | None = None
    user_role_id: int | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    person_id: UUID
    is_active: bool
    email_verified: bool
    two_factor_enabled: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime
