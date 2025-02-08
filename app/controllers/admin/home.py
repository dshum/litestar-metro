from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Template

from app.dependencies import provide_line_service, provide_station_service
from app.models import Line
from app.services import LineService


class HomeController(Controller):
    dependencies = {
        "line_service": Provide(provide_line_service),
        "station_service": Provide(provide_station_service),
    }

    @get("/", name="admin.index")
    async def get_index(self, line_service: LineService) -> Template:
        lines = await line_service.list(order_by=[(Line.order, False)])
        return Template(template_name="admin/index.html", context={"lines": lines})
