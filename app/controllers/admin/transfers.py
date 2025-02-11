from typing import Any
from uuid import UUID

from litestar import Controller, get, post, Request
from litestar.datastructures import MultiDict
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.plugins.flash import flash
from litestar.response import Template
from litestar_htmx import HTMXTemplate, ClientRefresh

from app.configs import logging_config, _
from app.dependencies import provide_station_service
from app.forms import StationTransfersForm
from app.models import Station
from app.services import StationService

logger = logging_config.configure()()


class StationTransfersController(Controller):
    path = "/stations"
    dependencies = {
        "station_service": Provide(provide_station_service),
    }

    @get("/{station_id:uuid}/transfers", name="admin.station.transfers.edit")
    async def edit(self, station_service: StationService, station_id: UUID) -> Template:
        station = await station_service.get(station_id)
        return Template(template_name="admin/stations/transfers/edit.html", context={"station": station})

    @get("/{station_id:uuid}/transfers/form", name="admin.station.transfers.edit.form")
    async def edit_transfers_form(
            self,
            station_service: StationService,
            station_id: UUID,
    ) -> HTMXTemplate:
        station = await station_service.get(station_id, load=[Station.transfers])
        form = StationTransfersForm(
            data=station.to_dict(),
            transfers=[transfer.id for transfer in station.transfers],
        )
        transfer_stations = await station_service.list(Station.id != station.id)
        form.transfers.choices = [(transfer_station.id, transfer_station.name)
                                  for transfer_station in transfer_stations]
        return HTMXTemplate(template_name="admin/stations/transfers/form.html",
                            context={"station": station, "form": form})

    @post("/{station_id:uuid}/transfers", name="admin.station.transfers.update")
    async def save(
            self,
            request: Request,
            station_service: StationService,
            station_id: UUID,
            data: dict[str, Any] = Body(media_type=RequestEncodingType.URL_ENCODED),
    ) -> HTMXTemplate | ClientRefresh:
        station = await station_service.get(station_id, load=[Station.transfers])
        if not data.get("transfers"):
            data.update({"transfers": []})
        form = StationTransfersForm(formdata=MultiDict(data))
        transfers = await station_service.list(Station.id != station.id)
        form.transfers.choices = [(transfer.id, transfer.name) for transfer in transfers]
        if form.validate():
            await station_service.update(data=form.data, item_id=station.id)
            flash(request, _("Transfers have been successfully updated!"), category="success")
            return ClientRefresh()
        return HTMXTemplate(template_name="admin/stations/transfers/form.html",
                            context={"station": station, "form": form})
