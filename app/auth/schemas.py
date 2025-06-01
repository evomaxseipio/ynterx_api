from typing import Any

from pydantic import BaseModel


class AuthLoginRequest(BaseModel):
    """
    Schema for the login request.
    """

    username: str
    password: str


class AuthLoginResponse(BaseModel):
    """
    Schema for the login response.
    """

    access_token: str
    token_type: str
    user: dict[str, Any]
