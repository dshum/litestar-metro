import anyio
import click
from sqlalchemy import delete

from app.configs import sqlalchemy_config
from app.models import Line, Material, Station, World
from app.services import LineService, StationService, WorldService


@click.group(name="metro", help="Manage metro data.")
def metro_group() -> None:
    ...


@metro_group.command(name="flush", help="Flush all data")
def flush_data() -> None:
    async def _flush_data():
        async with sqlalchemy_config.get_session() as db_session:
            await db_session.execute(delete(World))
            await db_session.execute(delete(Line))
            await db_session.execute(delete(Station))
            await db_session.commit()
            click.echo(f"Deleted all data")

    anyio.run(_flush_data)


@metro_group.command(name="create", help="Create lines and stations")
def create_data() -> None:
    async def _create_data() -> None:
        worlds = [
            World(name="Бермудово", order=0),
        ]

        async with sqlalchemy_config.get_session() as db_session:
            world_service = WorldService(db_session)
            worlds = await world_service.create_many(data=worlds, auto_commit=True)
            click.echo(f"Worlds created")

        lines = [
            Line(name="Подсолнуховая", order=0, world=worlds[0]),
            Line(name="Пунцевская", order=1, world=worlds[0]),
        ]

        async with sqlalchemy_config.get_session() as db_session:
            line_service = LineService(db_session)
            lines = await line_service.create_many(data=lines, auto_commit=True)
            click.echo(f"Lines created")

        stations = [
            Station(
                name="Бледная",
                order=0,
                line=lines[0],
                platform_length=31,
                platform_square=186,
                platform_number=2,
                has_depot=True,
                has_elevators=True,
                is_underground=True,
                is_terminal=True,
                entrance_number=2,
                materials=[
                    Material(russian_name="Ступеньки из глубинносланцевого плитняка"),
                    Material(russian_name="Глубинносланцевый плитняк"),
                    Material(russian_name="Красное стекло"),
                    Material(russian_name="Березовая дверь"),
                    Material(russian_name="Бревно бледного дуба"),
                    Material(russian_name="Обтесанное бревно бледного дуба"),
                    Material(russian_name="Светокамень"),
                    Material(russian_name="Вода"),
                    Material(russian_name="Энергорельсы"),
                    Material(russian_name="Рельсы"),
                ],
            ),
        ]

        async with sqlalchemy_config.get_session() as db_session:
            station_service = StationService(db_session)
            await station_service.create_many(data=stations, auto_commit=True)
            click.echo(f"Stations created")

    anyio.run(_create_data)
