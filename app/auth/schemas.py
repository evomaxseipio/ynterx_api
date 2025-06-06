from typing import Any

from pydantic import BaseModel, model_validator

from app.schemas import CustomSchema


class AuthLoginRequest(BaseModel):
    """
    Schema for the login request.
    """

    username: str
    password: str


class _AuthLoginDataResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Any


class AuthLoginResponse(CustomSchema):
    """
    Schema for the login response.
    """

    data: _AuthLoginDataResponse


class PasswordRecoveryRequest(BaseModel):
    """
    Schema for the password recovery request.
    """

    email: str


class PasswordChangeRequest(BaseModel):
    """
    Schema for the password change request.
    """

    current_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode='after')
    def check_password_match(self) -> 'PasswordChangeRequest':
        if self.new_password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self
