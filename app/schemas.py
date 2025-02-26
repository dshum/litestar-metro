from typing import Any

import msgspec


class BaseStruct(msgspec.Struct):
    def to_dict(self) -> dict[str, Any]:
        return {f: getattr(self, f) for f in self.__struct_fields__ if getattr(self, f, None) != msgspec.UNSET}


class CamelizedBaseStruct(BaseStruct, rename="camel"):
    """Camelized Base Struct"""


class UserCreate(CamelizedBaseStruct):
    username: str
    password: str
    first_name: str
    last_name: str
    is_active: bool = True
