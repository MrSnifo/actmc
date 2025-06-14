from __future__ import annotations

import asyncio
import zlib

from . import protocol

from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from .state import ConnectionState
    from .client import Client
    from typing import Self


import logging
_logger = logging.getLogger(__name__)


class MinecraftSocket:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, state: ConnectionState) -> None:
        self.reader:  asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self._state: ConnectionState = state
        self.compression_threshold = -1

    @classmethod
    async def initialize_socket(cls, client: Client, state: ConnectionState) -> Self:
        """Initialize socket connection and send login packet."""
        connection = await client.tcp.connect()
        gateway = cls(*connection, state=state)
        return gateway

    async def read_packet(self) -> Tuple[int, bytes]:
        """
        Reads a packet following the exact Minecraft protocol with compression,
        using the unpack_packet-style approach.
        """
        packet_length = await self._read_varint_async()

        # Read the entire packet body
        body = await self.reader.readexactly(packet_length)
        buffer = protocol.ProtocolBuffer(body)

        if self.compression_threshold >= 0:
            # Read uncompressed length (Data Length field)
            uncompressed_length = protocol.read_varint(buffer)

            if uncompressed_length > 0:
                # Compressed packet - decompress the remaining data
                compressed_data = buffer.read(buffer.remaining())
                try:
                    body = zlib.decompress(compressed_data)
                except zlib.error as e:
                    raise ValueError(f"Decompression error: {e}") from e

                # Verify length matches expected
                if len(body) != uncompressed_length:
                    raise ValueError(f"Decompressed length mismatch: expected {uncompressed_length} got {len(body)}")

                # Create new buffer with decompressed data
                buffer = protocol.ProtocolBuffer(body)

        packet_id = protocol.read_varint(buffer)
        data = buffer.read(buffer.remaining())
        return packet_id, data

    async def write_packet(self, packet_id: int, data: bytes) -> None:
        """
        Writes a packet following the exact Minecraft protocol with compression,
        maintaining consistency with the read_packet method.
        """
        # Prepare packet ID and payload
        packet_id_bytes = protocol.write_varint(packet_id)
        payload = packet_id_bytes + data
        payload_length = len(payload)

        # Create body buffer
        body_buffer = protocol.ProtocolBuffer()

        if self.compression_threshold >= 0:
            if payload_length >= self.compression_threshold:
                # Compress the payload
                compressed_data = zlib.compress(payload)

                # Write uncompressed length and compressed data
                body_buffer.write(protocol.write_varint(payload_length))
                body_buffer.write(compressed_data)
            else:
                # Write uncompressed marker (0) and original payload
                body_buffer.write(protocol.write_varint(0))
                body_buffer.write(payload)
        else:
            # No compression - just write the payload
            body_buffer.write(payload)

        # Get complete packet body
        body = body_buffer.getvalue()

        # Write packet length (VarInt) followed by body
        self.writer.write(protocol.write_varint(len(body)))
        self.writer.write(body)
        await self.writer.drain()

    def set_compression(self, threshold: int) -> None:
        """Update the compression threshold"""
        self.compression_threshold = threshold

    async def _read_varint_async(self) -> int:
        """Read VarInt from a StreamReader"""
        data = bytearray()
        for _ in range(5):  # Max 5 bytes for VarInt
            byte = await self.reader.readexactly(1)
            data.append(byte[0])
            if not (byte[0] & 0x80):
                break
        buf = protocol.ProtocolBuffer(data)
        return protocol.read_varint(buf)

    @staticmethod
    def _varint_size(value: int) -> int:
        """Calculate the byte size of a VarInt"""
        if value == 0:
            return 1
        size = 0
        while value:
            size += 1
            value >>= 7
        return size

    async def poll(self) -> None:
        packet_id, data = await self.read_packet()
        buffer = protocol.ProtocolBuffer(data)

        _logger.trace(f"Received packet ID 0x{packet_id:02X}") # type: ignore

        if packet_id == 0x03 and self.compression_threshold == -1:
            """
            Compression (State=Login)
            Server sends packet (0x03) with Threshold (VarInt) to enable compression.
            """
            threshold = protocol.read_varint(buffer)
            self.compression_threshold = threshold
            _logger.debug(f"Compression enabled with threshold set to {threshold}")
            return


        if packet_id == 0x1F:
            """
            Keep Alive (State=Play)
            Server sends keep-alive (0x1F) with random ID (Long).
            Client must reply or disconnects occur (30s server kick, 20s client timeout).
            """
            value = protocol.read_long(buffer)
            _logger.debug(f"Received KeepAlive packet with value {value}")
            await self.write_packet(0x0B, protocol.pack_long(value))
            return

        if packet_id in [0x02, 0x23, 0x1a, 0x41, 0x40, 0x3a, 0x20, 0x2f, 0x30, 0x00, 0x0b]:
            self._state.parse(packet_id, buffer)
