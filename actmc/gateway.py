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

from .errors import ProtocolError, PacketError
from typing import TYPE_CHECKING
from . import protocol
import asyncio
import zlib

if TYPE_CHECKING:
    from .state import ConnectionState
    from typing import Self, Tuple
    from .client import Client

import logging
_logger = logging.getLogger(__name__)

__all__ = ('MinecraftSocket',)


class MinecraftSocket:
    """Minecraft protocol socket implementation with packet handling."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, state: ConnectionState) -> None:
        self.__reader: asyncio.StreamReader = reader
        self.__writer: asyncio.StreamWriter = writer
        self._state: ConnectionState = state
        self.phase: int = 0

    @classmethod
    async def initialize_socket(cls, client: Client, host: str, port: int, state: ConnectionState) -> Self:
        """Factory method to create and initialize a socket connection."""
        _logger.debug("Attempting to establish socket connection to %s:%s", host, port)
        reader, writer = await client.tcp.open_connection(host, port)
        client.tcp._writer = writer
        gateway = cls(reader=reader, writer=writer, state=state)
        _logger.debug("Socket connection established successfully")
        await state.send_initial_packets(host, port)
        return gateway

    async def _read_varint_async(self) -> int:
        """Asynchronously read a variable-length integer from the stream."""
        data = bytearray()

        for _ in range(5):
            byte = await self.__reader.readexactly(1)
            data.append(byte[0])

            if not (byte[0] & 0x80):
                break
        else:
            raise ProtocolError("VarInt exceeds maximum length")

        buffer = protocol.ProtocolBuffer(data)
        return protocol.read_varint(buffer)

    def _decompress_payload(self, payload: bytes) -> bytes:
        """Decompress packet payload if compression is enabled."""
        if self._state.tcp.compression_threshold < 0:
            return payload

        buffer = protocol.ProtocolBuffer(payload)
        uncompressed_length = protocol.read_varint(buffer)

        if uncompressed_length > 0:
            compressed_data = buffer.read(buffer.remaining())
            try:
                decompressed_data = zlib.decompress(compressed_data)
            except zlib.error as e:
                raise PacketError(f"Packet decompression failed: {e}") from e

            if len(decompressed_data) != uncompressed_length:
                raise PacketError(
                    f"Decompressed packet length mismatch: "
                    f"expected {uncompressed_length}, got {len(decompressed_data)}"
                )
            return decompressed_data
        else:
            return buffer.read(buffer.remaining())

    async def read_packet(self) -> Tuple[int, bytes]:
        """Read and parse a complete Minecraft protocol packet."""
        packet_length = await self._read_varint_async()
        # Direct access to cached StreamReader
        body = await self.__reader.readexactly(packet_length)
        body = self._decompress_payload(body)
        buffer = protocol.ProtocolBuffer(body)
        packet_id = protocol.read_varint(buffer)
        data = buffer.read(buffer.remaining())
        return packet_id, data

    async def poll(self) -> None:
        """Poll for and handle incoming packets."""
        packet_id, data = await self.read_packet()
        buffer = protocol.ProtocolBuffer(data)
        _logger.trace(f"Processing packet ID 0x{packet_id:02X}")  # type: ignore

        if packet_id == 0x1F:
            await self._handle_keep_alive(buffer)
            return

        if self.phase != 6:
            if packet_id == 0x03:
                await self._handle_compression_setup(buffer)
                return

            if packet_id == 0x02:
                await self._handle_login_success(buffer)
                return

        await self._state.parse(packet_id, buffer)

    async def _handle_keep_alive(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle server keep-alive packet."""
        await self._state.tcp.write_packet(0x0B, buffer)
        _logger.debug("Sent keep-alive response")

    async def _handle_compression_setup(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle compression setup packet during login."""
        threshold = protocol.read_varint(buffer)
        self._state.tcp.compression_threshold = threshold
        self.phase = 4
        _logger.debug(f"Packet compression enabled with threshold {threshold}")

    async def _handle_login_success(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle successful login completion."""
        self._state.uid = protocol.read_string(buffer)
        self._state.username = protocol.read_string(buffer)
        self.phase = 6
        _logger.debug(f"Login successful for player {self._state.username} (UUID: {self._state.uid})")

    async def close(self) -> None:
        """Close the socket connection and clean up resources."""
        if self.__writer and not self.__writer.is_closing():
            try:
                self.__writer.close()
                await self.__writer.wait_closed()
            except (ConnectionError, asyncio.CancelledError):
                pass
        self.phase = 0