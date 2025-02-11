from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository, ModelT
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, is_dict_with_field, ModelDictT, is_dict
from litestar.exceptions import PermissionDeniedException
from sqlalchemy import func, select

from app.configs import _
from app.lib import crypt
from app.models import Line, Station, User, World, Material, Screenshot


class OrderableService(SQLAlchemyAsyncRepositoryService[ModelT]):
    async def _get_next_order(self):
        model = self.repository.model_type
        max_order = await self.repository.session.scalar(select(func.max(model.order)))
        return max_order + 1 if max_order is not None else 0

    async def _populate_order(self, data: ModelDictT[ModelT]) -> ModelDictT[ModelT]:
        if is_dict(data):
            data = await self.to_model(data)
        if not data.order:
            data.order = await self._get_next_order()
        return data

    async def to_model_on_create(self, data: ModelDictT[ModelT]) -> ModelDictT[ModelT]:
        return await self._populate_order(data)

    async def to_model_on_update(self, data: ModelDictT[ModelT]) -> ModelDictT[ModelT]:
        return await self._populate_order(data)


class UserService(SQLAlchemyAsyncRepositoryService[User]):
    class UserRepository(SQLAlchemyAsyncRepository[User]):
        model_type = User

    repository_type = UserRepository

    async def authenticate(self, username: str, password: bytes | str) -> User:
        user = await self.get_one_or_none(username=username)
        if user is None:
            raise PermissionDeniedException(detail=_("Incorrect username or password"))
        if not await crypt.verify_password(password, user.hashed_password):
            raise PermissionDeniedException(detail=_("Incorrect username or password"))
        if not user.is_active:
            raise PermissionDeniedException(detail=_("User is inactive"))
        return user

    async def to_model(self, data: ModelDictT[User], operation: str | None = None) -> User:
        if is_dict_with_field(data, "password"):
            password: bytes | str | None = data.pop("password", None)
            if password is not None:
                data.update({"hashed_password": await crypt.get_password_hash(password)})
        return await super().to_model(data, operation)


class WorldService(OrderableService[World]):
    class WorldRepository(SQLAlchemyAsyncRepository[World]):
        model_type = World

    repository_type = WorldRepository


class LineService(OrderableService[Line]):
    class LineRepository(SQLAlchemyAsyncRepository[Line]):
        model_type = Line

    repository_type = LineRepository


class StationService(OrderableService[Station]):
    class StationRepository(SQLAlchemyAsyncRepository[Station]):
        uniquify = True
        model_type = Station

    repository_type = StationRepository

    async def to_model_on_create(self, data: ModelDictT[Station]) -> ModelDictT[Station]:
        data = await self._add_relations_to_station(data)
        return await super().to_model_on_update(data)

    async def to_model_on_update(self, data: ModelDictT[Station]) -> ModelDictT[Station]:
        data = await self._add_relations_to_station(data)
        return await super().to_model_on_update(data)

    async def _add_relations_to_station(self, data: ModelDictT[Station]) -> ModelDictT[Station]:
        if is_dict(data):
            materials: list[str] | None = data.pop("materials", None)
            transfers: list[str] | None = data.pop("transfers", None)
            data = await self.to_model(data)
            if materials is not None:
                data.materials = []
                for material in materials:
                    data.materials.append(Material(russian_name=material))
            if transfers is not None:
                data.transfers = []
                for transfer_id in transfers:
                    data.transfers.append(Station(id=UUID(transfer_id)))
        return data


class ScreenshotService(OrderableService[Screenshot]):
    class ScreenshotRepository(SQLAlchemyAsyncRepository[Screenshot]):
        model_type = Screenshot

    repository_type = ScreenshotRepository
