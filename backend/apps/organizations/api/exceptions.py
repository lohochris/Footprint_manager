
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def problem_detail_exception_handler(exc, context):
    """Custom exception handler that returns RFC 9457 *Problem Details* JSON.

    The default DRF ``exception_handler`` is used to obtain the standard error
    response. The response payload is then transformed into the Problem Details
    format.
    """
    # Let DRF construct the standard error response first.
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exceptions – treat as 500 Internal Server Error.
        detail = {
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": str(exc),
            "instance": context.get("request").build_absolute_uri() if context.get("request") else "",
        }
        return Response(detail, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Transform DRF's error representation to Problem Details.
    # DRF typically returns a dict of field errors; we join them into a string.
    if isinstance(response.data, dict):
        # When "detail" key exists use that, otherwise concatenate messages.
        if "detail" in response.data:
            title = response.data.get("detail")
        else:
            # Concatenate all error messages for a concise title.
            title = ", ".join(
                [f"{field}: {', '.join(map(str, msgs))}" for field, msgs in response.data.items()]
            )
    else:
        title = str(response.data)

    problem = {
        "type": "about:blank",
        "title": title,
        "status": response.status_code,
        "detail": title,
        "instance": context.get("request").build_absolute_uri() if context.get("request") else "",
    }
    return Response(problem, status=response.status_code)
