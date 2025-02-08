from typing import Any

from litestar import Controller, get, post, Request
from litestar.datastructures import MultiDict
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import PermissionDeniedException
from litestar.params import Body
from litestar.response import Template
from litestar_htmx import HTMXTemplate, HTMXRequest, ClientRefresh, ClientRedirect

from app.dependencies import provide_user_service
from app.forms import LoginForm
from app.guards import session_auth
from app.services import UserService


class AuthController(Controller):
    dependencies = {
        "user_service": Provide(provide_user_service),
    }

    @get("/sign-in", name="signin")
    async def index(self) -> Template:
        return Template(template_name="login/index.html")

    @get("/signin/form", name="signin.form")
    async def login_form(self) -> HTMXTemplate:
        form = LoginForm()
        return HTMXTemplate(template_name="login/form.html", context={"form": form})

    @post("/login", name="login")
    async def post_login(
            self,
            request: HTMXRequest,
            user_service: UserService,
            data: dict[str, Any] = Body(media_type=RequestEncodingType.URL_ENCODED),
    ) -> HTMXTemplate | ClientRedirect:
        form = LoginForm(formdata=MultiDict(data))
        if not form.validate():
            return HTMXTemplate(template_name="login/form.html", context={"form": form})
        try:
            user = await user_service.authenticate(
                username=form.username.data,
                password=form.password.data,
            )
            request.set_session({"user_id": user.id})
            path = request.app.route_reverse("admin.index")
            return ClientRedirect(path)
        except PermissionDeniedException as e:
            request.clear_session()
            form.username.errors += (e.detail,)
            return HTMXTemplate(template_name="login/form.html", context={"form": form})

    @post("/logout", name="logout")
    async def logout(self, request: Request) -> ClientRedirect:
        request.cookies.pop(session_auth.session_backend_config.key, None)
        request.clear_session()
        path = request.app.route_reverse("signin")
        return ClientRedirect(path)
