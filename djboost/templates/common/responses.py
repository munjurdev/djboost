from rest_framework.response import Response
from rest_framework import status


def success_response(message="Success", data=None, status_code=status.HTTP_200_OK):
    """Standard success response format."""
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def error_response(message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """Standard error response format."""
    return Response(
        {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
        },
        status=status_code,
    )
