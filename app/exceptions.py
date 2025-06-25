import json
from typing import Annotated, Any
from typing_extensions import Doc

from fastapi import HTTPException, status

from app.enums import ErrorCodeEnum


class DetailedHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class PermissionDenied(DetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


class NotFound(DetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "Not Found"

    def __init__(self, message: str = "Not Found", **kwargs: Any) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class GenericHTTPException(HTTPException):
    """
    Exception for general HTTP errors with custom error codes and messages.
    This exception can be used to provide more specific error handling in the application.
    """

    def __init__(
        self,
        status_code: Annotated[
            int,
            Doc(
                """
                HTTP status code to send to the client.
                """
            ),
        ],
        error_code: Annotated[
            ErrorCodeEnum,
            Doc(
                """
                Custom error code representing the specific error.
                This should be an instance of `ErrorCodeEnum`.
                """
            ),
        ],
        message: Annotated[
            str,
            Doc(
                """
                A human-readable message describing the error.
                This message will be included in the response detail.
                """
            ),
        ],
        success: Annotated[
            bool,
            Doc(
                """
                Indicates whether the operation was successful or not.
                This will typically be `False` for error responses.
                """
            ),
        ] = False,
        **kwargs,
    ) -> None:
        super().__init__(status_code, **kwargs)
        self.error_code = error_code
        self.message = message
        self.success = success
        self.detail = self.to_json()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GenericHTTPException):
            return NotImplemented
        return (
            self.error_code == other.error_code
            and self.message == other.message
            and self.success == other.success
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the exception to a dictionary representation.
        """
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "success": self.success,
        }

    def to_json(self) -> str:
        """
        Convert the exception to a JSON string representation.
        """
        return json.dumps(self.to_dict())


class NotAuthenticated(GenericHTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCodeEnum.UNAUTHORIZED,
            message="Not authenticated",
            success=False,
            headers={"WWW-Authenticate": "Bearer"},
        )


class BadRequest(GenericHTTPException):
    def __init__(self, message: str = "Bad Request", **kwargs: Any) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCodeEnum.UNDEFINED,
            message=message,
            success=False,
            **kwargs,
        )
