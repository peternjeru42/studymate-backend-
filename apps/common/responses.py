from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone


def api_response(data=None, message=None, error=None, status_code=status.HTTP_200_OK):
    return Response(
        {
            "data": data,
            "message": message,
            "error": error,
            "timestamp": timezone.now(),
        },
        status=status_code,
    )
