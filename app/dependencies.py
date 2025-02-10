from advanced_alchemy.filters import LimitOffset
from litestar.params import Parameter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Line, Station, World, Screenshot
from app.services import LineService, StationService, UserService, WorldService, ScreenshotService


async def provide_limit_offset_pagination(
        offset: int = Parameter(query="offset", ge=0, default=0, required=False),
        limit: int = Parameter(query="limit", ge=1, le=100, default=10, required=False),
) -> LimitOffset:
    return LimitOffset(limit, offset)


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)


async def provide_world_service(db_session: AsyncSession) -> WorldService:
    statement = select(World).order_by(World.order)
    return WorldService(session=db_session, statement=statement)


async def provide_line_service(db_session: AsyncSession) -> LineService:
    statement = select(Line).order_by(Line.name)
    return LineService(session=db_session)


async def provide_station_service(db_session: AsyncSession) -> StationService:
    statement = select(Station).order_by(Station.name)
    return StationService(session=db_session)


async def provide_screenshot_service(db_session: AsyncSession) -> ScreenshotService:
    statement = select(Screenshot).order_by(Screenshot.order)
    return ScreenshotService(session=db_session)
