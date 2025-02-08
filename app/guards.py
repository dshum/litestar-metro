from typing import Any

from litestar import Request
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AuthenticationResult
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.security.session_auth import SessionAuth, SessionAuthMiddleware
from litestar.types import Empty

from app.configs import sqlalchemy_config
from app.models import User
from app.services import UserService


class AppSessionAuthMiddleware(SessionAuthMiddleware):
    async def authenticate_request(self, connection: ASGIConnection[Any, Any, Any, Any]) -> AuthenticationResult:
        """Auth middleware that doesn't raise AuthenticationError."""
        if not connection.session or connection.scope["session"] is Empty:
            connection.scope["session"] = Empty
            return self.access_denied_result(connection)
        user = await self.retrieve_user_handler(connection.session, connection)
        if not user:
            connection.scope["session"] = Empty
            return self.access_denied_result(connection)
        return AuthenticationResult(user=user, auth=connection.session)

    @classmethod
    def access_denied_result(cls, connection: ASGIConnection[Any, Any, Any, Any]):
        if connection.scope["path"].startswith("/admin"):
            raise NotAuthorizedException("Access denied")
        return AuthenticationResult(user=None, auth=connection.session)


async def retrieve_user_handler(
        session: dict[str, Any],
        connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    db_session = sqlalchemy_config.provide_session(connection.app.state, connection.scope)
    user_service = UserService(session=db_session)
    user = await user_service.get_one_or_none(id=session.get("user_id"))
    return user if user and user.is_active else None


session_auth = SessionAuth(
    retrieve_user_handler=retrieve_user_handler,
    session_backend_config=ServerSideSessionConfig(
        key="metro_session",

    ),
    authentication_middleware_class=AppSessionAuthMiddleware,
)
