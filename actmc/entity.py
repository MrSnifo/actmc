from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import math

class Entity:
    """Represents a generic entity in the Minecraft world (player, mob, item, etc.)."""

    __slots__ = ('id', 'type')

    def __init__(self, entity_id: int, entity_type: str = 'unknown') -> None:
        self.id: int = entity_id
        self.type: str = entity_type

    def __repr__(self) -> str:
        return f"<Entity id={self.id}, type={self.type}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Entity) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Player(Entity):
    """Represents the player's client instance."""

    __slots__ = ('username', 'uid', 'gamemode', 'health', 'food', 'food_saturation',
                 'experience_bar', 'level', 'total_experience', 'selected_slot',
                 'position', 'rotation')

    if TYPE_CHECKING:
        # Health
        health: float
        food: int
        food_saturation: float
        # Experience
        experience_bar: float
        level: int
        total_experience: int
        # Held item
        selected_slot: int
        # Position, rotation
        position: math.Vector3D
        rotation: math.Rotation

    def __init__(self, uid: str, username: str) -> None:
        super().__init__(0, 'player')
        self.uid: str = uid
        self.username: str = username

    @property
    def is_dead(self) -> bool:
        return self.health <= 0

    def __repr__(self) -> str:
        return f"<Player username={self.username} uid={self.uid}>"
