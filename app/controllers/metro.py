from uuid import UUID

from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Template

from app.dependencies import (
    provide_line_service,
    provide_station_service,
    provide_world_service,
)
from app.models import Station
from app.services import StationService, WorldService


class MetroController(Controller):
    dependencies = {
        "world_service": Provide(provide_world_service),
        "line_service": Provide(provide_line_service),
        "station_service": Provide(provide_station_service),
    }

    @get("/", name="index")
    async def get_index(self, world_service: WorldService) -> Template:
        worlds = await world_service.list()
        return Template(template_name="index.html", context={"worlds": worlds})

    @get("/stations", name="stations")
    async def get_stations(self, station_service: StationService) -> Template:
        stations = await station_service.list()
        return Template(template_name="stations.html", context={"stations": stations})

    @get("/stations/{station_id:uuid}", name="station")
    async def get_station(
            self,
            station_service: StationService,
            station_id: UUID,
    ) -> Template:
        station = await station_service.get(station_id, load=[Station.transfers])
        extras = [extra for extra in ["has_depot", "is_underground", "has_elevators", "is_terminal"]
                  if getattr(station, extra) is True]
        return Template(template_name="station.html", context={
            "station": station,
            "line": station.line,
            "materials": station.materials,
            "screenshots": station.screenshots,
            "transfers": station.transfers,
            "extras": extras,
        })
