from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from . import protocol, utils
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
        self.compression = protocol.PacketCompressor(-1)

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

    async def send_packet(self, packet_id: int, data: bytes) -> None:
        packet_id_bytes = protocol.write_varint(packet_id)
        uncompressed_payload = packet_id_bytes + data
        uncompressed_len = len(uncompressed_payload)

        if self.compression.compression_threshold  < 0:
            # No compression
            packet_bytes = protocol.write_varint(uncompressed_len) + uncompressed_payload
        else:
            if uncompressed_len < self.compression.compression_threshold :
                # Send uncompressed, but in compression format (VarInt 0 + data)
                data_length_bytes = protocol.write_varint(0)
                payload = data_length_bytes + uncompressed_payload
            else:
                # Compress payload: use your PacketCompressor.compress_packet here
                packet_bytes = self.compression.compress_packet(packet_id, data)
                # Return early since compress_packet already returns full packet including length prefix
                self.writer.write(packet_bytes)
                await self.writer.drain()
                return

            packet_bytes = protocol.write_varint(len(payload)) + payload

        # Send packet bytes over writer
        self.writer.write(packet_bytes)
        await self.writer.drain()

    def _parse_packet(self, data: bytes) -> tuple[int, protocol.ProtocolBuffer]:
        buffer = protocol.ProtocolBuffer(data)
        packet_length = protocol.read_varint(buffer)
        segment = buffer.read(packet_length)
        segment_buffer = protocol.ProtocolBuffer(segment)

        if  self.compression.compression_threshold < 0:
            packet_id = protocol.read_varint(segment_buffer)
            return packet_id, segment_buffer
        else:
            packet_id, decompressed_buffer = self.compression.decompress_packet(data)
            return packet_id, protocol.ProtocolBuffer(decompressed_buffer)

    async def poll(self) -> None:
        length = await self.async_read_varint()
        data = await self.reader.readexactly(length)
        full_packet = protocol.write_varint(length) + data
        packet_id, packet_data = self._parse_packet(full_packet)

        # Custom TRACE level 5.
        _logger.trace(f"Received packet ID 0x{packet_id:02X} with size {length} bytes") # type: ignore

        if packet_id == 0x03 and self.compression.compression_threshold == -1:
            """
            Compression (State=Login)
            Server sends packet (0x03) with Threshold (VarInt) to enable compression.
            """
            threshold = protocol.read_varint(packet_data)
            self.compression.compression_threshold = threshold
            _logger.debug(f"Compression enabled with threshold set to {threshold}")
            return

        if packet_id == 0x1F:
            """
            Keep Alive (State=Play)
            Server sends keep-alive (0x1F) with random ID (Long).
            Client must reply or disconnects occur (30s server kick, 20s client timeout).
            """
            value = protocol.read_long(packet_data)
            _logger.debug(f"Received KeepAlive packet with value {value}")
            await self.send_packet(0x0B, protocol.pack_long(value))
            return

        if packet_id in [0x02, 0x23, 0x1a, 0x41, 0x40, 0x3a, 0x20, 0x1d]:
            self._state.parse(packet_id, packet_data)

        return






