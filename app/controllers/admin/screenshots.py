from dataclasses import dataclass
from io import BytesIO
from typing import Annotated
from uuid import UUID, uuid4

import anyio
from PIL import Image
from anyio import Path
from litestar import Controller, get, post
from litestar.datastructures import MultiDict, UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.plugins.flash import flash
from litestar.response import Template
from litestar_htmx import HTMXTemplate, HTMXRequest, ClientRefresh
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs import logging_config, screenshots_path
from app.dependencies import provide_station_service, provide_screenshot_service
from app.forms import StationScreenshotForm, FileValidationException
from app.services import StationService, ScreenshotService

logger = logging_config.configure()()


@dataclass
class FormData:
    image: UploadFile
    title: str | None
    order: int | None


class StationScreenshotsController(Controller):
    path = "/stations"
    dependencies = {
        "station_service": Provide(provide_station_service),
        "screenshot_service": Provide(provide_screenshot_service),
    }

    @get("/{station_id:uuid}/screenshots", name="admin.station.screenshots.index")
    async def index(
            self,
            db_session: AsyncSession,
            station_service: StationService,
            station_id: UUID,
    ) -> Template:
        station = await station_service.get(station_id)
        return Template(template_name="admin/stations/screenshots/index.html", context={
            "station": station,
            "screenshots": station.screenshots,
        })

    @get("/{station_id:uuid}/screenshots/form", name="admin.station.screenshots.add.form")
    async def add_form(
            self,
            station_service: StationService,
            station_id: UUID,
    ) -> HTMXTemplate:
        station = await station_service.get(station_id)
        form = StationScreenshotForm()
        return HTMXTemplate(template_name="admin/stations/screenshots/form.html",
                            context={"station": station, "form": form})

    @post("/{station_id:uuid}/screenshots", name="admin.station.screenshots.create")
    async def create(
            self,
            request: HTMXRequest,
            station_service: StationService,
            screenshot_service: ScreenshotService,
            station_id: UUID,
            data: Annotated[FormData, Body(media_type=RequestEncodingType.MULTI_PART)],
    ) -> ClientRefresh | HTMXTemplate:
        station = await station_service.get(station_id)
        form = StationScreenshotForm(formdata=MultiDict({
            "image": data.image,
            "title": data.title,
            "order": data.order or "",
        }))
        if form.validate():
            try:
                filename = await self.upload_file(data.image)
                screenshot_data = form.data
                screenshot_data.update(image=filename)
                screenshot_data.update(station_id=station_id)
                await screenshot_service.create(data=screenshot_data)
                flash(request, "Screenshot has been successfully uploaded!", category="success")
                return ClientRefresh()
            except FileValidationException as e:
                form.image.errors.append(e.message)
        return HTMXTemplate(template_name="admin/stations/screenshots/form.html",
                            context={"station": station, "form": form})

    @post("/{screenshot_id:uuid}/screenshots/delete", name="admin.screenshot.delete")
    async def delete(self, screenshot_service: ScreenshotService, screenshot_id: UUID) -> None:
        screenshot = await screenshot_service.get(screenshot_id)
        await self.delete_file(screenshot.image)
        await screenshot_service.delete(item_id=screenshot_id)

    @staticmethod
    async def upload_file(file: UploadFile) -> str:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise FileValidationException(message="Allowed files extensions: jpg, png")
        content = await file.read()
        if len(content) > 4 * 1024 * 1024:
            raise FileValidationException(message="Maximum file size: 4Mb")
        filename_base = "screenshot"
        postfix = str(uuid4())
        extension = file.filename.rsplit(".", 1)[-1]
        filename = f"{filename_base}-{postfix}.{extension}"
        filepath = screenshots_path / filename
        image = Image.open(BytesIO(content))
        image.thumbnail(size=(800, 600))
        buf = BytesIO()
        image.save(buf, format=extension)
        async with await anyio.open_file(anyio.Path(filepath), "wb") as f:
            await f.write(buf.getbuffer())
        return filename

    @staticmethod
    async def delete_file(filename: str):
        filepath = Path(screenshots_path / filename)
        if await filepath.exists():
            await filepath.unlink()
