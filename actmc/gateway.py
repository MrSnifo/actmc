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
from . import protocol
import asyncio
import zlib

if TYPE_CHECKING:
    from typing import Self, ClassVar, Tuple
    from .state import ConnectionState
    from .client import Client

import logging
_logger = logging.getLogger(__name__)


class MinecraftSocket:
    """Minecraft protocol socket implementation."""

    KEEP_ALIVE_SERVERBOUND: ClassVar[int] = 0x0B
    KEEP_ALIVE_CLIENTBOUND: ClassVar[int] = 0x1F
    SET_COMPRESSION: ClassVar[int] = 0x03
    LOGIN_SUCCESS: ClassVar[int] = 0x02

    __slots__ = ('reader', 'writer', 'compression_threshold', 'phase', '_state')

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, state: ConnectionState) -> None:
        self.reader: asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer

        self.compression_threshold: int = -1
        self.phase: int = 0

        self._state: ConnectionState = state

    @classmethod
    async def initialize_socket(cls, client: Client, state: ConnectionState) -> Self:
        """Factory method to create and initialize a socket connection. """
        connection = await client.tcp.connect()
        gateway = cls(*connection, state=state)

        _logger.info("Socket connection established successfully")
        return gateway

    async def _read_varint_async(self) -> int:
        """Asynchronously read a variable-length integer from the stream."""
        data = bytearray()

        for _ in range(5):
            byte = await self.reader.readexactly(1)
            data.append(byte[0])

            # Check if this is the last byte (MSB not set)
            if not (byte[0] & 0x80):
                break
        else:
            raise ValueError("VarInt exceeds maximum length")

        buffer = protocol.ProtocolBuffer(data)
        return protocol.read_varint(buffer)

    @staticmethod
    def _varint_size(value: int) -> int:
        """Calculate the byte size required for a VarInt encoding."""
        if value == 0:
            return 1

        size = 0
        while value:
            size += 1
            value >>= 7

        return size

    async def read_packet(self) -> Tuple[int, bytes]:
        """Read and parse a complete Minecraft protocol packet."""
        packet_length = await self._read_varint_async()
        body = await self.reader.readexactly(packet_length)
        buffer = protocol.ProtocolBuffer(body)

        if self.compression_threshold >= 0:
            uncompressed_length = protocol.read_varint(buffer)
            if uncompressed_length > 0:
                compressed_data = buffer.read(buffer.remaining())
                try:
                    body = zlib.decompress(compressed_data)
                except zlib.error as e:
                    raise ValueError(f"Packet decompression failed: {e}") from e
                if len(body) != uncompressed_length:
                    raise ValueError(
                        f"Decompressed packet length mismatch: "
                        f"expected {uncompressed_length}, got {len(body)}"
                    )
                buffer = protocol.ProtocolBuffer(body)
        packet_id = protocol.read_varint(buffer)
        data = buffer.read(buffer.remaining())

        return packet_id, data

    async def write_packet(self, packet_id: int, data: bytes) -> None:
        """Write a complete Minecraft protocol packet."""
        packet_id_bytes = protocol.write_varint(packet_id)
        payload = packet_id_bytes + data
        payload_length = len(payload)

        body_buffer = protocol.ProtocolBuffer()
        if self.compression_threshold >= 0:
            if payload_length >= self.compression_threshold:
                compressed_data = zlib.compress(payload)
                body_buffer.write(protocol.write_varint(payload_length))
                body_buffer.write(compressed_data)
            else:
                body_buffer.write(protocol.write_varint(0))
                body_buffer.write(payload)
        else:
            body_buffer.write(payload)

        body = body_buffer.getvalue()
        self.writer.write(protocol.write_varint(len(body)))
        self.writer.write(body)
        await self.writer.drain()
        _logger.debug("Sent packet 0x%s", f"{packet_id:02X}")

    async def poll(self) -> None:
        """Poll for and handle incoming packets."""
        packet_id, data = await self.read_packet()
        buffer = protocol.ProtocolBuffer(data)

        _logger.trace(f"Processing packet ID 0x{packet_id:02X}")  # type: ignore

        # Handle keep-alive packets
        if packet_id == self.KEEP_ALIVE_CLIENTBOUND:
            await self._keep_alive(buffer)
            return

        # PLAY STATE: 6.
        if self.phase != 6:
            if packet_id == self.SET_COMPRESSION:
                await self._compression_setup(buffer)
                return

            if packet_id == self.LOGIN_SUCCESS:
                await self._login_success(buffer)
                return

        await self._state.parse(packet_id, buffer)

    async def _keep_alive(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle server keep-alive packet."""
        keep_alive_id = protocol.read_long(buffer)
        await self.write_packet(self.KEEP_ALIVE_SERVERBOUND, protocol.pack_long(keep_alive_id))
        _logger.debug(f"Responded to keep-alive: %s", keep_alive_id)

    async def _compression_setup(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle compression setup packet during login."""
        threshold = protocol.read_varint(buffer)
        self.compression_threshold = threshold
        self.phase = 4
        _logger.info(f"Packet compression enabled with threshold %s", threshold)

    async def _login_success(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle successful login completion."""
        self._state.uid = protocol.read_string(buffer)
        self._state.username = protocol.read_string(buffer)
        self.phase = 6
        _logger.debug(f"Login successful for player %s (UUID: %s)", self._state.username, self._state.uid)