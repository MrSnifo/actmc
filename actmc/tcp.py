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
from actmc import protocol
from . import math
import asyncio

if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter
    from typing import ClassVar, Optional, Tuple

import logging
_logger = logging.getLogger(__name__)

class TcpClient:
    """Represents an asynchronous TCP client for establishing and managing connections."""
    DEFAULT_LIMIT: ClassVar[int] = 65536
    PROTOCOL: ClassVar[int] = 340

    __slots__ = ('host', 'port')

    def __init__(self, host: str, port: Optional[int]) -> None:
        self.host = host
        self.port = port

    async def connect(self) -> Tuple[StreamReader, StreamWriter]:
        """Establish an asynchronous TCP connection to the specified host and port."""
        _logger.debug(f"Connecting to {self.host}:{self.port}...")
        reader, writer = await asyncio.open_connection(
            host=self.host, port=self.port, limit=self.DEFAULT_LIMIT
        )
        _logger.debug(f"Connection established to {self.host}:{self.port}")
        return reader, writer

    @property
    def handshake_packet(self, next_state: int = 2) -> protocol.ProtocolBuffer:
        """Construct the Minecraft handshake packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(self.PROTOCOL))
        buffer.write(protocol.pack_string(self.host))
        buffer.write(protocol.pack_short(self.port))
        buffer.write(protocol.write_varint(next_state))
        return buffer

    @staticmethod
    def login_packet(username: str) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_string(username))
        return buffer

    @staticmethod
    def client_status(action_id: int) -> protocol.ProtocolBuffer:
        return protocol.ProtocolBuffer(protocol.write_varint(action_id))

    @staticmethod
    def player_teleport_confirmation(teleport_id: int):
        return protocol.ProtocolBuffer(protocol.write_varint(teleport_id))

    @staticmethod
    def player_ground(on_ground: bool) -> protocol.ProtocolBuffer:
        return protocol.ProtocolBuffer(protocol.pack_bool(on_ground))

    @staticmethod
    def player_look_packet(yaw: float, pitch: float, on_ground: bool) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_float(yaw))
        buffer.write(protocol.pack_float(pitch))
        buffer.write(protocol.pack_bool(on_ground))
        return buffer

    @staticmethod
    def player_position_and_look_packet(position: math.Vector3D[float],
                                        rotation: math.Rotation,
                                        on_ground: bool) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_double(position.x))
        buffer.write(protocol.pack_double(position.y))
        buffer.write(protocol.pack_double(position.z))
        buffer.write(protocol.pack_float(rotation.yaw))
        buffer.write(protocol.pack_float(rotation.pitch))
        buffer.write(protocol.pack_bool(on_ground))
        return buffer

    @staticmethod
    def player_position(position: math.Vector3D[float], on_ground: bool) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_double(position.x))
        buffer.write(protocol.pack_double(position.y))
        buffer.write(protocol.pack_double(position.z))
        buffer.write(protocol.pack_bool(on_ground))
        return buffer

    @staticmethod
    def player_look(rotation: math.Rotation, on_ground: bool) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_float(rotation.yaw))
        buffer.write(protocol.pack_float(rotation.pitch))
        buffer.write(protocol.pack_bool(on_ground))
        return buffer

    @staticmethod
    def use_item(hand: int) -> protocol.ProtocolBuffer:
        return protocol.ProtocolBuffer(protocol.write_varint(hand))

    @staticmethod
    def swing_arm(hand: int) -> protocol.ProtocolBuffer:
        return protocol.ProtocolBuffer(protocol.write_varint(hand))

    @staticmethod
    def player_digging(status: int, position: math.Vector3D[float], face: int) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(status))
        buffer.write(protocol.pack_position(*position))
        buffer.write(protocol.pack_byte(face))
        return buffer

    @staticmethod
    def confirm_window_transaction(window_id: int, action_number: int, accepted: bool) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_byte(window_id))
        buffer.write(protocol.pack_short(action_number))
        buffer.write(protocol.pack_bool(accepted))
        return buffer

    @staticmethod
    def entity_action(entity_id: int, action_id: int, jump_boost: int) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(entity_id))
        buffer.write(protocol.write_varint(action_id))
        buffer.write(protocol.write_varint(jump_boost))
        return buffer

    @staticmethod
    def use_entity_interact(target_id: int, hand: int) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(target_id))
        buffer.write(protocol.write_varint(0))
        buffer.write(protocol.write_varint(hand))
        return buffer

    @staticmethod
    def use_entity_attack(target_id: int) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(target_id))
        buffer.write(protocol.write_varint(1))
        return buffer

    @staticmethod
    def use_entity_interact_at(target_id: int, hitbox: math.Vector3D[float], hand: int) -> protocol.ProtocolBuffer:
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(target_id))
        buffer.write(protocol.write_varint(2))
        buffer.write(protocol.pack_float(hitbox.x))
        buffer.write(protocol.pack_float(hitbox.y))
        buffer.write(protocol.pack_float(hitbox.z))
        buffer.write(protocol.write_varint(hand))
        return buffer
