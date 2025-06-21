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

from typing import TYPE_CHECKING
from . import enums
from . import protocol
import asyncio
from .ui.chat import Message
from .chunk import Chunk, BlockState, ChunkSection, BlockEntity
from . import entity
from . import math
import time
if TYPE_CHECKING:
    from typing import Optional, Dict, Callable, Any, Tuple, Literal, List
    from .gateway import MinecraftSocket
    from .tcp import TcpClient


import logging
_logger = logging.getLogger(__name__)

__all__ = ('ConnectionState',)


class ConnectionState:
    """
    Manages the connection state and packet handling for a Minecraft client.

    This class handles packet parsing, sending, and maintains the connection state
    with improved performance through caching and optimized packet handling.
    """

    if TYPE_CHECKING:
        _get_socket: Callable[..., MinecraftSocket]

    _packet_parsers: Dict[int, str] = {}

    def __init__(self, tcp: TcpClient, dispatcher: Callable[..., Any]) -> None:
        self.tcp: TcpClient = tcp
        self._dispatch: Callable[..., Any] = dispatcher
        self._load_chunks: bool = True

        # Waiters.
        self._waiters: Dict[str, List[asyncio.Future]] = {}

        # Player
        self.player: Optional[entity.Player] = None

        # Server
        self.server_difficulty: Optional[int] = None
        self.server_max_players: Optional[int] = None
        self.server_world_type: Optional[int] = None

        # World
        self.chunks: Dict[math.Vector2D, Chunk] = {}

        # Parser mapping for better performance
        if not self._packet_parsers:
            self._build_parser_cache()

    @classmethod
    def _build_parser_cache(cls) -> None:
        """Build a cache of packet ID to parser method mapping."""
        for attr_name in dir(cls):
            if attr_name.startswith('parse_0x'):
                try:
                    packet_id = int(attr_name[8:], 16)
                    cls._packet_parsers[packet_id] = attr_name
                except ValueError:
                    continue

    async def _wait_for(self, event: str, timeout: Optional[float] = 30.0) -> Any:
        """Wait for an event, or return cached data if recent."""
        future = asyncio.Future()
        if event not in self._waiters:
            self._waiters[event] = []
        self._waiters[event].append(future)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            if event in self._waiters and future in self._waiters[event]:
                self._waiters[event].remove(future)
            raise asyncio.TimeoutError(f"Timed out waiting for {event}")

    def _trigger_event(self, event: str, data: Any = None) -> None:
        """Trigger the event: cache it and notify all current waiters."""
        if event in self._waiters:
            for future in self._waiters[event]:
                if not future.done():
                    future.set_result(data)
            self._waiters[event].clear()

    def _has_waiters(self, event: str) -> bool:
        return event in self._waiters and any(not f.done() for f in self._waiters[event])


    def _get_socket(self) -> Optional[MinecraftSocket]:
        """Get the socket - this method will be overridden by the Client class."""

    async def send_packet(self, packet_id: int, buffer: bytes) -> None:
        """Send a packet to the server with improved error handling."""
        socket = self._get_socket()
        if not socket:
            raise RuntimeError("Socket is not initialized or not connected.")

        await socket.write_packet(packet_id=packet_id, data=buffer)

    async def send_initial_packets(self, username: str) -> None:
        """Send initial handshake and login packets with better error handling."""
        handshake_packet = self.tcp.build_handshake_packet
        login_packet = self.tcp.build_login_packet(username)
        await self.send_packet(0x00, handshake_packet.getvalue())
        await self.send_packet(0x00, login_packet.getvalue())
        _logger.debug("Sent handshake and login packets.")

        # Potato pc safety.
        if self._load_chunks:
            _logger.warning("Chunk loading is enabled. May cause stutter and memory growth.")

        self._dispatch('handshake')

    # --------------------------------------+ Chunk +--------------------------------------
    @staticmethod
    def _get_position_components(position: math.Vector3D[int]) -> Tuple[math.Vector2D[int], math.Vector3D[int], int]:
        x, y, z = position
        chunk_x, rel_x = x >> 4, x & 0xF
        chunk_z, rel_z = z >> 4, z & 0xF
        section_y, rel_y = y // 16, y % 16
        return math.Vector2D(chunk_x, chunk_z), math.Vector3D(rel_x, rel_y, rel_z), section_y

    def get_block_state(self, position: math.Vector3D[int]) -> Optional[BlockState]:
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled.")

        chunk_cords, block_pos, section_y = self._get_position_components(position)
        chunk = self.chunks.get(chunk_cords)
        if chunk is None:
            return None

        section = chunk.get_section(section_y)
        if section is None:
            return None
        return section.get_state(block_pos)

    def set_block_state(self, state: BlockState) -> None:
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled.")

        chunk_cords, block_pos, section_y = self._get_position_components(state.position)
        chunk = self.chunks.get(chunk_cords)
        if chunk is None:
            return

        section = chunk.get_section(section_y)
        if section is None:
            section = ChunkSection(math.Vector2D(0, 0))
            chunk.set_section(section_y, section)
        section.set_state(block_pos, state)

    def set_block_entity(self, position: math.Vector3D[int], entity: BlockEntity) -> None:
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled.")

        chunk_cords, block_pos, section_y = self._get_position_components(position)
        chunk = self.chunks.get(chunk_cords)
        if chunk is None:
            return

        section = chunk.get_section(section_y)
        if section is None:
            section = ChunkSection(math.Vector2D(0, 0))
            chunk.set_section(section_y, section)
        section.set_entity(block_pos, entity)

    # -------------------------------------------------------------------------------
    # --------------------------------------+ Parser +--------------------------------------








    # --------------------------------------+ Parser +--------------------------------------
    def parse(self, packet_id: int, data: protocol.ProtocolBuffer) -> None:
        """Parse incoming packets"""
        try:
            parser_name = self._packet_parsers.get(packet_id)
            if parser_name:
                func = getattr(self, parser_name)
                func(data)

        except Exception as error:
            _logger.exception(f'Failed to parse packet 0x{packet_id:02X}: %s', error)
            self._dispatch('error', packet_id, error)

    def parse_0x02(self, data: protocol.ProtocolBuffer) -> None:
        """Login Success (Packet ID: 0x02)"""
        uuid = protocol.read_string(data)
        username = protocol.read_string(data)
        self.player = entity.Player(username=username, uuid=uuid)

    def parse_0x23(self, data: protocol.ProtocolBuffer) -> None:
        """Join Game (Packet ID: 0x23)"""
        # Player.
        entity_id = protocol.read_int(data)
        gamemode = enums.GameMode(protocol.read_ubyte(data)).name.lower()
        dimension = enums.Dimension(protocol.read_int(data)).name.lower()

        # Server.
        self.server_difficulty = enums.Difficulty(protocol.read_ubyte(data)).name.lower()
        self.server_max_players = protocol.read_ubyte(data)
        self.server_world_type = protocol.read_string(data).lower()

        # Update player state.
        self.player.update_login_state(entity_id, gamemode, dimension)
        self._dispatch('join')

    def parse_0x1a(self, data: protocol.ProtocolBuffer) -> None:
        """Disconnect (Packet ID: 0x1A)"""
        reason = protocol.read_chat(data)

        _logger.debug(f"0x1a - Parsing: {reason}")
        message = Message(reason)
        self._dispatch('disconnect', message)

    def parse_0x0f(self, data) -> None:
        """Handles Chat Message (Packet ID: 0x0F)"""
        chat = protocol.read_chat(data)
        position = protocol.read_ubyte(data)

        _logger.debug(f"0x0f - Parsing: {chat} with position {position}")
        message = Message(chat)
        message_types: Dict[int, str] = {
            0: 'chat_message',
            1: 'system_message',
            2: 'action_bar'
        }
        if position in message_types:
            self._dispatch(message_types[position], message)
        else:
            _logger.warning(f"0x0f - Unknown chat position {position} with message: {message}")

    async def send_client_status(self, action_id: Literal[0, 1]) -> None:
        """
        Send a Client Status packet to the server.

        Parameters
        ----------
        action_id: Literal[0, 1]
            The action to perform:
            - 0: Perform respawn
            - 1: Request statistics
        """
        await self.send_packet(0x03, protocol.write_varint(action_id))

    async def get_statistics(self) -> Dict[str, int] :
        if not self._has_waiters('0x07'):
            await self.send_client_status(1)
        result: Dict[str, int] = await self._wait_for('0x07')
        return result

    def parse_0x20(self, data: protocol.ProtocolBuffer) -> None:
        """Handles Chunk Data (Packet ID: 0x20)"""
        chunk_x = protocol.read_int(data)
        chunk_z = protocol.read_int(data)
        ground_up_continuous = protocol.read_bool(data)
        primary_bit_mask = protocol.read_varint(data)
        size = protocol.read_varint(data)
        chunk_data = protocol.read_byte_array(data, size)
        num_block_entities = protocol.read_varint(data)

        chunk = Chunk(math.Vector2D(chunk_x, chunk_z))
        chunk.load_chunk_column(ground_up_continuous, primary_bit_mask, chunk_data)

        for _ in range(num_block_entities):
            e = protocol.read_nbt(data)
            entity_pos = math.Vector3D(e.pop('x'), e.pop('y'), e.pop('z')).to_int()
            entity_id = e.pop('id')

            chunk_cords, block_pos, section_y = self._get_position_components(entity_pos)
            section = chunk.get_section(section_y)
            if section is None:
                section = ChunkSection(math.Vector2D(0, 0))
                chunk.set_section(section_y, section)
            section.set_entity(block_pos, BlockEntity(entity_id, nbt_data=e))

        if self._load_chunks:
            self.chunks[math.Vector2D(chunk_x, chunk_z)] = chunk

        self._dispatch('chunk_load', chunk)

    def parse_0x0b(self, data: protocol.ProtocolBuffer) -> None:
        """Block Change (Packet ID: 0x0B)"""
        position = protocol.read_position(data)
        block_state_id = protocol.read_varint(data)
        block_type = block_state_id >> 4
        block_meta = block_state_id & 0xF

        state = BlockState(block_type, block_meta, math.Vector3D(*position).to_int())

        if self._load_chunks:
            self.set_block_state(state)

        self._dispatch('block_change', state)

    def parse_0x07(self, data: protocol.ProtocolBuffer) -> None:
        """Statistics (Packet ID: 0x07)"""
        count = protocol.read_varint(data)
        stats = {}

        for _ in range(count):
            name = protocol.read_string(data)
            value = protocol.read_varint(data)
            stats[name] = value
        self._trigger_event('0x07', stats)

    def parse_0x10(self, data: protocol.ProtocolBuffer) -> None:
        """Multi Block Change (Packet ID: 0x10)"""
        chunk_x = protocol.read_int(data)
        chunk_z = protocol.read_int(data)
        record_count = protocol.read_varint(data)

        states = []

        for _ in range(record_count):
            horizontal = protocol.read_ubyte(data)
            y = protocol.read_ubyte(data)
            block_state_id = protocol.read_varint(data)

            # Extract relative coordinates in the chunk (0-15)
            rel_x = (horizontal >> 4) & 0x0F
            rel_z = horizontal & 0x0F

            # Absolute coordinates
            x = (chunk_x * 16) + rel_x
            z = (chunk_z * 16) + rel_z

            block_type = block_state_id >> 4
            block_meta = block_state_id & 0xF

            state = BlockState(block_type, block_meta, math.Vector3D(x, y, z).to_int())

            if self._load_chunks:
                 self.set_block_state(state)

            states.append(state)

        self._dispatch('multi_block_change', states)

    def parse_0x09(self, data: protocol.ProtocolBuffer) -> None:
        """Update Block Entity (Packet ID: 0x09)"""
        # Read packet data
        _ = protocol.read_position(data)
        action_id = protocol.read_ubyte(data)
        e = protocol.read_nbt(data)

        pos = math.Vector3D(e.pop('x'), e.pop('y'), e.pop('z') )
        entity_id = e.pop('id')

        e = BlockEntity(entity_id, nbt_data=e)

        # Get or create block state
        if self._load_chunks:
            self.set_block_entity(pos.to_int(), e)

        # Determine action name
        try:
            action_name = enums.BlockEntityAction(action_id).name.lower()
        except ValueError:
            _logger.warning(f"0x09 - Unknown BlockEntityAction ID: {action_id}")
            action_name = str(action_id)

        # Dispatch the event
        self._dispatch('block_entity_update', action_name, pos, entity)

    def parse_0x1d(self, data: protocol.ProtocolBuffer) -> None:
        """Unload Chunk (Packet ID: 0x1D)"""
        chunk_x = protocol.read_int(data)
        chunk_z = protocol.read_int(data)
        pos = math.Vector2D(chunk_x, chunk_z)

        if self._load_chunks:
            self.chunks.pop(pos, None)

        self._dispatch('chunk_unload', pos)
