from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    """
    Standardised API response wrapper.

    Every endpoint in the project should return through one of these
    class methods so the response envelope is always consistent.

    Success shape:
    {
        "success": true,
        "message": "...",
        "data": { ... },
        "status_code": 200
    }

    Error shape:
    {
        "success": false,
        "message": "...",
        "errors": { ... },
        "status_code": 400
    }
    """

    @classmethod
    def success(cls, data=None, message="Request was successful.", status_code=status.HTTP_200_OK):
        payload = {
            "success": True,
            "message": message,
            "data": data if data is not None else {},
            "status_code": status_code,
        }
        return Response(payload, status=status_code)

    @classmethod
    def created(cls, data=None, message="Resource created successfully."):
        return cls.success(data=data, message=message, status_code=status.HTTP_201_CREATED)

    @classmethod
    def error(cls, message="Something went wrong.", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        payload = {
            "success": False,
            "message": message,
            "errors": errors if errors is not None else {},
            "status_code": status_code,
        }
        return Response(payload, status=status_code)

    @classmethod
    def not_found(cls, message="Resource not found."):
        return cls.error(message=message, status_code=status.HTTP_404_NOT_FOUND)

    @classmethod
    def unauthorized(cls, message="Authentication credentials were not provided or are invalid."):
        return cls.error(message=message, status_code=status.HTTP_401_UNAUTHORIZED)

    @classmethod
    def forbidden(cls, message="You do not have permission to perform this action."):
        return cls.error(message=message, status_code=status.HTTP_403_FORBIDDEN)

    @classmethod
    def no_content(cls, message="Resource deleted successfully."):
        return cls.success(data={}, message=message, status_code=status.HTTP_200_OK)
    
    @classmethod
    def exception(cls, message=None, errors=None, status_code=status.HTTP_417_EXPECTATION_FAILED):
        payload = {
            "success": False,
            "message": message,
            "errors": errors if errors is not None else {},
            "status_code": status_code,
        }
        return Response(payload, status=status_code)