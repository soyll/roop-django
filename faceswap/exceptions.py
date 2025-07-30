from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        error_msg = _flatten_error(exc.detail)
        return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

    if response is not None:
        return Response({'error': str(exc)}, status=response.status_code)

    return Response({'error': 'Internal server error'}, status=500)


def _flatten_error(detail):
    if isinstance(detail, dict):
        for field, messages in detail.items():
            if isinstance(messages, list) and messages:
                return f"{field}: {messages[0]}"
            return f"{field}: {messages}"
    elif isinstance(detail, list) and detail:
        return str(detail[0])
    return "Invalid input"
