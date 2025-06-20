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
from .enums import BlockEntityAction
from . import protocol
from .ui.chat import Message
from .chunk import Chunk, BlockState, ChunkSection, BlockEntity
from . import math
if TYPE_CHECKING:
    from typing import Optional, Dict, Callable, Any, Tuple
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

        # Player
        self.username: Optional[str] = None

        # World
        self.chunks: Dict[math.Vector2D, Chunk] = {}

        # Parser mapping for better performance
        if not self._packet_parsers:
            self._build_parser_cache()

    @staticmethod
    def _get_position_components(position: math.Vector3D[int]) -> Tuple[math.Vector2D[int], math.Vector3D[int], int]:

        x, y, z = position
        chunk_x, rel_x = x >> 4, x & 0xF
        chunk_z, rel_z = z >> 4, z & 0xF
        section_y, rel_y = y // 16, y % 16
        return math.Vector2D(chunk_x, chunk_z), math.Vector3D(rel_x, rel_y, rel_z), section_y

    def get_chunks(self, position: math.Vector3D[int]) -> Optional[Chunk]:
        """
        Get the chunk at the specified position.

        Parameters
        ----------
        position:math.Vector3D[int]
            The world position to get the chunk for

        Returns
        -------
        Optional[Chunk]
            The chunk at the position, or None if not loaded

        Raises
        ------
        RuntimeError
            If Chunk loading disabled.
        """
        if not self._load_chunks:
            raise RuntimeError("Chunk loading disabled.")
        chunk_cords, _, _ = self._get_position_components(position)
        return self.chunks.get(chunk_cords)

    def get_block_state(self, position: math.Vector3D[int]) -> Optional[BlockState]:
        """
        Get the block state at the specified world position.

        Parameters
        ----------
        position:math.Vector3D[int]
            The world position to get the block state for

        Returns
        -------
        Optional[BlockState]
            The block state at the position, or None if chunk/section not loaded

        Raises
        ------
        RuntimeError
            If Chunk loading disabled.
        """
        if not self._load_chunks:
            raise RuntimeError("Chunk loading disabled.")
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
            raise RuntimeError("Chunk loading disabled.")

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
            raise RuntimeError("Chunk loading disabled.")

        chunk_cords, block_pos, section_y = self._get_position_components(position)
        chunk = self.chunks.get(chunk_cords)
        if chunk is None:
            return

        section = chunk.get_section(section_y)
        if section is None:
            section = ChunkSection(math.Vector2D(0, 0))
            chunk.set_section(section_y, section)

        section.set_entity(block_pos, entity)



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

    def _get_socket(self) -> Optional[MinecraftSocket]:
        """Get the socket - this method will be overridden by the Client class."""

    async def send_packet(self, packet_id: int, buffer: protocol.ProtocolBuffer) -> None:
        """Send a packet to the server with improved error handling."""
        socket = self._get_socket()
        if not socket:
            raise RuntimeError("Socket is not initialized or not connected.")

        await socket.write_packet(packet_id=packet_id, data=buffer.getvalue())

    async def send_initial_packets(self) -> None:
        """Send initial handshake and login packets with better error handling."""
        handshake_packet = self.tcp.build_handshake_packet
        login_packet = self.tcp.build_login_packet(self.username)
        await self.send_packet(0x00, handshake_packet)
        await self.send_packet(0x00, login_packet)
        _logger.debug("Sent handshake and login packets.")

        # Potato pc safety.
        if self._load_chunks:
            _logger.warning("Chunk loading is enabled. May cause stutter and memory growth.")

        self._dispatch('handshake')

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

    def parse_0x23(self, data: protocol.ProtocolBuffer) -> None:
        """Join Game (Packet ID: 0x23)"""
        entity_id = protocol.read_int(data)
        gamemode = protocol.read_ubyte(data)
        dimension = protocol.read_int(data)
        difficulty = protocol.read_ubyte(data)
        max_players = protocol.read_ubyte(data)
        level_type = protocol.read_string(data)

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
        message_types = {
            0: 'chat_message',
            1: 'system_message',
            2: 'action_bar'
        }
        if position in message_types:
            self._dispatch(message_types[position], message)
        else:
            _logger.warning(f"0x0f - Unknown chat position {position} with message: {message}")

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
            block_entity = protocol.read_nbt(data)
            entity_pos = math.Vector3D(block_entity.pop('x'), block_entity.pop('y'), block_entity.pop('z')).to_int()
            entity_id = block_entity.pop('id')

            chunk_cords, block_pos, section_y = self._get_position_components(entity_pos)
            section = chunk.get_section(section_y)
            if section is None:
                section = ChunkSection(math.Vector2D(0, 0))
                chunk.set_section(section_y, section)
            section.set_entity(block_pos, BlockEntity(entity_id, nbt_data=block_entity))

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
        block_entity = protocol.read_nbt(data)

        pos = math.Vector3D(block_entity.pop('x'), block_entity.pop('y'), block_entity.pop('z') )
        entity_id = block_entity.pop('id')

        entity = BlockEntity(entity_id, nbt_data=block_entity)

        # Get or create block state
        if self._load_chunks:
            self.set_block_entity(pos.to_int(), entity)

        # Determine action name
        try:
            action_name = BlockEntityAction(action_id).name.lower()
        except ValueError:
            _logger.warning(f"0x09 - Unknown BlockEntityAction ID: {action_id}")
            action_name = str(action_id)

        # Dispatch the event
        self._dispatch('block_entity_update', action_name, pos, entity)

    def parse_0x1d(self, data: protocol.ProtocolBuffer) -> None:
        """Unload Chunk (Packet ID: 0x1D)"""
        chunk_x = protocol.read_int(data)
        chunk_z = protocol.read_int(data)
        position = math.Vector2D(chunk_x, chunk_z)

        if self._load_chunks:
            self.chunks.pop(position, None)

        self._dispatch('chunk_unload', position)
