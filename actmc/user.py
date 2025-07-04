from __future__ import annotations

from .entities.entity import BaseEntity
from .entities.player import Player
from typing import TYPE_CHECKING, overload
from .math import Vector3D, Rotation

if TYPE_CHECKING:
    from typing import Literal, Dict, ClassVar, Optional
    from .state import ConnectionState
    from .ui import gui


class User(Player):
    """Enhanced Minecraft Player class with utility methods

    Note: use hasattr to make sure that data....

    """
    __slots__ = ('_state', 'username', 'gamemode', 'dimension',
                 'health', 'food', 'food_saturation',
                 'level', 'total_experience', 'experience_bar',
                 'held_slot',
                 'spawn_point',
                 'invulnerable', 'flying', 'allow_flying', 'creative_mode', 'flying_speed', 'fov_modifier')

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
        gamemode: int
        dimension: int

        # Health
        food: int
        food_saturation: float

        # Experience
        level: int
        total_experience: int
        experience_bar: float

        # Inventory
        held_slot: int

        # Spawn
        spawn_point: Vector3D[float]

        # Abilities
        invulnerable: bool
        flying: bool
        allow_flying: bool
        creative_mode: bool
        flying_speed: float
        fov_modifier: float

    def __init__(self, entity_id: int, username: str, uuid: str, *, state: ConnectionState) -> None:
        super().__init__(entity_id, uuid, Vector3D(0, 0, 0), Rotation(0, 0), {},
                         state.tablist)
        self._state: ConnectionState = state
        self._update(username, uuid)

    def _update(self, username: str, uuid: str) -> None:
        self.username = username
        self.uuid = uuid

    @property
    def inventory(self) -> Optional[gui.Window]:
        return self._state.windows.get(0)

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
            await self._state.send_player_ground(on_ground)

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

    async def respawn(self) -> None:
        """Perform a respawn"""
        await self._state.send_client_status(0)

    async def interact_with(self, entity: BaseEntity, hand: Literal[0, 1] = 0) -> None:
        """
        Perform a right-click interaction with an entity.

        Parameters
        ----------
        entity: BaseEntity
            The target entity.
        hand: Literal[0, 1]
            Hand used to interact (0 = main hand, 1 = off-hand).
        """
        await self._state.send_use_entity_interact(entity.id, hand=hand)

    async def attack(self, entity: BaseEntity) -> None:
        """
        Perform a left-click attack on an entity.

        Parameters
        ----------
        entity: BaseEntity
            The target entity.
        """
        await self._state.send_use_entity_attack(entity.id)

    async def interact_at(self, entity: BaseEntity, hitbox: Vector3D[float], hand: Literal[0, 1] = 0) -> None:
        """
        Perform a precise interaction at a specific location on an entity.

        Parameters
        ----------
        entity: BaseEntity
            The target entity.
        hitbox: Vector3D[float]
            The coordinates on the entity's hitbox.
        hand: Literal[0, 1]
            Hand used to interact (0 = main hand, 1 = off-hand).
        """
        await self._state.send_use_entity_interact_at(entity.id, hitbox=hitbox, hand=hand)

    async def swing_arm(self, hand: Literal[0, 1] = 0) -> None:
        """
        Swing the player's arm.

        Parameters
        ----------
        hand: Literal[0, 1]
            Hand to swing (0 = main hand, 1 = off-hand).
        """
        await self._state.send_swing_arm(hand)

    async def use_item(self, hand: Literal[0, 1] = 0) -> None:
        """
        Use the item in the specified hand.

        This sends a Use Item packet to the server, which is triggered when
        right-clicking with an item. This can be used for:
        - Eating food
        - Drinking potions
        - Using tools (bow, fishing rod, etc.)
        - Placing blocks
        - Activating items

        Parameters
        ----------
        hand: Literal[0, 1]
            Hand to use the item with (0 = main hand, 1 = off hand).
        """
        await self._state.send_use_item(hand)

    async def release_item_use(self) -> None:
        """
        Use the currently held item.

        For example, shooting a bow, finishing eating, or using buckets.
        """
        await self._state.send_player_digging(5, Vector3D(0, 0, 0), 0)

    async def start_digging(self, position: Vector3D[int], face: int) -> None:
        """
        Start digging a block.

        Parameters
        ----------
        position: Vector3D[int]
            The (x, y, z) coordinates of the block to start digging.
        face: int
            The face of the block being targeted (0=down, 1=up, 2=north, 3=south, 4=west, 5=east).
        """
        await self._state.send_player_digging(0, position, face)

    async def cancel_digging(self, position: Vector3D[int], face: int) -> None:
        """
        Cancel digging a block.

        Parameters
        ----------
        position: Vector3D[int]
            The (x, y, z) coordinates of the block where digging is cancelled.
        face: int
            The face of the block being targeted.
        """
        await self._state.send_player_digging(1, position, face)

    async def finish_digging(self, position: Vector3D[int], face: int) -> None:
        """
        Finish digging (break) a block.

        Parameters
        ----------
        position: Vector3D[int]
            The (x, y, z) coordinates of the block being broken.
        face: int
            The face of the block being targeted.
        """
        await self._state.send_player_digging(2, position, face)

    async def drop_item_stack(self) -> None:
        """
        Drop the entire item stack.

        This corresponds to pressing the drop key with a modifier to drop the full stack.
        Position is set to (0, 0, 0) and face is set to down (0) as per protocol.
        """
        await self._state.send_player_digging(3, Vector3D(0, 0, 0), 0)

    async def drop_item(self) -> None:
        """
        Drop a single item.

        This corresponds to pressing the drop key without modifiers.
        Position is set to (0, 0, 0) and face is set to down (0) as per protocol.
        """
        await self._state.send_player_digging(4, Vector3D(0, 0, 0), 0)


    async def swap_item_in_hand(self) -> None:
        """
        Swap item to the second hand.

        Used to swap or assign an item to the offhand slot.
        Position is set to (0, 0, 0) and face is set to down (0) as per protocol.
        """
        await self._state.send_player_digging(6, Vector3D(0, 0, 0), 0)