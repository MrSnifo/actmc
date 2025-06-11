from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from . import utils

import logging


_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .state import ConnectionState
    from .client import Client


class MinecraftSocket:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, state: ConnectionState) -> None:
        self.reader:  asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self._state: ConnectionState = state
        self.compression_threshold: int = -1


    @classmethod
    async def initialize_socket(cls, client: Client, state: ConnectionState) -> MinecraftSocket:
        """Initialize socket connection and send login packet."""
        connection = await client.tcp.connect()
        gateway = cls(*connection, state=state)
        return gateway


    async def async_read_varint(self) -> int:
        """Read VarInt asynchronously from StreamReader"""
        value = 0
        position = 0
        while True:
            byte = await self.reader.read(1)
            if not byte:
                raise asyncio.IncompleteReadError(b'', 1)

            current_byte = byte[0]
            value |= (current_byte & 0x7F) << position
            if (current_byte & 0x80) == 0:
                break

            position += 7
            if position >= 32:
                raise ValueError("VarInt too big (max 5 bytes)")
        return value

    def _parse_packet(self, data: bytes) -> tuple[int, bytes, int]:
        packet_length, offset = utils.read_varint(data)
        segment = data[offset:offset + packet_length]
        offset += packet_length

        # No compression mode
        if self.compression_threshold < 0:
            packet_id, seg_offset = utils.read_varint(segment)
            return packet_id, segment[seg_offset:], offset

        # Compression mode
        data_length, seg_offset = utils.read_varint(segment)
        remaining = segment[seg_offset:]

        # Uncompressed within compressed format
        if data_length == 0:
            packet_id, seg_offset = utils.read_varint(remaining)
            return packet_id, remaining[seg_offset:], offset

        # Actually compressed data
        packet_id, packet_data = utils.decompress_packet(remaining, data_length)
        return packet_id, packet_data, offset

    async def poll(self) -> None:
        length = await self.async_read_varint()
        data = await self.reader.readexactly(length)
        full_packet = utils.write_varint(length) + data
        packet_id, packet_data, _ = self._parse_packet(full_packet)

        # Custom TRACE level 5.
        _logger.trace(f"Received packet ID 0x{packet_id:02X} with size {length} bytes") # type: ignore

        if packet_id == 0x03 and self.compression_threshold == -1:
            """
            Compression (State=Login)

            Server sends packet (0x03) with Threshold (VarInt) to enable compression.
            Packets larger than Threshold are compressed.
            """
            threshold, _ = utils.read_varint(packet_data)
            self.compression_threshold = threshold
            _logger.debug(f"Compression enabled with threshold set to {threshold}")
            return

        if packet_id == 0x1F:
            """
            Keep Alive (State=Play)

            Server sends keep-alive (0x1F) with random ID (Long).
            Client must reply or disconnects occur (30s server kick, 20s client timeout).
            """
            value, _ = utils.read_long(packet_data)
            _logger.debug(f"Received KeepAlive packet with value {value}")
            await self._state.send_packet(0x0B, utils.long(value))
            return

        if packet_id in [0x02]:
            self._state.parse(packet_id, packet_data)

        return





