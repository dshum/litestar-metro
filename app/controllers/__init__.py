from litestar import Router

from app.controllers.auth import AuthController
from app.controllers.metro import MetroController

app_router = Router(
    route_handlers=[AuthController, MetroController],
    path="/",
)
