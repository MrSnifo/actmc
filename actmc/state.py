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

from . import entities, math, protocol
from typing import TYPE_CHECKING
from .ui.chat import Message
from .ui import tab, gui
from .chunk import *
from .user import User
import asyncio

from .entities import BLOCK_ENTITY_TYPES, MOB_ENTITY_TYPES, OBJECT_ENTITY_TYPES

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Literal, Optional, Tuple
    from .gateway import MinecraftSocket
    from .tcp import TcpClient

import logging
_logger = logging.getLogger(__name__)

__all__ = ('ConnectionState',)

class ConnectionState:
    """
    Manages connection state and packet handling for a Minecraft client.

    This class handles all incoming packet parsing, maintains world state,
    manages player information, and provides an event-driven interface
    for interacting with the Minecraft server.
    """

    if TYPE_CHECKING:
        _get_socket: Callable[..., MinecraftSocket]

    # Class-level packet parser cache for performance
    _packet_parsers: Dict[int, str] = {}

    def __init__(self, tcp: TcpClient, dispatcher: Callable[..., Any]) -> None:
        self.tcp = tcp
        self._dispatch = dispatcher
        self._load_chunks = True

        # Event system
        self._waiters: Dict[str, List[asyncio.Future]] = {}

        # Player state
        self.username: Optional[str] = None
        self.uid: Optional[str] = None
        self.user: Optional[User] = None

        # Server information
        self.server_difficulty: Optional[str] = None
        self.server_max_players: Optional[int] = None
        self.server_world_type: Optional[str] = None
        self.server_world_age = 0
        self.server_time_of_day = 0

        # World state
        self.chunks: Dict[math.Vector2D, Chunk] = {}

        self.entities: Dict[int, entities.entity.Entity] = {}
        self.tablist: Dict[str, tab.TabPlayer] = {}
        self.windows: Dict[int, gui.Window] = {}

        # Initialize packet parser cache
        if not self._packet_parsers:
            self._build_parser_cache()

        _logger.debug("ConnectionState initialized")

    @classmethod
    def _build_parser_cache(cls) -> None:
        """
        Build a performance cache mapping packet IDs to parser methods.

        Scans all methods starting with 'parse_0x' and creates a lookup table
        for efficient packet routing.
        """
        for attr_name in dir(cls):
            if attr_name.startswith('parse_0x'):
                try:
                    packet_id = int(attr_name[8:], 16)
                    cls._packet_parsers[packet_id] = attr_name
                except ValueError:
                    _logger.warning(f"Invalid packet parser method name: {attr_name}")
                    continue

        _logger.debug(f"Built packet parser cache with {len(cls._packet_parsers)} parsers")

    def _get_socket(self) -> Optional[MinecraftSocket]:
        """Get the current socket connection."""

    # ================================ Event System ================================

    async def _wait_for(self, event: str, timeout: Optional[float] = 30.0) -> Any:
        """
        Wait for a specific event to occur.

        Args:
            event: Event name to wait for
            timeout: Maximum time to wait (None for no timeout)

        Returns:
            Event data when the event occurs

        Raises:
            asyncio.TimeoutError: If timeout is reached before event occurs
        """
        future = asyncio.Future()

        if event not in self._waiters:
            self._waiters[event] = []
        self._waiters[event].append(future)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            # Clean up the future from waiters list
            if event in self._waiters and future in self._waiters[event]:
                self._waiters[event].remove(future)
            raise asyncio.TimeoutError(f"Timed out waiting for event '{event}'")

    def _trigger_event(self, event: str, data: Any = None) -> None:
        """
        Trigger an event and notify all waiting futures.

        Args:
            event: Name of the event to trigger
            data: Data to pass to event handlers
        """
        if event not in self._waiters:
            return

        # Notify all waiters and clear the list
        for future in self._waiters[event]:
            if not future.done():
                future.set_result(data)

        self._waiters[event].clear()

    def _has_waiters(self, event: str) -> bool:
        """
        Check if there are any active waiters for an event.

        Args:
            event: Event name to check

        Returns:
            True if there are active waiters, False otherwise
        """
        return event in self._waiters and any(not f.done() for f in self._waiters[event])

    # ============================== Network Operations ==============================

    async def send_packet(self, packet_id: int, buffer: bytes) -> None:
        """
        Send a packet to the server.

        Args:
            packet_id: Minecraft protocol packet ID
            buffer: Packet data payload

        Raises:
            RuntimeError: If socket is not available or not connected
        """
        socket = self._get_socket()
        if not socket:
            raise RuntimeError("Socket is not initialized or not connected")

        await socket.write_packet(packet_id=packet_id, data=buffer)

    async def send_initial_packets(self, username: str) -> None:
        """
        Send initial handshake and login packets to establish connection.

        Args:
            username: Player username for login

        Raises:
            RuntimeError: If TCP client is not properly configured
        """
        try:
            handshake_packet = self.tcp.build_handshake_packet
            login_packet = self.tcp.build_login_packet(username)

            await self.send_packet(0x00, handshake_packet.getvalue())
            await self.send_packet(0x00, login_packet.getvalue())

            # Performance warning for chunk loading
            if self._load_chunks:
                _logger.warning(
                    "Chunk loading is enabled - may cause performance issues "
                    "and increased memory usage on large worlds"
                )

            self._dispatch('handshake')

        except Exception as e:
            _logger.error(f"Failed to send initial packets: {e}")
            raise

    # ============================== World State Management ==============================

    @staticmethod
    def _get_position_components(
        position: math.Vector3D[int]
    ) -> Tuple[math.Vector2D[int], math.Vector3D[int], int]:
        """
        Convert world position to chunk coordinates and relative position.

        Args:
            position: Absolute world position

        Returns:
            Tuple of (chunk_coordinates, relative_position, section_y)
        """
        x, y, z = position

        # Calculate chunk coordinates
        chunk_x, rel_x = x >> 4, x & 0xF
        chunk_z, rel_z = z >> 4, z & 0xF

        # Calculate section and relative Y
        section_y, rel_y = y // 16, y % 16

        return (
            math.Vector2D(chunk_x, chunk_z),
            math.Vector3D(rel_x, rel_y, rel_z),
            section_y
        )

    def get_block_state(self, position: math.Vector3D[int]) -> Optional[Block]:
        """
        Get the block state at a specific world position.

        Args:
            position: World position to query

        Returns:
            Block state if available, None otherwise

        Raises:
            RuntimeError: If chunk loading is disabled
        """
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled - cannot query block states")

        chunk_coords, block_pos, section_y = self._get_position_components(position)

        chunk = self.chunks.get(chunk_coords)
        if chunk is None:
            return None

        section = chunk.get_section(section_y)
        if section is None:
            return None

        return section.get_state(block_pos)

    def set_block_state(self, state: Block) -> None:
        """
        Set the block state at a specific world position.

        Args:
            state: Block state to set

        Raises:
            RuntimeError: If chunk loading is disabled
        """
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled - cannot modify block states")

        chunk_coords, block_pos, section_y = self._get_position_components(state.position)

        chunk = self.chunks.get(chunk_coords)
        if chunk is None:
            return

        section = chunk.get_section(section_y)
        if section is None:
            section = ChunkSection(math.Vector2D(0, 0))
            chunk.set_section(section_y, section)

        section.set_state(block_pos, state)

    def set_block_entity(self,
        pos: math.Vector3D[int],
        block_entity: entities.entity.BaseEntity[str]
    ) -> None:
        """
        Set a block entity at a specific world position.

        Args:
            pos: World position for the block entity
            block_entity: Block entity instance to set

        Raises:
            RuntimeError: If chunk loading is disabled
        """
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled - cannot modify block entities")

        chunk_coords, block_pos, section_y = self._get_position_components(pos)

        chunk = self.chunks.get(chunk_coords)
        if chunk is None:
            return

        section = chunk.get_section(section_y)
        if section is None:
            section = ChunkSection(math.Vector2D(0, 0))
            chunk.set_section(section_y, section)

        section.set_entity(block_pos, block_entity)

    @staticmethod
    def _create_block_entity(entity_id: str, data: Any) -> entities.entity.BaseEntity[str]:
        """
        Create a block entity instance from NBT data.

        Args:
            entity_id: Minecraft block entity identifier
            data: NBT data for the block entity

        Returns:
            Appropriate block entity instance
        """
        entity_class = BLOCK_ENTITY_TYPES.get(entity_id)

        if entity_class:
            return entity_class(entity_id, data)
        else:
            # Create generic entity for unknown types
            block_entity = entities.entity.BaseEntity(entity_id)
            if data:
                _logger.warning(f"Unknown block entity: {entity_id}, Type: '{entity_id}' with data: {data}")
            return block_entity

    @staticmethod
    def _create_mob_entity(mob_type: int,
                           entity_id: int,
                           uuid: str,
                           position: math.Vector3D[float],
                           rotation: math.Rotation,
                           metadata: Dict[int, Dict[str, Any]]) -> Any:
        entity_class = MOB_ENTITY_TYPES.get(mob_type)
        if entity_class:
            return entity_class(entity_id, uuid, position, rotation, metadata)
        else:
            mob_entity = entities.entity.Entity(entity_id, uuid, position, rotation, metadata)
            if mob_type:
                _logger.warning(f"Unknown mob entity: {entity_id}, Type: '{mob_type}', With data: {metadata}")
            return mob_entity

    @staticmethod
    def _create_object_entity(object_type: int,
                           entity_id: int,
                           uuid: str,
                           position: math.Vector3D[float],
                           rotation: math.Rotation,
                           data: int) -> Any:
        entity = OBJECT_ENTITY_TYPES.get(object_type)
        if entity:
            if isinstance(entity, dict):
                entity = entity.get(data)
            return entity(entity_id, uuid, position, rotation, {-1: {'value': data}})
        else:
            mob_entity = entities.entity.Entity(entity_id, uuid, position, rotation, {-1: {'value': data}})
            if object_type:
                _logger.warning(f"Unknown object entity: {entity_id}, Type: '{object_type}', With data: {data}")
            return mob_entity

    # ============================== Packet Parsing ==============================

    async def parse(self, packet_id: int, buffer: protocol.ProtocolBuffer) -> None:
        """
        Parse and handle incoming packets.

        Routes packets to appropriate parser methods based on packet ID.

        Args:
            packet_id: Minecraft protocol packet identifier
            buffer: Packet data buffer
        """
        try:
            parser_name = self._packet_parsers.get(packet_id)
            if parser_name:
                func = getattr(self, parser_name)
                await func(buffer)

        except Exception as error:
            _logger.exception(f"Failed to parse packet 0x{packet_id:02X}: {error}")
            self._dispatch('error', packet_id, error)

    # ============================== Client Actions ==============================

    async def send_use_entity(
            self,
            target_id: int,
            action: Literal[0, 1, 2],
            hitbox: Optional[math.Vector3D[float]] = None,
            hand: Optional[Literal[0, 1]] = None) -> None:
        """Send a Use Entity packet to the server. """
        buffer =protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(target_id))
        buffer.write(protocol.write_varint(action))

        if action == 2:
            buffer.write(protocol.pack_float(hitbox.x or 0.0))
            buffer.write(protocol.pack_float(hitbox.y or 0.0))
            buffer.write(protocol.pack_float(hitbox.z or 0.0))

        if action in (0, 2):
            buffer.write(protocol.write_varint(hand if hand is not None else 0))

        await self.send_packet(0x0A, buffer.getvalue())

    async def send_swing_arm(self, hand: int = 0) -> None:
        """
        Send the Animation (Swing Arm) packet (0x1D).

        Parameters
        ----------
        hand: int
            Hand used for the animation.
            0 = main hand
            1 = off-hand
        """
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(hand))
        await self.send_packet(0x1D, buffer.getvalue())

    async def send_use_item(self, hand: int = 0) -> None:
        """
        Send the Use Item packet (0x20).

        Sent when pressing the Use Item key (default: right click) with an item in hand.

        Parameters
        ----------
        hand: int
            Hand used for the animation.
            0 = main hand
            1 = off-hand
        """
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(hand))
        await self.send_packet(0x20, buffer.getvalue())

    async def send_confirm_transaction(self, window_id: int, action_number: int, accepted: bool) -> None:
        """
        Send the Confirm Transaction packet (0x05).

        If a transaction sent by the client was not accepted, the server will reply with a
        Confirm Transaction (clientbound) packet with the Accepted field set to false.
        When this happens, the client must send this packet to apologize (as with movement),
        otherwise the server ignores any successive transactions.

        Parameters
        ----------
        window_id: int
            The ID of the window that the action occurred in.
        action_number: int
            Every action that is to be accepted has a unique number. This number is an
            incrementing integer (starting at 1) with separate counts for each window ID.
        accepted: bool
            Whether the action was accepted.
        """
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_byte(window_id))
        buffer.write(protocol.pack_short(action_number))
        buffer.write(protocol.pack_bool(accepted))
        await self.send_packet(0x05, buffer.getvalue())

    async def send_player_digging(self,
                                  status: int,
                                  position: math.Vector3D[int] = math.Vector3D(0, 0, 0),
                                  face: int = 0) -> None:
        """
        Send the Player Digging packet (0x14).

        Parameters
        ----------
        status: int
            The action the player is taking against the block.

            Valid values:

            0 : Started digging

            1 : Cancelled digging

            2 : Finished digging

            3 : Drop item stack (position set to 0,0,0; face = down)

            4 : Drop item (position set to 0,0,0; face = down)

            5 : Shoot arrow / finish eating (position set to 0,0,0; face = down)

            6 : Swap item in hand (position set to 0,0,0; face = down)

        position: math.Vector3D[int]
            The block position (x, y, z). Ignored if status is 3-6.

        face: int
            The face of the block being hit (0=down,1=up,2=north,3=south,4=west,5=east).

            Ignored if status is 3-6. Defaults to 0.
        """
        buffer = protocol.ProtocolBuffer()
        # Write fields in correct order: Status, Position, Face
        buffer.write(protocol.write_varint(status))
        buffer.write(protocol.pack_position(position.x, position.y, position.z))  # Position as single field
        buffer.write(protocol.pack_byte(face))
        await self.send_packet(0x14, buffer.getvalue())

    async def send_client_status(self, action_id: Literal[0, 1]) -> None:
        """Send a Client Status packet to the server."""
        await self.send_packet(0x03, protocol.write_varint(action_id))

    async def get_statistics(self) -> Dict[str, int]:
        """
        Request and retrieve player statistics from the server.

        Returns:
            Dictionary of player statistics
        """
        if not self._has_waiters('0x07'):
            await self.send_client_status(1)

        result: Dict[str, int] = await self._wait_for('0x07')
        return result

    async def send_player_packet(self, on_ground: bool) -> None:
        """Send Player packet (0x0C) - indicates if player is on ground"""
        data = protocol.pack_bool(on_ground)
        await self.send_packet(0x0C, data)

    async def send_player_position(self, position: math.Vector3D[float], on_ground: bool) -> None:
        """Send Player Position packet (0x0D) - updates XYZ position"""
        data = (protocol.pack_double(position.x) +
                protocol.pack_double(position.y) +
                protocol.pack_double(position.z) +
                protocol.pack_bool(on_ground))
        await self.send_packet(0x0D, data)

    async def send_player_look(self, rotation: math.Rotation, on_ground: bool) -> None:
        """Send Player Look packet (0x0F) - updates rotation"""
        data = (protocol.pack_float(rotation.yaw) +
                protocol.pack_float(rotation.pitch) +
                protocol.pack_bool(on_ground))
        await self.send_packet(0x0F, data)

    async def send_entity_action(self, entity_id: int, action_id: int, jump_boost: int = 0) -> None:
        """Send Entity Action packet (0x15) - notifies server of player actions

        Parameters
        ----------
        entity_id : int
            The ID of the entity performing the action.
        action_id : int
            The ID of the action being performed.
        jump_boost : int, optional
            Used only for 'start jump with horse' action (action_id == 5).
        """
        data = (
                protocol.write_varint(entity_id) +
                protocol.write_varint(action_id) +
                protocol.write_varint(jump_boost)
        )
        await self.send_packet(0x15, data)

    async def send_player_position_and_look(self, position: math.Vector3D[float], rotation: math.Rotation,
                                      on_ground: bool) -> None:
        """Send Player Position And Look packet (0x0E) - combines position and rotation"""
        data = (protocol.pack_double(position.x) +
                protocol.pack_double(position.y) +
                protocol.pack_double(position.z) +
                protocol.pack_float(rotation.yaw) +
                protocol.pack_float(rotation.pitch) +
                protocol.pack_bool(on_ground))
        await self.send_packet(0x0E, data)

    # ============================== Packet Parsers ==============================

    async def parse_0x23(self, buffer: protocol.ProtocolBuffer) -> None:
        """
        Handle Join Game packet (0x23).

        Processes initial game state including player info and server settings.
        """
        # Parse player information
        entity_id = protocol.read_int(buffer)
        gamemode = protocol.read_ubyte(buffer)
        dimension = protocol.read_int(buffer)

        # Parse server information
        self.server_difficulty = protocol.read_ubyte(buffer)
        self.server_max_players = protocol.read_ubyte(buffer)
        self.server_world_type = protocol.read_string(buffer).lower()

        # Update player state
        self.user = User(entity_id, self.username, self.uid, state=self)
        self.user.gamemode = self.user.GAMEMODE.get(gamemode, 'survival')
        self.user.dimension = self.user.DIMENSION.get(dimension, 'overworld')
        # Player's inventory.
        self.windows[0] = gui.Window(0, 'container', Message('inventory'), 45)
        # Needed to update user properties and metadata.
        self.entities[entity_id] = self.user
        self._dispatch('join')

    async def parse_0x1a(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Disconnect packet (0x1A)."""
        reason = protocol.read_chat(buffer)
        message = Message(reason)

        self._dispatch('disconnect', message)

    async def parse_0x0f(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Chat Message packet (0x0F)."""
        chat = protocol.read_chat(buffer)
        position = protocol.read_ubyte(buffer)

        message = Message(chat)
        message_type = {0: 'chat_message', 1: 'system_message', 2: 'action_bar'}.get(position)
        if message_type:
            self._dispatch(message_type, message)
        else:
            _logger.warning(f"Unknown chat Position: {position}, For message: {message}")

    async def parse_0x20(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Chunk Data packet (0x20)."""
        # Parse chunk metadata
        chunk_x = protocol.read_int(buffer)
        chunk_z = protocol.read_int(buffer)
        ground_up_continuous = protocol.read_bool(buffer)
        primary_bit_mask = protocol.read_varint(buffer)
        size = protocol.read_varint(buffer)
        chunk_buffer = protocol.read_byte_array(buffer, size)
        num_block_entities = protocol.read_varint(buffer)

        # Create and load chunk
        chunk = Chunk(math.Vector2D(chunk_x, chunk_z))
        chunk.load_chunk_column(ground_up_continuous, primary_bit_mask, chunk_buffer)

        # Process block entities
        for _ in range(num_block_entities):
            data = protocol.read_nbt(buffer)
            entity_pos = math.Vector3D(data.pop('x'), data.pop('y'), data.pop('z')).to_int()
            entity_id = data.pop('id')

            # Add block entity to appropriate chunk section
            chunk_coords, block_pos, section_y = self._get_position_components(entity_pos)
            section = chunk.get_section(section_y)

            if section is None:
                section = ChunkSection(math.Vector2D(0, 0))
                chunk.set_section(section_y, section)

            block_entity = self._create_block_entity(entity_id, data)
            section.set_entity(block_pos, block_entity)

        # Store chunk if loading is enabled
        if self._load_chunks:
            self.chunks[math.Vector2D(chunk_x, chunk_z)] = chunk

        self._dispatch('chunk_load', chunk)

    async def parse_0x1d(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Unload Chunk packet (0x1D)."""
        chunk_x = protocol.read_int(buffer)
        chunk_z = protocol.read_int(buffer)
        pos = math.Vector2D(chunk_x, chunk_z)

        # Remove chunk from memory if loading is enabled
        if self._load_chunks:
            self.chunks.pop(pos, None)

        self._dispatch('chunk_unload', pos)

    async def parse_0x0b(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Block Change packet (0x0B)."""
        position = protocol.read_position(buffer)
        block_state_id = protocol.read_varint(buffer)

        # Extract block type and metadata
        block_type = block_state_id >> 4
        block_meta = block_state_id & 0xF

        state = Block(block_type, block_meta, math.Vector3D(*position).to_int())

        if self._load_chunks:
            self.set_block_state(state)

        self._dispatch('block_change', state)

    async def parse_0x10(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Multi Block Change packet (0x10)."""
        chunk_x = protocol.read_int(buffer)
        chunk_z = protocol.read_int(buffer)
        record_count = protocol.read_varint(buffer)

        states = []

        for _ in range(record_count):
            horizontal = protocol.read_ubyte(buffer)
            y = protocol.read_ubyte(buffer)
            block_state_id = protocol.read_varint(buffer)

            # Extract relative coordinates within chunk
            rel_x = (horizontal >> 4) & 0x0F
            rel_z = horizontal & 0x0F

            # Calculate absolute world coordinates
            x = (chunk_x * 16) + rel_x
            z = (chunk_z * 16) + rel_z

            # Extract block type and metadata
            block_type = block_state_id >> 4
            block_meta = block_state_id & 0xF

            state = Block(block_type, block_meta, math.Vector3D(x, y, z).to_int())

            if self._load_chunks:
                self.set_block_state(state)

            states.append(state)

        self._dispatch('multi_block_change', states)

    async def parse_0x09(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Update Block Entity packet (0x09)."""
        # Parse packet data
        _ = protocol.read_position(buffer)
        _ = protocol.read_ubyte(buffer)
        data = protocol.read_nbt(buffer)

        # Extract position and entity ID from NBT
        pos = math.Vector3D(data.pop('x'), data.pop('y'), data.pop('z'))
        entity_id = data.pop('id')

        block_entity = self._create_block_entity(entity_id, data)
        if self._load_chunks:
            self.set_block_entity(pos.to_int(), block_entity)

        self._dispatch('block_entity_update', pos, block_entity)

    # USER
    async def parse_0x41(self, data: protocol.ProtocolBuffer) -> None:
        """Update Health (Packet ID: 0x41)"""
        self.user.health = protocol.read_float(data)
        self.user.food = protocol.read_varint(data)
        self.user.food_saturation = protocol.read_float(data)
        self._dispatch('player_health_update', self.user.health, self.user.food, self.user.food_saturation)

    async def parse_0x40(self, data: protocol.ProtocolBuffer) -> None:
        """Set Experience (Packet ID: 0x40)"""
        self.user.experience_bar = protocol.read_float(data)
        self.user.level = protocol.read_varint(data)
        self.user.total_experience = protocol.read_varint(data)
        self._dispatch('player_experience_set', self.user.level, self.user.total_experience, self.user.experience_bar)


    async def parse_0x3a(self, data: protocol.ProtocolBuffer) -> None:
        """
        Held Item Change (Packet ID: 0x3A)

        Sent by the server to update which hotbar slot the player has selected.
        """
        self.user.held_slot = protocol.read_byte(data)
        self._dispatch('held_slot_change', self.user.held_slot)

    async def parse_0x1e(self, data: protocol.ProtocolBuffer) -> None:
        """
        Change Game State (Packet ID: 0x1E)

        Reason codes:
            0: Invalid Bed
            1: End Raining
            2: Begin Raining
            3: Change Gamemode (0=Survival, 1=Creative, 2=Adventure, 3=Spectator)
            4: Exit End (0=No credits, 1=Show credits)
            5: Demo Message (101=Move, 102=Jump, 103=Inventory)
            6: Arrow hitting player
            7: Fade value (1=Dark, 0=Bright)
            8: Fade time (in ticks)
            10: Elder Guardian effect
        """
        reason = protocol.read_ubyte(data)
        value = protocol.read_float(data)

        if reason == 3:
            self.user.gamemode = self.user.GAMEMODE.get(int(value), 'survival')

        self._dispatch('game_state_change', reason, value)

    async def parse_0x2f(self, data: protocol.ProtocolBuffer) -> None:
        """
        Player Position and Look (Packet ID: 0x2F)

        Sent by the server to update the player's position and rotation.
        Also closes the "Downloading Terrain" screen after join/respawn.

        Fields:
            - X, Y, Z: Position (absolute or relative depending on flags)
            - Yaw, Pitch: Rotation (absolute or relative depending on flags)
            - Flags: Bit field
                0x01 = relative X
                0x02 = relative Y
                0x04 = relative Z
                0x08 = relative Yaw
                0x10 = relative Pitch
            - Teleport ID: must be acknowledged with a Teleport Confirm packet
        """
        x = protocol.read_double(data)
        y = protocol.read_double(data)
        z = protocol.read_double(data)
        yaw = protocol.read_float(data)
        pitch = protocol.read_float(data)
        flags = protocol.read_ubyte(data)
        teleport_id = protocol.read_varint(data)

        if flags & 0x01:  # relative X
            x += self.user.position.x
        if flags & 0x02:  # relative Y
            y += self.user.position.y
        if flags & 0x04:  # relative Z
            z += self.user.position.z
        if flags & 0x08:  # relative Yaw
            yaw += self.user.rotation.yaw
        if flags & 0x10:  # relative Pitch
            pitch += self.user.rotation.pitch

        self.user.position = math.Vector3D(x, y, z)
        self.user.rotation = math.Rotation(yaw, pitch)

        # Teleport Confirmation.
        await self.send_packet(0x00, protocol.write_varint(teleport_id))
        self._dispatch('player_position_and_look', self.user.position, self.user.rotation)

    async def parse_0x46(self, data: protocol.ProtocolBuffer) -> None:
        """
        Spawn Position (Packet ID: 0x46)

        Sent by the server to set the spawn location (where players respawn and compasses point to).
        Can be sent at any time to update the compass target.
        """
        x, y, z = protocol.read_position(data)
        self.user.spawn_point = math.Vector3D(x, y, z)
        self._dispatch('spawn_position', self.user.spawn_point)

    async def parse_0x35(self, data: protocol.ProtocolBuffer) -> None:
        """
        Respawn (Packet ID: 0x35)

        Sent by the server to change the player's dimension.

        Fields:
            Dimension (Int): -1=Nether, 0=Overworld, 1=End
            Difficulty (Unsigned Byte): 0=Peaceful, 1=Easy, 2=Normal, 3=Hard
            Gamemode (Unsigned Byte): 0=Survival, 1=Creative, 2=Adventure, 3=Spectator
            Level Type (String): World generation type, e.g. "default"

        Notes:
            Avoid respawning the player in the same dimension unless they are dead.
            To force a respawn in the same dimension, send two respawn packets: one to a different dimension,
            then the desired one.
        """
        dimension = protocol.read_int(data)
        difficulty = protocol.read_ubyte(data)
        gamemode = protocol.read_ubyte(data)
        level_type = protocol.read_string(data)

        self.user.dimension = self.user.DIMENSION.get(dimension, 'overworld')
        self.server_difficulty = difficulty
        self.user.gamemode = self.user.GAMEMODE.get(gamemode, 'survival')
        self.server_world_type = level_type

        self._dispatch('respawn', dimension, difficulty, gamemode, level_type)

    async def parse_0x25(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity (Packet ID: 0x25)"""
        entity_id = protocol.read_varint(buffer)

        if entity_id in self.entities:
            self._dispatch('entity_keep_alive', self.entities[entity_id])
        else:
            _logger.warning(f"Entity keep-alive received for untracked entity ID {entity_id}")

    async def parse_0x2a(self, buffer: protocol.ProtocolBuffer) -> None:
        """Open Sign Editor (Packet ID: 0x2A)"""
        location = protocol.read_position(buffer)
        self._dispatch('open_sign_editor', math.Vector3D(*location))

    async def parse_0x2d(self, buffer: protocol.ProtocolBuffer) -> None:
        """Combat Event (Packet ID: 0x2D)"""
        event = protocol.read_varint(buffer)

        if event == 0:
            self._dispatch('enter_combat')
        elif event == 1:
            duration = protocol.read_varint(buffer)
            entity_id = protocol.read_int(buffer)
            entity = self.entities.get(entity_id)

            if not entity:
                _logger.warning(f"Combat ended for untracked entity {entity_id}")
                return

            self._dispatch('end_combat', entity, duration)
        elif event == 2:
            player_id = protocol.read_varint(buffer)
            entity_id = protocol.read_int(buffer)
            message = protocol.read_chat(buffer)

            player = self.entities.get(player_id)
            entity = self.entities.get(entity_id)

            if not player:
                _logger.warning(f"Entity death for untracked player {player_id}")
                return

            if not entity:
                _logger.warning(f"Entity death for untracked entity {entity_id}")
                return

            self._dispatch('player_death', player, entity, Message(message))

    async def parse_0x2e(self, buffer: protocol.ProtocolBuffer) -> None:
        """Player List Item (Packet ID: 0x2E)"""
        action = protocol.read_varint(buffer)
        number_of_players = protocol.read_varint(buffer)

        players_affected = []

        for _ in range(number_of_players):
            player_uuid = protocol.read_uuid(buffer)
            uuid_str = str(player_uuid)

            if action == 0:  # add player
                name = protocol.read_string(buffer, 16)
                number_of_properties = protocol.read_varint(buffer)

                properties = []
                for _ in range(number_of_properties):
                    property_name = protocol.read_string(buffer, 32767)
                    value = protocol.read_string(buffer, 32767)
                    is_signed = protocol.read_bool(buffer)
                    signature = protocol.read_string(buffer, 32767) if is_signed else None
                    properties.append(tab.Property(property_name, value, signature))

                gamemode = protocol.read_varint(buffer)
                ping = protocol.read_varint(buffer)
                has_display_name = protocol.read_bool(buffer)
                display_name = Message(protocol.read_chat(buffer)) if has_display_name else None

                player = tab.TabPlayer(
                    name=name,
                    properties=properties,
                    gamemode=gamemode,
                    ping=ping,
                    display_name=display_name
                )
                self.tablist[uuid_str] = player
                players_affected.append(player)

            elif action == 1:  # update gamemode
                gamemode = protocol.read_varint(buffer)
                if uuid_str in self.tablist:
                    player = self.tablist[uuid_str]
                    player.gamemode = gamemode
                    players_affected.append(player)

            elif action == 2:  # update latency
                ping = protocol.read_varint(buffer)
                if uuid_str in self.tablist:
                    player = self.tablist[uuid_str]
                    player.ping = ping
                    players_affected.append(player)

            elif action == 3:  # update display name
                has_display_name = protocol.read_bool(buffer)
                display_name = protocol.read_chat(buffer) if has_display_name else None
                if uuid_str in self.tablist:
                    player = self.tablist[uuid_str]
                    player.display_name = display_name
                    players_affected.append(player)

            elif action == 4:  # remove player
                if uuid_str in self.tablist:
                    player = self.tablist[uuid_str]
                    del self.tablist[uuid_str]
                    players_affected.append(player)

        if players_affected:
            action_names = {
                0: 'players_add',
                1: 'players_gamemode_update',
                2: 'players_ping_update',
                3: 'players_display_name_update',
                4: 'players_remove'
            }
            event_name = action_names.get(action)
            if event_name:
                self._dispatch(event_name, players_affected)

    async def parse_0x05(self, buffer: protocol.ProtocolBuffer) -> None:
        """Spawn Player (Packet ID: 0x05)"""
        entity_id = protocol.read_varint(buffer)
        player_uuid = protocol.read_uuid(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        yaw = protocol.read_angle(buffer)
        pitch = protocol.read_angle(buffer)
        metadata = protocol.read_entity_metadata(buffer)
        player = entities.player.Player(entity_id, player_uuid, math.Vector3D(x, y, z), math.Rotation(yaw, pitch),
                                        metadata, self.tablist)
        self.entities[entity_id] = player
        self._dispatch('spawn_player', player)

    async def parse_0x4e(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Properties (Packet ID: 0x4E)"""
        entity_id = protocol.read_varint(buffer)
        num_properties = protocol.read_int(buffer)

        properties = {}
        for _ in range(num_properties):
            key = protocol.read_string(buffer, max_length=64)
            value = protocol.read_double(buffer)
            num_modifiers = protocol.read_varint(buffer)

            modifiers = {}
            for _ in range(num_modifiers):
                modifier_uuid = protocol.read_uuid(buffer)
                amount = protocol.read_double(buffer)
                operation = protocol.read_byte(buffer)
                modifiers[modifier_uuid] = {'amount': amount, 'operation': operation}
            properties[key] = {'value': value, 'modifiers': modifiers}

        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.update_properties(properties)
            self._dispatch('entity_properties', entity, properties)
        else:
            _logger.warning(f"Unknown entity ID: '{entity_id}', with properties: {properties}")

    async def parse_0x4c(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Teleport (Packet ID: 0x4C)"""
        entity_id = protocol.read_varint(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        yaw = protocol.read_angle(buffer)
        pitch = protocol.read_angle(buffer)
        on_ground = protocol.read_bool(buffer)

        if entity_id in self.entities:
            self.entities[entity_id].position = math.Vector3D(x, y, z)
            self.entities[entity_id].rotation = math.Rotation(yaw, pitch)
            self._dispatch('entity_teleport', self.entities[entity_id], on_ground)

    async def parse_0x29(self, buffer: protocol.ProtocolBuffer) -> None:
        """Vehicle Move (Packet ID: 0x29)"""
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        yaw = protocol.read_float(buffer)
        pitch = protocol.read_float(buffer)


        self._dispatch('vehicle_move', math.Vector3D(x, y, z), math.Rotation(yaw, pitch))

    async def parse_0x26(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Relative Move (Packet ID: 0x26)"""
        entity_id = protocol.read_varint(buffer)
        delta_x = protocol.read_short(buffer)
        delta_y = protocol.read_short(buffer)
        delta_z = protocol.read_short(buffer)
        on_ground = protocol.read_bool(buffer)

        delta = math.Vector3D(delta_x / 4096.0, delta_y / 4096.0, delta_z / 4096.0)

        # Update entity if it exists
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            current_pos = entity.position

            # Apply relative movement
            new_x = current_pos.x + delta.x
            new_y = current_pos.y + delta.y
            new_z = current_pos.z + delta.z

            entity.position = math.Vector3D(new_x, new_y, new_z)
            self._dispatch('entity_move', entity, delta, on_ground)

    async def parse_0x27(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Look And Relative Move (Packet ID: 0x27)"""
        entity_id = protocol.read_varint(buffer)
        delta_x_raw = protocol.read_short(buffer)  # Change in position * 4096
        delta_y_raw = protocol.read_short(buffer)
        delta_z_raw = protocol.read_short(buffer)
        yaw = protocol.read_angle(buffer)  # Absolute yaw
        pitch = protocol.read_angle(buffer)  # Absolute pitch
        on_ground = protocol.read_bool(buffer)

        # Convert raw delta values to actual coordinate changes
        delta_x = delta_x_raw / 4096.0
        delta_y = delta_y_raw / 4096.0
        delta_z = delta_z_raw / 4096.0

        delta = math.Vector3D(delta_x, delta_y, delta_z)

        # Update entity if it exists
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            current_pos = entity.position

            # Apply relative movement
            new_x = current_pos.x + delta.x
            new_y = current_pos.y + delta.y
            new_z = current_pos.z + delta.z

            entity.position = math.Vector3D(new_x, new_y, new_z)
            entity.rotation = math.Rotation(yaw, pitch)

            self._dispatch('entity_move_look', entity, delta, on_ground)

    async def parse_0x28(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Look (Packet ID: 0x28)"""
        entity_id = protocol.read_varint(buffer)
        yaw = protocol.read_angle(buffer)
        pitch = protocol.read_angle(buffer)
        on_ground = protocol.read_bool(buffer)

        # Update entity if it exists
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.rotation = math.Rotation(yaw, pitch)
            self._dispatch('entity_look', entity, on_ground)

    async def parse_0x36(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Head Look (Packet ID: 0x36)"""
        entity_id = protocol.read_varint(buffer)
        head_yaw = protocol.read_angle(buffer)

        # Update entity if it exists
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.rotation.yaw = head_yaw
            self._dispatch('entity_head_look', entity)

    async def parse_0x03(self, buffer: protocol.ProtocolBuffer) -> None:
        """Spawn Mob (Packet ID: 0x03)"""
        entity_id = protocol.read_varint(buffer)
        entity_uuid = protocol.read_uuid(buffer)
        mob_type = protocol.read_varint(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        yaw = protocol.read_angle(buffer)
        pitch = protocol.read_angle(buffer)
        head_pitch = protocol.read_angle(buffer)
        # Entity Velocity
        _ = protocol.read_short(buffer)
        _ = protocol.read_short(buffer)
        _ = protocol.read_short(buffer)
        metadata = protocol.read_entity_metadata(buffer)

        mob_entity = self._create_mob_entity(mob_type, entity_id, entity_uuid, math.Vector3D(x, y, z),
                                             math.Rotation(yaw, pitch), metadata)
        self.entities[entity_id] = mob_entity
        self._dispatch('spawn_mob', mob_entity, math.Rotation(0, head_pitch))


    async def parse_0x3e(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Velocity (Packet ID: 0x3E)"""
        entity_id = protocol.read_varint(buffer)
        velocity_x = protocol.read_short(buffer) / 8000.0 * 20
        velocity_y = protocol.read_short(buffer) / 8000.0 * 20
        velocity_z = protocol.read_short(buffer) / 8000.0 * 20

        if entity_id in self.entities:
            velocity = math.Vector3D(velocity_x, velocity_y, velocity_z)
            self._dispatch('entity_velocity', self.entities[entity_id], velocity)

    async def parse_0x3c(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Metadata (Packet ID: 0x3C)"""
        entity_id = protocol.read_varint(buffer)
        metadata = protocol.read_entity_metadata(buffer)

        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.update_metadata(metadata)
            self._dispatch('entity_metadata', entity, metadata)

    async def parse_0x3f(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Equipment (Packet ID: 0x3F)"""
        entity_id = protocol.read_varint(buffer)
        slot = protocol.read_varint(buffer)
        item = protocol.read_slot(buffer)

        """if entity_id in self.entities:
            print('entity_equipment',  self.entities[entity_id], slot, item)"""


    async def parse_0x32(self, buffer: protocol.ProtocolBuffer) -> None:
        """Destroy Entities (Packet ID: 0x32)"""
        count = protocol.read_varint(buffer)
        entity_ids = [protocol.read_varint(buffer) for _ in range(count)]
        destroyed = {eid: self.entities.pop(eid, None) for eid in entity_ids if eid in self.entities}

        if destroyed:
            self._dispatch('destroy_entities', list(destroyed.values()))

    async def parse_0x1b(self, buffer: protocol.ProtocolBuffer) -> None:
        """Entity Status (Packet ID: 0x1B)"""
        entity_id = protocol.read_int(buffer)
        status = protocol.read_byte(buffer)

        if entity_id in self.entities:
            self._dispatch('entity_status', entity_id, status)
        else:
            _logger.warning(f"Unknown entity ID: '{entity_id}', with status: {status}")

    # Object
    async def parse_0x00(self, buffer: protocol.ProtocolBuffer) -> None:
        """Spawn Object (Packet ID: 0x00)"""
        entity_id = protocol.read_varint(buffer)
        entity_uuid = protocol.read_uuid(buffer)
        obj_type = protocol.read_byte(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        pitch = protocol.read_angle(buffer)
        yaw = protocol.read_angle(buffer)
        data = protocol.read_int(buffer)
        # 20 ticks.
        vel_x = protocol.read_short(buffer) / 8000.0 * 20
        vel_y = protocol.read_short(buffer) / 8000.0 * 20
        vel_z = protocol.read_short(buffer) / 8000.0 * 20

        velocity = math.Vector3D(vel_x, vel_y, vel_z)
        entity = self._create_object_entity(obj_type, entity_id, entity_uuid, math.Vector3D(x, y, z),
                                             math.Rotation(yaw, pitch), data)
        self.entities[entity_id] = entity
        self._dispatch('spawn_object', entity, velocity)


    async def parse_0x04(self, buffer: protocol.ProtocolBuffer) -> None:
        """Spawn Painting (Packet ID: 0x04)"""
        entity_id = protocol.read_varint(buffer)
        entity_uuid = protocol.read_uuid(buffer)
        title = protocol.read_string(buffer, max_length=13)
        position = protocol.read_position(buffer)
        direction = protocol.read_byte(buffer)

        entity = self._create_object_entity(83, entity_id, entity_uuid, math.Vector3D(*position),
                                            math.Rotation(0, 0), direction)
        entity.set_painting_type(title)
        self.entities[entity_id] = entity
        self._dispatch('spawn_painting', entity)

    async def parse_0x47(self, buffer: protocol.ProtocolBuffer) -> None:
        """Time Update (Packet ID: 0x47)"""
        world_age = protocol.read_long(buffer)
        time_of_day = protocol.read_long(buffer)
        self.server_world_age = world_age
        self.server_time_of_day = time_of_day

        self._dispatch('time_update', world_age, time_of_day)


    async def parse_0x02(self, buffer: protocol.ProtocolBuffer) -> None:
        """Spawn Global Entity (Packet ID: 0x02)"""
        entity_id = protocol.read_varint(buffer)
        entity_type = protocol.read_byte(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)

        entity = self._create_object_entity(200, entity_id, '00000000-0000-0000-0000-000000000000',
                                            math.Vector3D(x, y, z),
                                            math.Rotation(0, 0), entity_type)
        self._dispatch('spawn_global_entity', entity)

    async def parse_0x01(self, buffer: protocol.ProtocolBuffer) -> None:
        """Spawn Experience Orb (Packet ID: 0x01)"""
        entity_id = protocol.read_varint(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        count = protocol.read_short(buffer)

        entity = self._create_object_entity(69, entity_id, '00000000-0000-0000-0000-000000000000',
                                            math.Vector3D(x, y, z),
                                            math.Rotation(0, 0), count)
        self.entities[entity_id] = entity
        self._dispatch('spawn_experience_orb', entity)

    async def parse_0x11(self, buffer: protocol.ProtocolBuffer) -> None:
        """Confirm Transaction (Packet ID: 0x11)"""
        window_id = protocol.read_byte(buffer)
        action_number = protocol.read_short(buffer)
        accepted = protocol.read_bool(buffer)
        await self.send_confirm_transaction(window_id, action_number, accepted)
        self._dispatch('transaction_confirmed', window_id, action_number, accepted)

    async def parse_0x12(self, buffer: protocol.ProtocolBuffer) -> None:
        """Close Window (Packet ID: 0x12)"""
        window_id = protocol.read_ubyte(buffer)

        if window_id in self.windows:
            del self.windows[window_id]

        self._dispatch('window_closed', window_id)

    async def parse_0x13(self, buffer: protocol.ProtocolBuffer) -> None:
        """Open Window (Packet ID: 0x13)"""
        window_id = protocol.read_ubyte(buffer)
        window_type = protocol.read_string(buffer, max_length=32)
        window_title = protocol.read_chat(buffer)
        number_of_slots = protocol.read_ubyte(buffer)

        window = gui.Window(window_id, window_type, Message(window_title), number_of_slots)

        if window_type == 'EntityHorse':
            # Custom property.
            entity_id = protocol.read_int(buffer)
            window.set_property(-1, entity_id)

        self.windows[window_id] = window
        self._dispatch('window_opened', window)

    async def parse_0x14(self, buffer: protocol.ProtocolBuffer) -> None:
        """Window Items (Packet ID: 0x14)"""
        window_id = protocol.read_ubyte(buffer)
        count = protocol.read_short(buffer)

        if window_id not in self.windows:
            window = gui.Window(window_id, 'container', Message('inventory'), count)
            self.windows[window_id] = window
            return

        window = self.windows[window_id]

        for i in range(count):
            slot_data = protocol.read_slot(buffer)
            if slot_data is not None:
                window.set_slot(i, slot_data)

        self._dispatch('window_items_updated', window)

    async def parse_0x15(self, buffer: protocol.ProtocolBuffer) -> None:
        """Window Property (Packet ID: 0x15)"""
        window_id = protocol.read_ubyte(buffer)
        property_id = protocol.read_short(buffer)
        value = protocol.read_short(buffer)

        if window_id not in self.windows:
            _logger.warning(
                f"Received property update for unknown window ID: {window_id} (property: {property_id},"
                f" value: {value})")
            return

        window = self.windows[window_id]
        window.set_property(property_id, value)
        self._dispatch('window_property_changed', window, property_id, value)

    async def parse_0x16(self, buffer: protocol.ProtocolBuffer) -> None:
        """Set Slot (Packet ID: 0x16)"""
        window_id = protocol.read_byte(buffer)
        slot_index = protocol.read_short(buffer)
        slot_data = protocol.read_slot(buffer)

        # Handle special window IDs
        if window_id == -1:
            # Cursor slot (dragged item)
            self._dispatch('cursor_slot_changed', slot_data)
        elif window_id == -2:
            if 0 in self.windows:
                updated_slot = self.windows[0].set_slot(slot_index, slot_data)
                self._dispatch('inventory_slot_changed', updated_slot)
            else:
                _logger.warning("Received inventory update but no player inventory window found")
        else:
            # Regular window slot update
            if window_id not in self.windows:
                _logger.warning(f"Received slot update for unknown window ID: {window_id} (slot: {slot_index})")
                return

            window = self.windows[window_id]
            updated_slot = window.set_slot(slot_index, slot_data)
            self._dispatch('window_slot_changed', window, updated_slot)