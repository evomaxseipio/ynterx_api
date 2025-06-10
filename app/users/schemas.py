from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr

from app.enums import ErrorCodeEnum


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


###
### Schemas
###


class RolePermissionsSchema(BaseModel):
    pagos: list[str]
    usuarios: list[str]
    prestamos: list[str]
    propiedades: list[str]
    configuracion: list[str]


class RoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: int
    role_description: str
    role_name: str
    permissions: RolePermissionsSchema


class PersonSchema(BaseModel):
    person_id: UUID
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: datetime


class UserPreferencesSchema(BaseModel):
    temp_password: str | None = None
    theme: str | None = None


class UserSchema(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: RoleSchema
    person: PersonSchema
    email_verified: bool = False
    two_factor_enabled: bool = False
    last_login: datetime | None = None
    created_at: datetime
    preferences: UserPreferencesSchema | None = None


class UserListResponse(BaseModel):
    data: list[UserSchema]
    error: ErrorCodeEnum | None = None
    message: str | None = None
    success: bool = False
