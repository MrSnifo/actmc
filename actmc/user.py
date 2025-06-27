from __future__ import annotations

from .entities.entity import BaseEntity
from typing import TYPE_CHECKING
from .math import Vector3D, Rotation

if TYPE_CHECKING:
    from typing import Literal, Dict, ClassVar
    from .state import ConnectionState


class User(BaseEntity):
    """Enhanced Minecraft Player class with utility methods

    Noit: use Hasattrube to make sure that data....

    """
    __slots__ = ('_state', 'username', 'uuid', 'gamemode', 'dimension',
                 'health', 'food', 'food_saturation',
                 'level', 'total_experience', 'experience_bar',
                 'held_slot',
                 'position', 'rotation')

    GAMEMODE: ClassVar[Dict[int, Literal['survival', 'creative', 'adventure', 'spectator']]] = {
        0: 'survival',
        1: 'creative',
        2: 'adventure',
        3: 'spectator'
    }

    DIMENSION: ClassVar[Dict[int, Literal['nether', 'overworld', 'end']]] = {
        -1: 'nether',
        0: 'overworld',
        1: 'end'
    }

    if TYPE_CHECKING:
        username: str
        uuid: str
        gamemode: Literal['survival', 'creative', 'adventure', 'spectator']
        dimension: Literal['nether', 'overworld', 'end']

        # Health
        health: float
        food: int
        food_saturation: float

        # Experience
        level: int
        total_experience: int
        experience_bar: float

        # Inventory
        held_slot: int

        # Position
        position: Vector3D[float]
        rotation: Rotation


    def __init__(self, entity_id: int, username: str, uuid: str, *, state: ConnectionState) -> None:
        super().__init__(entity_id)
        self._state: ConnectionState = state
        self._update(username, uuid)

    def _update(self, username: str, uuid: str) -> None:
        self.username = username
        self.uuid = uuid
