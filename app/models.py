from typing import List
from uuid import UUID

from advanced_alchemy.base import UUIDBase, UUIDAuditBase
from advanced_alchemy.mixins import UniqueMixin
from sqlalchemy import ForeignKey, String, Table, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates


class Base(UUIDBase):
    ...


stations_materials_table = Table(
    "stations_materials",
    Base.metadata,
    Column("station_id", ForeignKey("stations.id"), primary_key=True),
    Column("material_id", ForeignKey("materials.id"), primary_key=True),
)

stations_transfers_table = Table(
    "stations_transfers",
    Base.metadata,
    Column("station_id", ForeignKey("stations.id"), primary_key=True),
    Column("transfer_id", ForeignKey("stations.id"), primary_key=True),
)


class User(UUIDAuditBase):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)


class World(UUIDAuditBase, UniqueMixin):
    __tablename__ = "worlds"
    name: Mapped[str]
    order: Mapped[int] = mapped_column()
    lines: Mapped[List["Line"]] = relationship(
        back_populates="world",
        lazy="selectin",
        order_by="Line.order",
    )


class Line(UUIDAuditBase, UniqueMixin):
    __tablename__ = "lines"
    name: Mapped[str]
    order: Mapped[int]
    world_id: Mapped[UUID] = mapped_column(ForeignKey("worlds.id"), index=True)
    world: Mapped["World"] = relationship(back_populates="lines", lazy="selectin")
    stations: Mapped[List["Station"]] = relationship(
        back_populates="line",
        lazy="selectin",
        order_by="Station.order",
    )


class Station(UUIDAuditBase, UniqueMixin):
    __tablename__ = "stations"
    name: Mapped[str] = mapped_column(String(255))
    order: Mapped[int]
    line_id: Mapped[UUID] = mapped_column(ForeignKey("lines.id"), index=True)
    line: Mapped["Line"] = relationship(back_populates="stations", lazy="selectin")
    platform_length: Mapped[int | None] = mapped_column(nullable=True)
    platform_square: Mapped[int | None] = mapped_column(nullable=True)
    platform_number: Mapped[int | None] = mapped_column(nullable=True)
    has_depot: Mapped[bool | None] = mapped_column(nullable=True)
    has_elevators: Mapped[bool | None] = mapped_column(nullable=True)
    is_underground: Mapped[bool | None] = mapped_column(nullable=True)
    is_terminal: Mapped[bool | None] = mapped_column(nullable=True)
    entrance_number: Mapped[int | None] = mapped_column(nullable=True)
    materials: Mapped[List["Material"]] = relationship(
        secondary=stations_materials_table,
        lazy="selectin",
        order_by="Material.russian_name",
    )
    screenshots: Mapped[List["Screenshot"]] = relationship(
        back_populates="station",
        lazy="selectin",
        order_by="Screenshot.order",
    )
    transfers: Mapped[List["Station"]] = relationship(
        secondary=stations_transfers_table,
        primaryjoin="Station.id == stations_transfers.c.station_id",
        secondaryjoin="Station.id == stations_transfers.c.transfer_id",
        lazy="noload",
        backref="transfer_from"
    )


class Material(UUIDAuditBase):
    __tablename__ = "materials"
    russian_name: Mapped[str] = mapped_column("russian_name", String(255))

    @validates("russian_name")
    def validate_russian_name(self, key: str, value: str):
        return value.capitalize()


class Screenshot(UUIDAuditBase):
    __tablename__ = "screenshots"
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image: Mapped[str] = mapped_column(String(255))
    order: Mapped[int]
    station_id: Mapped[UUID] = mapped_column(ForeignKey("stations.id"), index=True)
    station: Mapped["Station"] = relationship(back_populates="screenshots", lazy="noload")
