from litestar import Response, MediaType
from litestar.exceptions import (
    HTTPException,
    NotAuthorizedException,
    NotFoundException,
    ValidationException,
)
from litestar.response import Template
from litestar_htmx import HTMXRequest

from app.configs import _


def base_exception_handler(request: HTMXRequest, exc: Exception) -> Template:
    return error_response(request, exc, 500)


def http_exception_handler(request: HTMXRequest, exc: HTTPException) -> Template:
    return error_response(request, exc, 500)


def not_found_exception_handler(request: HTMXRequest, exc: NotFoundException) -> Template:
    return error_response(request, exc, 404)


def not_authorized_exception_handler(request: HTMXRequest, exc: NotAuthorizedException) -> Template:
    return error_response(request, exc, 403)


def validation_exception_handler(request: HTMXRequest, exc: ValidationException) -> Template:
    return error_response(request, exc, 400)


def error_response(request: HTMXRequest, exc: Exception, code: int):
    match code:
        case 400:
            message = _("Bad request")
        case 403:
            message = _("Access denied")
        case 404:
            message = _("Page not found")
        case _:
            message = exc.detail if hasattr(exc, "detail") else _("Internal server error")

    if request.htmx:
        return Response(content=message, status_code=code, media_type=MediaType.TEXT)

    return Template(
        template_name="error.html",
        context={"message": message, "code": code},
        status_code=400,
    )
