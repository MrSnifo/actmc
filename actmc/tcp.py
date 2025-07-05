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
import zlib
from typing import TYPE_CHECKING, Self
from actmc import protocol
from . import math
from .entities import misc
import asyncio

if TYPE_CHECKING:
    from typing import ClassVar, Optional, Coroutine, Any
    from asyncio import StreamReader, StreamWriter

import logging

_logger = logging.getLogger(__name__)


class TcpClient:
    """TCP connection handler for Minecraft protocol communication."""
    DEFAULT_LIMIT: ClassVar[int] = 65536
    PROTOCOL_VERSION: ClassVar[int] = 340  # Minecraft 1.12.2
    COMPRESSION_THRESHOLD_DEFAULT: ClassVar[int] = -1

    def __init__(self, host: str, port: int, reader: StreamReader, writer: StreamWriter) -> None:
        self.host: str = host
        self.port: int = port
        self._reader = reader
        self._writer = writer
        self._closed = False
        self.compression_threshold = self.COMPRESSION_THRESHOLD_DEFAULT

    @classmethod
    async def connect(cls, host: str, port: int) -> Self:
        """Create and initialize a socket connection."""
        reader, writer = await asyncio.open_connection(host=host, port=port, limit=cls.DEFAULT_LIMIT)
        _logger.debug(f"Connection established to {host}:{port}")
        return cls(host, port, reader, writer)

    @property
    def reader(self) -> StreamReader:
        """Get the stream reader."""
        if self._closed:
            raise RuntimeError("Connection is closed")
        return self._reader

    @property
    def writer(self) -> StreamWriter:
        """Get the stream writer."""
        if self._closed:
            raise RuntimeError("Connection is closed")
        return self._writer

    @property
    def is_closed(self) -> bool:
        """Check if the connection is closed."""
        return self._closed or self._writer.is_closing()

    async def close(self) -> None:
        """Close the connection gracefully."""
        if not self._closed:
            self._writer.close()
            await self._writer.wait_closed()
            self._closed = True
            _logger.debug(f"Connection to {self.host}:{self.port} closed")

    def _compress_payload(self, payload: bytes) -> bytes:
        """Compress payload data if compression is enabled."""
        payload_length = len(payload)
        body_buffer = protocol.ProtocolBuffer()

        if self.compression_threshold >= 0:
            if payload_length >= self.compression_threshold:
                # Compress data and include original length
                compressed_data = zlib.compress(payload)
                body_buffer.write(protocol.write_varint(payload_length))
                body_buffer.write(compressed_data)
                _logger.debug(f"Compressed payload: {payload_length} -> {len(compressed_data)} bytes")
            else:
                # Include uncompressed data with 0 length marker
                body_buffer.write(protocol.write_varint(0))
                body_buffer.write(payload)
        else:
            # No compression enabled
            body_buffer.write(payload)

        return body_buffer.getvalue()

    async def write_packet(self, packet_id: int, data: protocol.ProtocolBuffer) -> None:
        """Write a complete Minecraft protocol packet."""
        if self.is_closed:
            raise RuntimeError("Cannot write to closed connection")

        try:
            packet_id_bytes = protocol.write_varint(packet_id)
            payload = packet_id_bytes + data.getvalue()

            body = self._compress_payload(payload)

            # Write packet length followed by packet data
            self.writer.write(protocol.write_varint(len(body)))
            self.writer.write(body)
            await self.writer.drain()

            _logger.debug("Sent packet 0x%02X", packet_id)
        except Exception as e:
            _logger.error(f"Failed to write packet 0x{packet_id:02X}: {e}")
            raise

    def handshake_packet(self, next_state: int = 2) -> Coroutine[Any, Any, None]:
        """Construct the Minecraft handshake packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(self.PROTOCOL_VERSION))
        buffer.write(protocol.pack_string(self.host))
        buffer.write(protocol.pack_short(self.port))
        buffer.write(protocol.write_varint(next_state))
        return self.write_packet(0x00, buffer)

    def login_packet(self, username: str) -> Coroutine[Any, Any, None]:
        """Send login start packet with username."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_string(username))
        return self.write_packet(0x00, buffer)

    def client_status(self, action_id: int) -> Coroutine[Any, Any, None]:
        """Send client status packet (respawn, request stats, etc.)."""
        return self.write_packet(0x03, protocol.ProtocolBuffer(protocol.write_varint(action_id)))

    def player_teleport_confirmation(self, teleport_id: int) -> Coroutine[Any, Any, None]:
        """Confirm server teleport request."""
        return self.write_packet(0x00, protocol.ProtocolBuffer(protocol.write_varint(teleport_id)))

    def player_ground(self, on_ground: bool) -> Coroutine[Any, Any, None]:
        """Send player ground state packet."""
        return self.write_packet(0x0C, protocol.ProtocolBuffer(protocol.pack_bool(on_ground)))

    def player_look(self, rotation: math.Rotation, on_ground: bool) -> Coroutine[Any, Any, None]:
        """Send player rotation update packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_float(rotation.yaw))
        buffer.write(protocol.pack_float(rotation.pitch))
        buffer.write(protocol.pack_bool(on_ground))
        return self.write_packet(0x0F, buffer)

    def player_position_and_look_packet(self, position: math.Vector3D[float],
                                        rotation: math.Rotation,
                                        on_ground: bool) -> Coroutine[Any, Any, None]:
        """Send combined player position and rotation update packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_double(position.x))
        buffer.write(protocol.pack_double(position.y))
        buffer.write(protocol.pack_double(position.z))
        buffer.write(protocol.pack_float(rotation.yaw))
        buffer.write(protocol.pack_float(rotation.pitch))
        return self.write_packet(0x0E, buffer)

    def player_position(self, position: math.Vector3D[float], on_ground: bool) -> Coroutine[Any, Any, None]:
        """Send player position update packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_double(position.x))
        buffer.write(protocol.pack_double(position.y))
        buffer.write(protocol.pack_double(position.z))
        buffer.write(protocol.pack_bool(on_ground))
        return self.write_packet(0x0D, buffer)

    def use_item(self, hand: int) -> Coroutine[Any, Any, None]:
        """Send use item packet (right-click with item)."""
        return self.write_packet(0x20, protocol.ProtocolBuffer(protocol.write_varint(hand)))

    def held_item_change(self, slot: int) -> Coroutine[Any, Any, None]:
        """Change selected hotbar slot."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_short(slot))
        return self.write_packet(0x15, buffer)

    def swing_arm(self, hand: int) -> Coroutine[Any, Any, None]:
        """Send arm swing animation packet."""
        return self.write_packet(0x1D, protocol.ProtocolBuffer(protocol.write_varint(hand)))

    def player_block_placement(self, position: math.Vector3D[int], face: int, hand: int, cursor: math.Vector3D[float]
                               ) -> Coroutine[Any, Any, None]:
        """Send block placement packet (right-click on block)."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_position(*position))
        buffer.write(protocol.write_varint(face))
        buffer.write(protocol.write_varint(hand))
        buffer.write(protocol.pack_float(cursor.x))
        buffer.write(protocol.pack_float(cursor.y))
        buffer.write(protocol.pack_float(cursor.z))
        return self.write_packet(0x1F, buffer)

    def player_digging(self, status: int, position: math.Vector3D[float], face: int) -> Coroutine[Any, Any, None]:
        """Send block digging packet (start/stop/finish mining)."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(status))
        buffer.write(protocol.pack_position(*position))
        buffer.write(protocol.pack_byte(face))
        return self.write_packet(0x14, buffer)

    def confirm_window_transaction(self, window_id: int, action_number: int,
                                   accepted: bool) -> Coroutine[Any, Any, None]:
        """Confirm or deny window transaction (inventory actions)."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_byte(window_id))
        buffer.write(protocol.pack_short(action_number))
        buffer.write(protocol.pack_bool(accepted))
        return self.write_packet(0x05, buffer)

    def entity_action(self, entity_id: int, action_id: int, jump_boost: int) -> Coroutine[Any, Any, None]:
        """Send entity action packet (sneak, sprint, stop sneaking, etc.)."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(entity_id))
        buffer.write(protocol.write_varint(action_id))
        buffer.write(protocol.write_varint(jump_boost))
        return self.write_packet(0x15, buffer)

    def use_entity(self, target_id: int, type_action: int, hitbox: math.Vector3D[float] = None, hand: int = None
                   ) -> Coroutine[Any, Any, None]:
        """Send use entity packet (interact, attack, or interact at specific location)."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(target_id))
        buffer.write(protocol.write_varint(type_action))

        # Include hitbox coordinates for targeted interactions
        if type_action == 2 and hitbox is not None:
            buffer.write(protocol.pack_float(hitbox.x))
            buffer.write(protocol.pack_float(hitbox.y))
            buffer.write(protocol.pack_float(hitbox.z))

        # Include hand for interact and targeted interact actions
        if type_action in [0, 2] and hand is not None:
            buffer.write(protocol.write_varint(hand))

        return self.write_packet(0x0A, buffer)

    def update_sign(self, position: math.Vector3D[float], line1: str, line2: str, line3: str, line4: str
                    ) -> Coroutine[Any, Any, None]:
        """Update sign text at specified position."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_position(*position))
        buffer.write(protocol.pack_string(line1))
        buffer.write(protocol.pack_string(line2))
        buffer.write(protocol.pack_string(line3))
        buffer.write(protocol.pack_string(line4))
        return self.write_packet(0x1C, buffer)

    def creative_inventory_action(self, slot: int, clicked_item: Optional[misc.ItemData]) -> Coroutine[Any, Any, None]:
        """Set or clear item in creative mode inventory slot."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_short(slot))

        if clicked_item is None:
            # Clear slot by setting item ID to -1
            buffer.write(protocol.pack_short(-1))
        else:
            # Set item with all properties
            buffer.write(protocol.pack_short(clicked_item['item_id']))
            buffer.write(protocol.pack_byte(clicked_item['item_count']))
            buffer.write(protocol.pack_short(clicked_item['item_damage']))
            if clicked_item.get('nbt') is None:
                buffer.write(protocol.pack_byte(0))
            else:
                nbt_data = protocol.pack_nbt(clicked_item['nbt'])
                buffer.write(nbt_data)

        return self.write_packet(0x1B, buffer)

    def advancement_tab(self, action: int, tab_id: Optional[str] = None) -> Coroutine[Any, Any, None]:
        """Send advancement tab action (open/close specific tab)."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(action))
        if tab_id is not None:
            buffer.write(protocol.pack_string(tab_id))

        return self.write_packet(0x19, buffer)

    def resource_pack_status(self, result: int) -> Coroutine[Any, Any, None]:
        """Send resource pack status response (accepted, declined, loaded, etc.)."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(result))
        return self.write_packet(0x18, buffer)

    def client_settings(self, locale: str, view_distance: int, chat_mode: int, chat_colors: bool,
                        skin_parts: int, main_hand: int) -> Coroutine[Any, Any, None]:
        """Send client settings packet with player preferences."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_string(locale))
        buffer.write(protocol.pack_byte(view_distance))
        buffer.write(protocol.write_varint(chat_mode))
        buffer.write(protocol.pack_bool(chat_colors))
        buffer.write(protocol.pack_ubyte(skin_parts))
        buffer.write(protocol.write_varint(main_hand))
        return self.write_packet(0x04, buffer)