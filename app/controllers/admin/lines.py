from typing import Any
from uuid import UUID

from litestar import Controller, get, post, Request, Response
from litestar.datastructures import MultiDict
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.plugins.flash import flash
from litestar.response import Template
from litestar_htmx import HTMXTemplate, ClientRefresh, ClientRedirect

from app.configs import _
from app.dependencies import provide_line_service, provide_world_service
from app.forms import LineForm
from app.services import LineService, WorldService


class LineController(Controller):
    path = "/lines"
    dependencies = {
        "world_service": Provide(provide_world_service),
        "line_service": Provide(provide_line_service),
    }

    @get("/", name="admin.line.index")
    async def index(self, line_service: LineService) -> Template:
        lines = await line_service.list()
        return Template(template_name="admin/lines/index.html", context={"lines": lines})

    @get("/add", name="admin.line.add")
    async def add(self, line_service: LineService) -> Template:
        return Template(template_name="admin/lines/add.html", context={"line": None})

    @get("/add/form", name="admin.line.add.form")
    async def add_form(self, world_service: WorldService) -> HTMXTemplate:
        form = LineForm()
        worlds = await world_service.list()
        form.world_id.choices = [(world.id, world.name) for world in worlds]
        return HTMXTemplate(template_name="admin/lines/form.html", context={"form": form})

    @post("/add", name="admin.line.create")
    async def create(
            self,
            request: Request,
            world_service: WorldService,
            line_service: LineService,
            data: dict[str, Any] = Body(media_type=RequestEncodingType.URL_ENCODED),
    ) -> HTMXTemplate | ClientRedirect:
        form = LineForm(formdata=MultiDict(data))
        worlds = await world_service.list()
        form.world_id.choices = [(world.id, world.name) for world in worlds]
        if form.validate():
            await line_service.create(data=form.data)
            flash(request, _("Line has been successfully created!"), category="success")
            path = request.app.route_reverse("admin.line.index")
            return ClientRedirect(path)
        return HTMXTemplate(template_name="admin/lines/form.html", context={"form": form})

    @get("/{line_id:uuid}", name="admin.line.edit")
    async def edit(self, line_service: LineService, line_id: UUID) -> Template:
        line = await line_service.get(line_id)
        return Template(template_name="admin/lines/edit.html", context={"line": line})

    @get("/{line_id:uuid}/form", name="admin.line.edit.form")
    async def edit_form(
            self,
            world_service: WorldService,
            line_service: LineService,
            line_id: UUID,
    ) -> HTMXTemplate:
        line = await line_service.get(line_id)
        form = LineForm(data=line.to_dict())
        worlds = await world_service.list()
        form.world_id.choices = [(world.id, world.name) for world in worlds]
        return HTMXTemplate(template_name="admin/lines/form.html", context={"line": line, "form": form})

    @post("/{line_id:uuid}", name="admin.line.update")
    async def save(
            self,
            request: Request,
            world_service: WorldService,
            line_service: LineService,
            line_id: UUID,
            data: dict[str, Any] = Body(media_type=RequestEncodingType.URL_ENCODED),
    ) -> HTMXTemplate | ClientRefresh:
        line = await line_service.get(line_id)
        form = LineForm(formdata=MultiDict(data))
        worlds = await world_service.list()
        form.world_id.choices = [(world.id, world.name) for world in worlds]
        if form.validate():
            await line_service.update(data=form.data, item_id=line.id)
            flash(request, _("Line has been successfully updated!"), category="success")
            return ClientRefresh()
        return HTMXTemplate(template_name="admin/lines/form.html", context={"line": line, "form": form})

    @post("/{line_id:uuid}/delete", name="admin.line.delete")
    async def delete(self, line_service: LineService, line_id: UUID) -> Response | None:
        line = await line_service.get(line_id)
        if line.stations:
            return Response(content=_("You cannot delete a non-empty line"), status_code=400)
        await line_service.delete(item_id=line_id)
