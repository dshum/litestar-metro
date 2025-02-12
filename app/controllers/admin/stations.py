from typing import Any
from uuid import UUID

from litestar import Controller, get, post, Request
from litestar.datastructures import MultiDict
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.plugins.flash import flash
from litestar.response import Template
from litestar_htmx import HTMXTemplate, ClientRefresh, ClientRedirect

from app.configs import logging_config, _
from app.dependencies import provide_station_service, provide_world_service
from app.forms import StationForm
from app.models import Station
from app.services import StationService, WorldService

logger = logging_config.configure()()


class StationController(Controller):
    path = "/stations"
    dependencies = {
        "world_service": Provide(provide_world_service),
        "station_service": Provide(provide_station_service),
    }

    @get("/", name="admin.station.index")
    async def index(self, station_service: StationService) -> Template:
        stations = await station_service.list(load=[Station.transfers])
        return Template(template_name="admin/stations/index.html", context={"stations": stations})

    @get("/{station_id:uuid}", name="admin.station.view")
    async def view(
            self,
            station_service: StationService,
            station_id: UUID,
    ) -> Template:
        station = await station_service.get(station_id, load=[Station.transfers])
        extras = [extra for extra in ["has_depot", "is_underground", "has_elevators", "is_terminal"]
                  if getattr(station, extra) is True]
        return Template(template_name="admin/stations/view.html", context={
            "station": station,
            "line": station.line,
            "materials": station.materials,
            "screenshots": station.screenshots,
            "transfers": station.transfers,
            "extras": extras,
        })

    @get("/add", name="admin.station.add")
    async def add(self, station_service: StationService) -> Template:
        return Template(template_name="admin/stations/add.html", context={"station": None})

    @get("/add/form", name="admin.station.add.form")
    async def add_form(self, world_service: WorldService, ) -> HTMXTemplate:
        form = StationForm()
        worlds = await world_service.list()
        form.line_id.choices = {world.name: [(line.id, line.name) for line in world.lines] for world in worlds}
        return HTMXTemplate(template_name="admin/stations/form.html", context={"form": form})

    @post("/add", name="admin.station.create")
    async def create(
            self,
            request: Request,
            world_service: WorldService,
            station_service: StationService,
            data: dict[str, Any] = Body(media_type=RequestEncodingType.URL_ENCODED),
    ) -> HTMXTemplate | ClientRedirect:
        form = StationForm(formdata=MultiDict(data))
        worlds = await world_service.list()
        form.line_id.choices = {world.name: [(line.id, line.name) for line in world.lines] for world in worlds}
        if form.validate():
            await station_service.create(data=form.data)
            flash(request, _("Station has been successfully created!"), category="success")
            path = request.app.route_reverse("admin.station.index")
            return ClientRedirect(path)
        return HTMXTemplate(template_name="admin/stations/form.html", context={"form": form})

    @get("/{station_id:uuid}/edit", name="admin.station.edit")
    async def edit(self, station_service: StationService, station_id: UUID) -> Template:
        station = await station_service.get(station_id)
        return Template(template_name="admin/stations/edit.html", context={"station": station})

    @get("/{station_id:uuid}/form", name="admin.station.edit.form")
    async def edit_form(
            self,
            world_service: WorldService,
            station_service: StationService,
            station_id: UUID,
    ) -> HTMXTemplate:
        station = await station_service.get(station_id)
        form = StationForm(
            data=station.to_dict(),
            materials=[material.russian_name for material in station.materials],
        )
        worlds = await world_service.list()
        form.line_id.choices = {world.name: [(line.id, line.name) for line in world.lines] for world in worlds}
        return HTMXTemplate(template_name="admin/stations/form.html", context={"station": station, "form": form})

    @post("/{station_id:uuid}", name="admin.station.update")
    async def save(
            self,
            request: Request,
            world_service: WorldService,
            station_service: StationService,
            station_id: UUID,
            data: dict[str, Any] = Body(media_type=RequestEncodingType.URL_ENCODED),
    ) -> HTMXTemplate | ClientRefresh:
        station = await station_service.get(station_id)
        form = StationForm(formdata=MultiDict(data))
        worlds = await world_service.list()
        form.line_id.choices = {world.name: [(line.id, line.name) for line in world.lines] for world in worlds}
        if form.validate():
            await station_service.update(data=form.data, item_id=station.id)
            flash(request, _("Station has been successfully updated!"), category="success")
            return ClientRefresh()
        return HTMXTemplate(template_name="admin/stations/form.html", context={"station": station, "form": form})

    @post("/{station_id:uuid}/delete", name="admin.station.delete")
    async def delete(self, station_service: StationService, station_id: UUID) -> None:
        await station_service.delete(item_id=station_id)
