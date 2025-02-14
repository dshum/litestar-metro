from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Template

from app.dependencies import provide_world_service
from app.services import WorldService


class HomeController(Controller):
    dependencies = {
        "world_service": Provide(provide_world_service),
    }

    @get("/", name="admin.index")
    async def get_index(self, world_service: WorldService) -> Template:
        worlds = await world_service.list()
        return Template(template_name="admin/index.html", context={"worlds": worlds})
