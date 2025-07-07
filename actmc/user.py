"""
The MIT License (MIT)

Copyright (c) 2025-present Snifo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, overload
from .entities.entity import BaseEntity
from .math import Vector3D, Rotation
from .entities.player import Player

if TYPE_CHECKING:
    from typing import Literal, Dict, ClassVar, Optional
    from .state import ConnectionState
    from .ui import gui

__slots__ = ('User',)

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
        health: float
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
        """Get the player's inventory window"""
        return self._state.windows.get(0)

    async def translate(self,
                        position: Optional[Vector3D[float]] = None,
                        rotation: Optional[Rotation] = None,
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
            await self._state.tcp.player_position_and_look(self.position, self.rotation, on_ground)
        elif position is not None:
            await self._state.tcp.player_position(self.position, on_ground)
        elif rotation is not None:
            await self._state.tcp.player_look(self.rotation, on_ground)
        else:
            await self._state.tcp.player_ground(on_ground)

    async def sneak(self, state: bool = True) -> None:
        """
        Perform sneaking action.

        Parameters
        ----------
        state: bool
            True to start sneaking, False to stop sneaking. Default is True.
        """
        await self._state.tcp.entity_action(self.id, 0 if state else 1, 0)

    async def sprint(self, state: bool = True) -> None:
        """
        Perform sprinting action.

        Parameters
        ----------
        state: bool
            True to start sprinting, False to stop sprinting. Default is True.
        """
        await self._state.tcp.entity_action(self.id, 3 if state else 4, 0)

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
        await self._state.tcp.entity_action(self.id, action_id, jump_boost)

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
        await self._state.tcp.use_entity(entity.id, 0, hand=hand)

    async def attack(self, entity: BaseEntity) -> None:
        """
        Perform a left-click attack on an entity.

        Parameters
        ----------
        entity: BaseEntity
            The target entity.
        """
        await self._state.tcp.use_entity(entity.id, 1)

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
        await self._state.tcp.use_entity(entity.id, 2, hitbox=hitbox, hand=hand)

    async def swing_arm(self, hand: Literal[0, 1] = 0) -> None:
        """
        Swing the player's arm.

        Parameters
        ----------
        hand: Literal[0, 1]
            Hand to swing (0 = main hand, 1 = off-hand).
        """
        await self._state.tcp.swing_arm(hand)

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
        await self._state.tcp.use_item(hand)

    async def spectate_entity(self, target_uuid: str) -> None:
        """
        Teleport to and spectate an entity.

        This sends a Spectate packet to the server to teleport the player to the
        specified entity. The player must be in spectator mode for this to work.
        The entity can be in any dimension - if necessary, the player will be
        respawned in the correct world.

        Parameters
        ----------
        target_uuid: str
            The UUID of the entity to teleport to and spectate. While commonly
            used for players, this can be any entity UUID. The packet will be
            ignored if the entity cannot be found, isn't loaded, or if the player
            attempts to teleport to themselves.
        """
        await self._state.tcp.spectate(target_uuid)

    async def release_item_use(self) -> None:
        """
        Use the currently held item.

        For example, shooting a bow, finishing eating, or using buckets.
        """
        await self._state.tcp.player_digging(5, Vector3D(0, 0, 0), 0)

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
        await self._state.tcp.player_digging(0, position, face)

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
        await self._state.tcp.player_digging(1, position, face)

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
        await self._state.tcp.player_digging(2, position, face)

    async def drop_item_stack(self) -> None:
        """
        Drop the entire item stack.

        This corresponds to pressing the drop key with a modifier to drop the full stack.
        Position is set to (0, 0, 0) and face is set to down (0) as per protocol.
        """
        await self._state.tcp.player_digging(3, Vector3D(0, 0, 0), 0)

    async def drop_item(self) -> None:
        """
        Drop a single item.

        This corresponds to pressing the drop key without modifiers.
        Position is set to (0, 0, 0) and face is set to down (0) as per protocol.
        """
        await self._state.tcp.player_digging(4, Vector3D(0, 0, 0), 0)

    async def swap_item_in_hand(self) -> None:
        """
        Swap item to the second hand.

        Used to swap or assign an item to the offhand slot.
        Position is set to (0, 0, 0) and face is set to down (0) as per protocol.
        """
        await self._state.tcp.player_digging(6, Vector3D(0, 0, 0), 0)

    async def toggle_flight(self) -> None:
        """
        Toggle flight mode on/off.

        This automatically handles the flight state based on current abilities.
        Only works if the player has flight permissions (creative mode, etc.).
        """
        if not hasattr(self, 'allow_flying') or not self.allow_flying:
            return

        # Toggle flying state
        new_flying_state = not getattr(self, 'flying', False)
        self.flying = new_flying_state

        # Build flags based on current abilities
        flags = 0
        if getattr(self, 'invulnerable', False):
            flags |= 0x08  # Damage disabled
        if getattr(self, 'allow_flying', False):
            flags |= 0x04
        if new_flying_state:
            flags |= 0x02
        if getattr(self, 'creative_mode', False):
            flags |= 0x01

        flying_speed = getattr(self, 'flying_speed', 0.05)
        walking_speed = 0.1  # Default walking speed
        await self._state.tcp.player_abilities(flags, flying_speed, walking_speed)

    async def change_held_slot(self, slot: int) -> None:
        """
        Change the selected hotbar slot.

        Parameters
        ----------
        slot: int
            The hotbar slot to select (0-8).
        """
        if not 0 <= slot <= 8:
            raise ValueError("Slot must be between 0 and 8")

        self.held_slot = slot
        await self._state.tcp.held_item_change(slot)

    async def interact_with_block(self, position: Vector3D[int], face: int, hand: Literal[0, 1] = 0,
                          cursor: Vector3D[float] = None) -> None:
        """
        Interact with a block (right-click action).

        This function handles all types of block interactions including placing blocks,
        opening containers, activating mechanisms, using doors, and other right-click actions.

        Parameters
        ----------
        position: Vector3D[int]
            The position of the block to interact with.
        face: int
            The face of the block being targeted.
        hand: Literal[0, 1]
            Hand to use for the interaction:
            - 0: main hand
            - 1: off-hand
        cursor: Vector3D[float], optional
            The cursor position on the targeted face, with coordinates from 0.0 to 1.0.
            If not provided, defaults to center of the face (0.5, 0.5, 0.5).

        Notes
        -----
        Behavior depends on your held item and the block. Examples:
        - Placing blocks

        - Opening containers (chests, furnaces)

        - Activating buttons, levers, redstone

        - Using tools on blocks

        Ensure you have permission to interact with blocks or open containers.
        """
        if cursor is None:
            cursor = Vector3D(0.5, 0.5, 0.5)

        await self._state.tcp.player_block_placement(position, face, hand, cursor)

    async def update_sign_text(self, position: Vector3D[float], line1: str = "", line2: str = "",
                               line3: str = "", line4: str = "") -> None:
        """
        Update the text on a sign.

        Parameters
        ----------
        position: Vector3D[float]
            The position of the sign.
        line1: str
            First line of text.
        line2: str
            Second line of text.
        line3: str
            Third line of text.
        line4: str
            Fourth line of text.
        """
        await self._state.tcp.update_sign(position, line1, line2, line3, line4)

    async def move_vehicle(self, position: Vector3D[float], yaw: float, pitch: float) -> None:
        """
        Move a vehicle (boat, minecart, etc.) that the player is riding.

        Parameters
        ----------
        position: Vector3D[float]
            The absolute position of the vehicle.
        yaw: float
            The absolute yaw rotation in degrees.
        pitch: float
            The absolute pitch rotation in degrees.
        """
        await self._state.tcp.vehicle_move(position, yaw, pitch)

    async def steer_boat(self, right_paddle: bool, left_paddle: bool) -> None:
        """
        Control boat paddle movement for visual effects.

        Parameters
        ----------
        right_paddle: bool
            Whether the right paddle is turning.
        left_paddle: bool
            Whether the left paddle is turning.
        """
        await self._state.tcp.steer_boat(right_paddle, left_paddle)

    async def steer_vehicle(self, sideways: float, forward: float, flags: int) -> None:
        """
        Control vehicle movement and actions.

        Parameters
        ----------
        sideways: float
            Sideways movement. Positive values steer to the left of the player.
        forward: float
            Forward movement. Positive values move forward.
        flags: int
            Bit mask for vehicle actions. 0x1: jump, 0x2: unmount.
        """
        await self._state.tcp.steer_vehicle(sideways, forward, flags)
