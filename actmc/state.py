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
from .chunk import *
from .user import User
import asyncio

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Literal, Optional, Tuple
    from .gateway import MinecraftSocket
    from .tcp import TcpClient

import logging
_logger = logging.getLogger(__name__)


BLOCK_ENTITY_TYPES = {
    'minecraft:bed': entities.block.Bed,
    'minecraft:flower_pot': entities.block.FlowerPot,
    'minecraft:banner': entities.block.Banner,
    'minecraft:beacon': entities.block.Beacon,
    'minecraft:sign': entities.block.Sign,
    'minecraft:mob_spawner': entities.block.MobSpawner,
    'minecraft:skull': entities.block.Skull,
    'minecraft:structure_block': entities.block.StructureBlock,
    'minecraft:end_gateway': entities.block.EndGateway,
    'minecraft:shulker_box': entities.block.ShulkerBox
}

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

        # World state
        self.chunks: Dict[math.Vector2D, Chunk] = {}

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
                _logger.warning(f"Unknown block entity '{entity_id}' with data: {data}")
            return block_entity

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

    async def send_client_status(self, action_id: Literal[0, 1]) -> None:
        """
        Send a Client Status packet to the server.

        Args:
            action_id: Action to perform (0: respawn, 1: request statistics)
        """
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

        # Route message based on position type
        message_type = {0: 'chat_message', 1: 'system_message', 2: 'action_bar'}.get(position)
        if message_type:
            _logger.debug(f"Received {message_type}: {message}")
            self._dispatch(message_type, message)
        else:
            _logger.warning(f"Unknown chat position {position} for message: {message}")

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

        # Create block entity
        block_entity = self._create_block_entity(entity_id, data)

        # Update world state if chunk loading is enabled
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

        if not hasattr(self.user, 'position'):
            self.user.position = math.Vector3D(0.0, 0.0, 0.0)
        if not hasattr(self.user, 'rotation'):
            self.user.rotation = math.Rotation(0.0, 0.0)

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

        # Teleport Confirm
        await self.send_packet(0x00, protocol.write_varint(teleport_id))
        self._dispatch('player_position_and_look', self.user.position, self.user.rotation)
