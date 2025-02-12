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
from app.dependencies import provide_world_service
from app.forms import WorldForm
from app.services import WorldService


class WorldController(Controller):
    path = "/worlds"
    dependencies = {
        "world_service": Provide(provide_world_service),
    }

    @get("/", name="admin.world.index")
    async def index(self, world_service: WorldService) -> Template:
        worlds = await world_service.list()
        return Template(template_name="admin/worlds/index.html", context={"worlds": worlds})

    @get("/add", name="admin.world.add")
    async def add(self, world_service: WorldService) -> Template:
        return Template(template_name="admin/worlds/add.html", context={"world": None})

    @get("/add/form", name="admin.world.add.form")
    async def add_form(self) -> HTMXTemplate:
        form = WorldForm()
        return HTMXTemplate(template_name="admin/worlds/form.html", context={"form": form})

    @post("/add", name="admin.world.create")
    async def create(
            self,
            request: Request,
            world_service: WorldService,
            data: dict[str, Any] = Body(media_type=RequestEncodingType.URL_ENCODED),
    ) -> HTMXTemplate | ClientRedirect:
        form = WorldForm(formdata=MultiDict(data))
        if form.validate():
            await world_service.create(data=form.data)
            flash(request, _("World has been successfully created!"), category="success")
            path = request.app.route_reverse("admin.world.index")
            return ClientRedirect(path)
        return HTMXTemplate(template_name="admin/worlds/form.html", context={"form": form})

    @get("/{world_id:uuid}", name="admin.world.edit")
    async def edit(self, world_service: WorldService, world_id: UUID) -> Template:
        world = await world_service.get(world_id)
        return Template(template_name="admin/worlds/edit.html", context={"world": world})

    @get("/{world_id:uuid}/form", name="admin.world.edit.form")
    async def edit_form(self, world_service: WorldService, world_id: UUID) -> HTMXTemplate:
        world = await world_service.get(world_id)
        form = WorldForm(data=world.to_dict())
        return HTMXTemplate(template_name="admin/worlds/form.html", context={"world": world, "form": form})

    @post("/{world_id:uuid}", name="admin.world.update")
    async def save(
            self,
            request: Request,
            world_service: WorldService,
            world_id: UUID,
            data: dict[str, Any] = Body(media_type=RequestEncodingType.URL_ENCODED),
    ) -> HTMXTemplate | ClientRefresh:
        world = await world_service.get(world_id)
        form = WorldForm(formdata=MultiDict(data))
        if form.validate():
            await world_service.update(data=form.data, item_id=world.id)
            flash(request, _("World has been successfully updated!"), category="success")
            return ClientRefresh()
        return HTMXTemplate(template_name="admin/worlds/form.html", context={"world": world, "form": form})

    @post("/{world_id:uuid}/delete", name="admin.world.delete")
    async def delete(self, world_service: WorldService, world_id: UUID) -> Response | None:
        world = await world_service.get(world_id)
        if world.lines:
            return Response(content=_("You cannot delete a non-empty world"), status_code=400)
        await world_service.delete(item_id=world_id)
