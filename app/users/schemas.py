from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr

from app.person.schemas import PersonSchema
from app.schemas import CustomSchema


class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    language: str | None = Field(default="en", max_length=10)
    user_role_id: int
    is_active: bool = True


###
### Schemas
###


class RolePermissionsSchema(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    # Esquema completamente adaptable para cualquier estructura de permisos
    # Permite campos adicionales automáticamente sin necesidad de modificar el código


class RoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_role_id: int
    role_name: str
    role_description: str
    permissions: RolePermissionsSchema


# class PersonSchema(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     person_id: UUID
#     first_name: str
#     last_name: str
#     middle_name: str
#     date_of_birth: datetime


class UserPreferencesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class UserRead(CustomSchema):
    data: UserSchema


class UserListResponse(CustomSchema):
    data: list[UserSchema]


###


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    language: str | None = Field(default="en", max_length=10)
    user_role_id: int
    new_password: constr(min_length=8)
    person_id: UUID
    preferences: UserPreferencesSchema | None = None


class UserUpdate(BaseModel):
    username: constr(min_length=3, max_length=50) | None = None
    email: EmailStr | None = None
    language: str | None = None
    is_active: bool | None = None
    user_role_id: int | None = None
    preferences: UserPreferencesSchema | None = None
    # Nuevo campo para contraseña (solo para administradores)
    new_password: constr(min_length=8) | None = None
