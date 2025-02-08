from litestar import Router

from app.controllers.admin.home import HomeController
from app.controllers.admin.lines import LineController
from app.controllers.admin.screenshots import StationScreenshotsController
from app.controllers.admin.stations import StationController
from app.controllers.admin.transfers import StationTransfersController
from app.controllers.admin.worlds import WorldController

admin_router = Router(
    route_handlers=[
        HomeController,
        WorldController,
        LineController,
        StationController,
        StationTransfersController,
        StationScreenshotsController,
    ],
    path="/admin",
)
