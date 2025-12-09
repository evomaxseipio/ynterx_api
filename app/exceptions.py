import json
from typing import Annotated, Any
from typing_extensions import Doc

from fastapi import HTTPException, status

from app.enums import ErrorCodeEnum


class DetailedHTTPException(HTTPException):
    """
    Base exception class for HTTP errors with predefined status codes and details.
    Used as a foundation for specific exception types.
    """
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class PermissionDenied(DetailedHTTPException):
    """
    Exception raised when a user does not have permission to access a resource.
    Returns HTTP 403 Forbidden status code.
    """
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


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
        # Extract custom detail from kwargs if provided (e.g., missing_fields, errors)
        # Keep it as a dict so the exception handler can use it directly
        custom_detail = kwargs.pop("detail", None)
        super().__init__(status_code, **kwargs)
        self.error_code = error_code
        self.message = message
        self.success = success
        # If detail is a dict, keep it as dict for direct access; otherwise convert to JSON string
        if isinstance(custom_detail, dict):
            self.detail = custom_detail
        else:
            self.detail = self.to_json()

    def __eq__(self, other: object) -> bool:
        """
        Compare two GenericHTTPException instances for equality.
        Two exceptions are equal if they have the same error_code, message, and success status.
        """
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
        
        Returns:
            dict: Dictionary containing error_code, message, success, and any additional
                  fields from self.detail (e.g., missing_fields, errors).
        """
        result = {
            "error_code": self.error_code.value,
            "message": self.message,
            "success": self.success,
        }
        # If detail is a dict, include all its fields in the result
        # This includes additional fields like missing_fields, errors, etc.
        if isinstance(self.detail, dict):
            # Include all fields from detail, especially missing_fields for validation errors
            for key, value in self.detail.items():
                result[key] = value
        return result

    def to_json(self) -> str:
        """
        Convert the exception to a JSON string representation.
        
        Returns:
            str: JSON string representation of the exception dictionary.
        """
        return json.dumps(self.to_dict())


class NotAuthenticated(GenericHTTPException):
    """
    Exception raised when a user is not authenticated.
    Returns HTTP 401 Unauthorized status code with WWW-Authenticate header.
    """
    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCodeEnum.UNAUTHORIZED,
            message=message,
            success=False,
            headers={"WWW-Authenticate": "Bearer"},
        )


class BadRequest(GenericHTTPException):
    """
    Exception raised for bad request errors.
    Returns HTTP 400 Bad Request status code.
    """
    def __init__(self, message: str = "Bad Request", **kwargs: Any) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCodeEnum.UNDEFINED,
            message=message,
            success=False,
            **kwargs,
        )


class NotFound(GenericHTTPException):
    """
    Exception raised when a requested resource is not found.
    Returns HTTP 404 Not Found status code.
    """
    def __init__(self, message: str = "Not Found", **kwargs: Any) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCodeEnum.NOT_FOUND,
            message=message,
            success=False,
            **kwargs,
        )


class ContractNotFound(GenericHTTPException):
    """
    Exception raised when a requested contract is not found.
    Returns HTTP 404 Not Found status code with CONTRACT_NOT_FOUND error code.
    """
    def __init__(self, message: str = "Contract not found", **kwargs: Any) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCodeEnum.CONTRACT_NOT_FOUND,
            message=message,
            success=False,
            **kwargs,
        )


class ContractInactive(GenericHTTPException):
    """
    Exception raised when attempting to perform an operation on an inactive contract.
    Returns HTTP 400 Bad Request status code with CONTRACT_INACTIVE error code.
    """
    def __init__(self, message: str = "Contract is inactive", **kwargs: Any) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCodeEnum.CONTRACT_INACTIVE,
            message=message,
            success=False,
            **kwargs,
        )


class InvalidAmount(GenericHTTPException):
    """
    Exception raised when an invalid amount is provided.
    Returns HTTP 400 Bad Request status code with INVALID_AMOUNT error code.
    """
    def __init__(self, message: str = "Invalid amount", **kwargs: Any) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCodeEnum.INVALID_AMOUNT,
            message=message,
            success=False,
            **kwargs,
        )
