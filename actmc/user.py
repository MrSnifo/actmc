from __future__ import annotations

from .entities.entity import BaseEntity
from typing import TYPE_CHECKING, overload
from .math import Vector3D, Rotation

if TYPE_CHECKING:
    from typing import Literal, Dict, ClassVar, Optional
    from .state import ConnectionState


class User(BaseEntity):
    """Enhanced Minecraft Player class with utility methods

    Note: use hasattr to make sure that data....

    """
    __slots__ = ('_state', 'username', 'uuid', 'gamemode', 'dimension',
                 'health', 'food', 'food_saturation',
                 'level', 'total_experience', 'experience_bar',
                 'held_slot',
                 'position', 'rotation', 'spawn_point')

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

        # Spawn
        spawn_point: Vector3D[float]

    def __init__(self, entity_id: int, username: str, uuid: str, *, state: ConnectionState) -> None:
        super().__init__(entity_id)
        self._state: ConnectionState = state
        self._update(username, uuid)


    def _update(self, username: str, uuid: str) -> None:
        self.username = username
        self.uuid = uuid

    async def translate(self,
                        position: Optional[Vector3D[float]] = None,
                        rotation: Optional[Rotation]  = None,
                        on_ground: bool = True) -> None:
        """
        Update the player's position and/or rotation.

        Parameters
        ----------
        position: Optional[Vector3D[float]]
            The new position to set for the player.
        rotation: Optional[Rotation]
            The new rotation to set for the player.
        on_ground: bool
             Whether the player is currently on the ground.

             When this changes from False to True, fall damage may be applied
             based on the distance fallen.
        """

        if position is not None:
            self.position = position
        if rotation is not None:
            self.rotation = rotation

        if position is not None and rotation is not None:
            await self._state.send_player_position_and_look(self.position, self.rotation, on_ground)
        elif position is not None:
            await self._state.send_player_position(self.position, on_ground)
        elif rotation is not None:
            await self._state.send_player_look(self.rotation, on_ground)
        else:
            await self._state.send_player_packet(on_ground)

    async def sneak(self, state: bool = True) -> None:
        """
        Perform sneaking action.

        Parameters
        ----------
        state: bool
            True to start sneaking, False to stop sneaking. Default is True.
        """
        await self._state.send_entity_action(self.id, 0 if state else 1)

    async def sprint(self, state: bool = True) -> None:
        """
        Perform sprinting action.

        Parameters
        ----------
        state: bool
            True to start sprinting, False to stop sprinting. Default is True.
        """
        await self._state.send_entity_action(self.id, 3 if state else 4)

    @overload
    async def action(self, action_id: Literal[5], jump_boost: int) -> None:
        ...

    @overload
    async def action(self, action_id: Literal[2, 6, 7, 8]) -> None:
        ...

    async def action(self, action_id: int, jump_boost: int = 0) -> None:
        """
        Perform an entity action.

        Parameters
        ----------
        action_id: int
            The ID of the action to perform. Valid values include:

                2: Leave bed

                5: Start jump with horse (should be handled separately with jump_boost)

                6: Stop jump with horse

                7: Open horse inventory

                8: Start flying with elytra
        jump_boost: int
            Jump strength (0-100) used only with action_id 5.
        """
        await self._state.send_entity_action(self.id, action_id, jump_boost)

    