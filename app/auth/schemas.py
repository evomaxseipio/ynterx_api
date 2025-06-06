from typing import Any

from pydantic import BaseModel

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
