from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.enums import ErrorCodeEnum


@dataclass
class UserRole:
    """
    Represents a user role in the system.
    """

    role_name: str
    permissions: list[str]  # List of permissions associated with the role
    user_role_id: int | None = None  # Optional ID for the role, if applicable
    role_description: str | None = None  # Optional description of the role


@dataclass
class User:
    """
    Represents a user in the system.
    """

    user_id: str  # Unique identifier for the user, this is usually a UUID
    person_id: str  # Unique identifier for the person, this is usually a UUID
    username: str
    email: str
    role: UserRole
    language: str | None = None
    is_active: bool = True
    last_login: str | None = None  # ISO 8601 format for last login time
    preferences: dict[str, str] | None = None  # User preferences as key-value pairs
    email_verified: bool = False
    two_factor_enabled: bool = False

    def __post_init__(self):
        if not self.user_id:
            raise ValueError("user_id must be provided")
        if not self.person_id:
            raise ValueError("person_id must be provided")
        if not self.username:
            raise ValueError("username must be provided")
        if not self.email:
            raise ValueError("email must be provided")
        if not isinstance(self.role, UserRole):
            raise TypeError("role must be an instance of UserRole")

    @classmethod
    def from_dict(cls, data: dict) -> User:
        """
        Create a User instance from a dictionary.
        """
        role_data = data.get("role", {})
        role = UserRole(
            role_name=role_data.get("role_name", ""),
            permissions=role_data.get("permissions", []),
            user_role_id=role_data.get("user_role_id"),
            role_description=role_data.get("role_description"),
        )
        return cls(
            user_id=data["user_id"],
            person_id=data["person_id"],
            username=data["username"],
            email=data["email"],
            role=role,
            language=data.get("language"),
            is_active=data.get("is_active", True),
            last_login=data.get("last_login"),
            preferences=data.get("preferences", {}),
            email_verified=data.get("email_verified", False),
            two_factor_enabled=data.get("two_factor_enabled", False),
        )


@dataclass
class Session:
    """
    Represents a user session.
    """

    expires_at: str  # ISO 8601 format
    session_token: str

    @classmethod
    def from_dict(cls, data: dict) -> Session:
        """
        Create a Session instance from a dictionary.
        """
        return cls(
            expires_at=data["expires_at"],
            session_token=data["session_token"],
        )


@dataclass
class LoginUserQueryResult:
    """
    Represents a SQL query for user login.
    """

    message: str
    success: bool
    error_code: ErrorCodeEnum
    user: dict[str, Any]
    session: Session | None = None
    api_config: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict) -> LoginUserQueryResult:
        """
        Create a LoginUserQueryResult instance from a dictionary.
        """
        user_data = data.get("user", {})
        session_data = data.get("session")
        api_config_data = data.get("api_config")
        # user = User.from_dict(user_data) if user_data else None
        session = Session.from_dict(session_data) if session_data else None
        return cls(
            message=data.get("message", ""),
            success=data.get("success", False),
            user=user_data,
            session=session,
            api_config=api_config_data,
            error_code=(
                ErrorCodeEnum(data["error_code"])
                if "error_code" in data
                else ErrorCodeEnum.UNDEFINED
            ),
        )

    @classmethod
    def from_json(cls, json_data: str) -> LoginUserQueryResult:
        """
        Create a LoginUserQueryResult instance from a JSON string.
        """
        data = json.loads(json_data)
        return cls.from_dict(data)

    def get_user(self) -> User | None:
        """
        Get the User instance from the query result.
        """
        if self.user:
            return User.from_dict(self.user)
        return None
