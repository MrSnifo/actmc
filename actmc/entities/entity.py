
from __future__ import annotations

from typing import TYPE_CHECKING
from ..math import Vector3D, Rotation

if TYPE_CHECKING:
    from typing import TypeVar
    T = TypeVar('T', int, float, default=float)


class BaseEntity[T]:
    __slots__ = ('id',)

    def __init__(self, entity_id: T) -> None:
        self.id: T = entity_id

    def __eq__(self, other: Entity) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f"<BaseEntity id={self.id}>"


class Entity(BaseEntity[int]):
    __slots__ = ('uuid', 'position')

    def __init__(self, entity_id: int, object_uuid: str, position: Vector3D) -> None:
        super().__init__(entity_id)
        self.uuid: str = object_uuid
        self.position: Vector3D[int] = position

    def __hash__(self) -> int:
        return hash((self.id, self.uuid))

    def __repr__(self):
        return f"<Entity id={self.id}, position={self.position}>"


class ObjectEntity(Entity):
    __slots__ = ('type_id',)

    def __init__(self, entity_id: int, entity_type_id: int, object_uuid: str,  position: Vector3D[float]):
        super().__init__(entity_id, object_uuid, position)
        self.type_id: int = entity_type_id


    def __repr__(self):
        return f"<ObjectEntity id={self.id}, type_id={self.type_id}, position={self.position}>"
