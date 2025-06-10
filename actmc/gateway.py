from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING

from .utils import decompress_packet, compress_packet, Packet
from .socket import ClientSocket

import logging


_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .state import ConnectionState


class SocketGateway:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, state: ConnectionState) -> None:
        self.reader:  asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self._state: ConnectionState = state
        self.compression_threshold: int = -1



    @classmethod
    async def initialize_socket(cls, state: ConnectionState) -> SocketGateway:
        """Initialize socket connection and send login packet."""
        socket = ClientSocket(state.host, state.port)
        connection = await socket.connect()
        gateway = cls(*connection, state=state)
        await gateway.send_packet(0x00, socket.handshake_packet)
        await gateway.send_packet(0x00, Packet.string(state.username))
        return gateway

    async def send_packet(self, packet_id: int, data: bytes) -> None:
        packet_id_bytes = Packet.write_varint(packet_id)
        uncompressed_payload = packet_id_bytes + data
        uncompressed_len = len(uncompressed_payload)

        if self.compression_threshold < 0:
            # No compression
            packet_bytes = Packet.write_varint(len(uncompressed_payload)) + uncompressed_payload
        else:
            if uncompressed_len < self.compression_threshold:
                # Send uncompressed, but in compression format (VarInt 0 + data)
                data_length_bytes = Packet.write_varint(0)
                payload = data_length_bytes + uncompressed_payload
            else:
                # Compress payload
                compressed_data = compress_packet(packet_id, data)
                data_length_bytes = Packet.write_varint(uncompressed_len)
                payload = data_length_bytes + compressed_data

            packet_bytes = Packet.write_varint(len(payload)) + payload

        self.writer.write(packet_bytes)
        await self.writer.drain()
        _logger.debug(f"Sent packet ID 0x{packet_id:02X} with size {len(packet_bytes)} bytes")

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
        packet_length, offset = Packet.read_varint(data)
        segment = data[offset:offset + packet_length]
        offset += packet_length

        # No compression mode
        if self.compression_threshold < 0:
            packet_id, seg_offset = Packet.read_varint(segment)
            return packet_id, segment[seg_offset:], offset

        # Compression mode
        data_length, seg_offset = Packet.read_varint(segment)
        remaining = segment[seg_offset:]

        # Uncompressed within compressed format
        if data_length == 0:
            packet_id, seg_offset = Packet.read_varint(remaining)
            return packet_id, remaining[seg_offset:], offset

        # Actually compressed data
        packet_id, packet_data = decompress_packet(remaining, data_length)
        return packet_id, packet_data, offset

    async def poll(self) -> None:
        length = await self.async_read_varint()
        data = await self.reader.readexactly(length)
        full_packet = Packet.write_varint(length) + data
        packet_id, packet_data, _ = self._parse_packet(full_packet)

        # Custom TRACE level 5.
        _logger.trace(f"Received packet ID 0x{packet_id:02X} with size {length} bytes") # type: ignore

        if packet_id == 0x03 and self.compression_threshold == -1:
            """
            Compression (State=Login)

            Server sends packet (0x03) with Threshold (VarInt) to enable compression.
            Packets larger than Threshold are compressed.
            """
            threshold, _ = Packet.read_varint(packet_data)
            self.compression_threshold = threshold
            _logger.debug(f"Compression enabled with threshold set to {threshold}")
            return

        if packet_id == 0x1F:
            """
            Keep Alive (State=Play)

            Server sends keep-alive (0x1F) with random ID (Long).
            Client must reply or disconnects occur (30s server kick, 20s client timeout).
            """
            value, _ = Packet.read_long(packet_data)
            _logger.debug(f"Received KeepAlive packet with value {value}")
            await self.send_packet(0x0B, Packet.long(value))
            return

        self._state.parse(packet_id, packet_data)





