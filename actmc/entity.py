from __future__ import annotations

from typing import TYPE_CHECKING


class Entity:
    """Represents a generic entity in the Minecraft world (player, mob, item, etc.)."""

    __slots__ = ('id',)

    def __init__(self, entity_id: int) -> None:
        self.id: int = entity_id

    def __repr__(self) -> str:
        return f"<Entity id={self.id}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Entity) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Player(Entity):
    """Represents the player's client instance."""

    __slots__ = ('username', 'uid', 'gamemode', 'health', 'food', 'food_saturation',
                 'experience_bar', 'level', 'total_experience', 'selected_slot')

    if TYPE_CHECKING:
        # Health
        health: float
        food: int
        food_saturation: float
        # Set Experience
        experience_bar: float
        level: int
        total_experience: int
        # Held Item slot.
        selected_slot: int

    def __init__(self,  uid: str, username: str) -> None:
        super().__init__(0)
        self.uid: str = uid
        self.username: str = username

    @property
    def is_dead(self) -> bool:
        return self.health <= 0




    def __repr__(self) -> str:
        return f"<Player username={self.id} uid={self.uid} >"