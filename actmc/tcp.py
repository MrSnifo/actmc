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

from .errors import InvalidDataError, ConnectionClosed, PacketError
from typing import TYPE_CHECKING
from actmc import protocol
import asyncio
import zlib

if TYPE_CHECKING:
    from typing import ClassVar, Optional, Coroutine, Any, Tuple
    from .entities import misc
    from . import math

import logging
_logger = logging.getLogger(__name__)

__all__ = ('TcpClient',)

class TcpClient:
    """TCP connection handler for Minecraft protocol communication."""
    DEFAULT_LIMIT: ClassVar[int] = 65536
    # Minecraft 1.12.2
    PROTOCOL_VERSION: ClassVar[int] = 340
    COMPRESSION_THRESHOLD_DEFAULT: ClassVar[int] = -1

    if TYPE_CHECKING:
        _writer: asyncio.StreamWriter

    def __init__(self) -> None:
        self.compression_threshold = self.COMPRESSION_THRESHOLD_DEFAULT

    def clear(self) -> None:
        """Clear connection state and cleanup resources."""
        self.compression_threshold = self.COMPRESSION_THRESHOLD_DEFAULT
        if hasattr(self, '_writer'): 
            delattr(self, '_writer')

    async def open_connection(self, host: str, port: int) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Create and initialize a socket connection."""
        
        if not host or not host.strip():
            raise InvalidDataError("Host cannot be empty")
        if not (1 <= port <= 65535):
            raise InvalidDataError("Port must be between 1 and 65535")
        
        reader, writer = await asyncio.open_connection(host=host, port=port, limit=self.DEFAULT_LIMIT)
        _logger.debug(f"Connection established to {host}:{port}")
        return reader, writer

    @property
    def writer(self) -> asyncio.StreamWriter:
        """Get the stream writer."""
        if not hasattr(self, '_writer') or self._writer.is_closing():
            raise ConnectionClosed("Connection is closed")
        return self._writer

    def _compress_payload(self, payload: bytes) -> bytes:
        """Compress payload data if compression is enabled."""
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

        return body_buffer.getvalue()

    async def write_packet(self, packet_id: int, data: protocol.ProtocolBuffer) -> None:
        """Write a complete Minecraft protocol packet."""
        try:
            packet_id_bytes = protocol.write_varint(packet_id)
            payload = packet_id_bytes + data.getvalue()

            body = self._compress_payload(payload)

            self.writer.write(protocol.write_varint(len(body)))
            self.writer.write(body)
            await self.writer.drain()
            _logger.debug("Sent packet 0x%02X", packet_id)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError) as e:
            raise ConnectionClosed(f"Connection lost while writing packet 0x{packet_id:02X}") from e
        except OSError as e:
            raise ConnectionClosed(f"Network error writing packet 0x{packet_id:02X}: {e}") from e
        except (ValueError, TypeError) as e:
            raise InvalidDataError(f"Invalid packet data for 0x{packet_id:02X}: {e}") from e
        except Exception as e:
            raise PacketError(f"Unexpected error writing packet 0x{packet_id:02X}: {e}") from e

    def handshake_packet(self, host: str, port: int, next_state: int = 2) -> Coroutine[Any, Any, None]:
        """Construct the Minecraft handshake packet."""
        if not host or not host.strip():
            raise InvalidDataError("Host cannot be empty")
        if not (1 <= port <= 65535):
            raise InvalidDataError("Port must be between 1 and 65535")
        if next_state not in [1, 2]:
            raise InvalidDataError("Next state must be 1 (status) or 2 (login)")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(self.PROTOCOL_VERSION))
        buffer.write(protocol.pack_string(host))
        buffer.write(protocol.pack_ushort(port))
        buffer.write(protocol.write_varint(next_state))
        return self.write_packet(0x00, buffer)

    def login_packet(self, username: str) -> Coroutine[Any, Any, None]:
        """Send login start packet with username."""
        if not username or not username.strip():
            raise InvalidDataError("Username cannot be empty")
        if len(username) > 16:
            raise InvalidDataError("Username cannot exceed 16 characters")
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_string(username))
        return self.write_packet(0x00, buffer)

    def client_status(self, action_id: int) -> Coroutine[Any, Any, None]:
        """Send client status packet (respawn, request stats, etc.)."""
        if action_id not in [0, 1]:
            raise InvalidDataError("Action ID must be 0 (respawn) or 1 (request stats)")
        return self.write_packet(0x03, protocol.ProtocolBuffer(protocol.write_varint(action_id)))

    def player_teleport_confirmation(self, teleport_id: int) -> Coroutine[Any, Any, None]:
        """Confirm server teleport request."""
        return self.write_packet(0x00, protocol.ProtocolBuffer(protocol.write_varint(teleport_id)))

    def player_position_and_look(self,
                                 position: math.Vector3D[float],
                                 rotation: math.Rotation,
                                 on_ground: bool) -> Coroutine[Any, Any, None]:
        """Send combined player position and rotation update packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_double(position.x))
        buffer.write(protocol.pack_double(position.y))
        buffer.write(protocol.pack_double(position.z))
        buffer.write(protocol.pack_float(rotation.yaw))
        buffer.write(protocol.pack_float(rotation.pitch))
        buffer.write(protocol.pack_bool(on_ground))
        return self.write_packet(0x0E, buffer)

    def player_position(self, position: math.Vector3D[float], on_ground: bool) -> Coroutine[Any, Any, None]:
        """Send player position update packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_double(position.x))
        buffer.write(protocol.pack_double(position.y))
        buffer.write(protocol.pack_double(position.z))
        buffer.write(protocol.pack_bool(on_ground))
        return self.write_packet(0x0D, buffer)

    def player_look(self, rotation: math.Rotation, on_ground: bool) -> Coroutine[Any, Any, None]:
        """Send player rotation update packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_float(rotation.yaw))
        buffer.write(protocol.pack_float(rotation.pitch))
        buffer.write(protocol.pack_bool(on_ground))
        return self.write_packet(0x0F, buffer)

    def player_ground(self, on_ground: bool) -> Coroutine[Any, Any, None]:
        """Send player ground state packet."""
        return self.write_packet(0x0C, protocol.ProtocolBuffer(protocol.pack_bool(on_ground)))

    def vehicle_move(self, position: math.Vector3D[float], yaw: float, pitch: float) -> Coroutine[Any, Any, None]:
        """Send vehicle movement packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_double(position.x))
        buffer.write(protocol.pack_double(position.y))
        buffer.write(protocol.pack_double(position.z))
        buffer.write(protocol.pack_float(yaw))
        buffer.write(protocol.pack_float(pitch))
        return self.write_packet(0x10, buffer)

    def steer_boat(self, right_paddle_turning: bool, left_paddle_turning: bool) -> Coroutine[Any, Any, None]:
        """Send boat steering packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_bool(right_paddle_turning))
        buffer.write(protocol.pack_bool(left_paddle_turning))
        return self.write_packet(0x11, buffer)

    def steer_vehicle(self, sideways: float, forward: float, flags: int) -> Coroutine[Any, Any, None]:
        """Send steer vehicle packet to control vehicle movement."""
        if not (0 <= flags <= 3):
            raise InvalidDataError("Flags must be between 0 and 3")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_float(sideways))
        buffer.write(protocol.pack_float(forward))
        buffer.write(protocol.pack_ubyte(flags))
        return self.write_packet(0x16, buffer)

    def player_abilities(self, flags: int, flying_speed: float, walking_speed: float) -> Coroutine[Any, Any, None]:
        """Send player abilities packet."""
        if not (0 <= flags <= 15):
            raise InvalidDataError("Flags must be between 0 and 15")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_byte(flags))
        buffer.write(protocol.pack_float(flying_speed))
        buffer.write(protocol.pack_float(walking_speed))
        return self.write_packet(0x13, buffer)

    def use_item(self, hand: int) -> Coroutine[Any, Any, None]:
        """Send use item packet (right-click with item)."""
        if hand not in [0, 1]:
            raise InvalidDataError("Hand must be 0 (main) or 1 (off)")
        
        return self.write_packet(0x20, protocol.ProtocolBuffer(protocol.write_varint(hand)))

    def held_item_change(self, slot: int) -> Coroutine[Any, Any, None]:
        """Change selected hotbar slot."""
        if not (0 <= slot <= 8):
            raise InvalidDataError("Slot must be between 0 and 8")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_short(slot))
        return self.write_packet(0x1A, buffer)

    def swing_arm(self, hand: int) -> Coroutine[Any, Any, None]:
        """Send arm swing animation packet."""
        if hand not in [0, 1]:
            raise InvalidDataError("Hand must be 0 (main) or 1 (off)")
        
        return self.write_packet(0x1D, protocol.ProtocolBuffer(protocol.write_varint(hand)))

    def player_block_placement(self, position: math.Vector3D[int], face: int, hand: int, cursor: math.Vector3D[float]
                               ) -> Coroutine[Any, Any, None]:
        """Send block placement packet (right-click on block)."""
        if not (0 <= face <= 5):
            raise InvalidDataError("Face must be between 0 and 5")
        if hand not in [0, 1]:
            raise InvalidDataError("Hand must be 0 (main) or 1 (off)")
        
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
        if not (0 <= status <= 6):
            raise InvalidDataError("Status must be between 0 and 6")
        if not (0 <= face <= 5):
            raise InvalidDataError("Face must be between 0 and 5")
        
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

    def craft_recipe_request(self, window_id: int, recipe_id: int, make_all: bool) -> Coroutine[Any, Any, None]:
        """Send craft recipe request packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_byte(window_id))
        buffer.write(protocol.write_varint(recipe_id))
        buffer.write(protocol.pack_bool(make_all))
        return self.write_packet(0x12, buffer)

    def crafting_book_data_displayed_recipe(self, recipe_id: int) -> Coroutine[Any, Any, None]:
        """Send crafting book data packet for displayed recipe."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(0))
        buffer.write(protocol.pack_int(recipe_id))
        return self.write_packet(0x17, buffer)

    def crafting_book_data_status(self, crafting_book_open: bool, crafting_filter: bool) -> Coroutine[Any, Any, None]:
        """Send crafting book data packet for status."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(1))
        buffer.write(protocol.pack_bool(crafting_book_open))
        buffer.write(protocol.pack_bool(crafting_filter))
        return self.write_packet(0x17, buffer)

    def entity_action(self, entity_id: int, action_id: int, jump_boost: int) -> Coroutine[Any, Any, None]:
        """Send entity action packet (sneak, sprint, stop sneaking, etc.)."""
        if entity_id < 0:
            raise InvalidDataError("Entity ID cannot be negative")
        if not (0 <= action_id <= 8):
            raise InvalidDataError("Action ID must be between 0 and 8")
        if not (0 <= jump_boost <= 100):
            raise InvalidDataError("Jump boost must be between 0 and 100")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(entity_id))
        buffer.write(protocol.write_varint(action_id))
        buffer.write(protocol.write_varint(jump_boost))
        return self.write_packet(0x15, buffer)

    def use_entity(self, target_id: int, type_action: int, hitbox: math.Vector3D[float] = None, hand: int = None
                   ) -> Coroutine[Any, Any, None]:
        """Send use entity packet (interact, attack, or interact at specific location)."""
        if not (0 <= type_action <= 2):
            raise InvalidDataError("Type action must be between 0 and 2")
        if type_action == 2 and hitbox is None:
            raise InvalidDataError("Hitbox required for interact at action")
        if type_action in [0, 2] and hand is None:
            raise InvalidDataError("Hand required for interact actions")
        if hand is not None and hand not in [0, 1]:
            raise InvalidDataError("Hand must be 0 (main) or 1 (off)")
        
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
        # Check line lengths (max 384 characters each)
        for i, line in enumerate([line1, line2, line3, line4], 1):
            if len(line) > 384:
                raise InvalidDataError(f"Line {i} cannot exceed 384 characters")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_position(*position))
        buffer.write(protocol.pack_string(line1))
        buffer.write(protocol.pack_string(line2))
        buffer.write(protocol.pack_string(line3))
        buffer.write(protocol.pack_string(line4))
        return self.write_packet(0x1C, buffer)

    def creative_inventory_action(self, slot: int, clicked_item: Optional[misc.ItemData]) -> Coroutine[Any, Any, None]:
        """Set or clear item in creative mode inventory slot."""
        if not (-1 <= slot <= 45):
            raise InvalidDataError("Slot must be between -1 and 45")
        
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
        if action not in [0, 1]:  # 0=opened tab, 1=closed screen
            raise InvalidDataError("Action must be 0 (opened tab) or 1 (closed screen)")
        if action == 0 and (tab_id is None or not tab_id.strip()):
            raise InvalidDataError("Tab ID required for opened tab action")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(action))
        if tab_id is not None:
            buffer.write(protocol.pack_string(tab_id))

        return self.write_packet(0x19, buffer)

    def resource_pack_status(self, result: int) -> Coroutine[Any, Any, None]:
        """Send resource pack status response (accepted, declined, loaded, etc.)."""
        if not (0 <= result <= 3):
            raise InvalidDataError("Result must be between 0 and 3")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.write_varint(result))
        return self.write_packet(0x18, buffer)

    def client_settings(self, locale: str, view_distance: int, chat_mode: int, chat_colors: bool,
                        skin_parts: int, main_hand: int) -> Coroutine[Any, Any, None]:
        """Send client settings packet with player preferences."""
        if len(locale) > 16:
            raise InvalidDataError("Locale must be non-empty and max 16 characters")
        if not (2 <= view_distance <= 32):
            raise InvalidDataError("View distance must be between 2 and 32")
        if chat_mode not in [0, 1, 2]:
            raise InvalidDataError("Chat mode must be 0, 1, or 2")
        if not (0 <= skin_parts <= 127):
            raise InvalidDataError("Skin parts must be between 0 and 127")
        if main_hand not in [0, 1]:
            raise InvalidDataError("Main hand must be 0 (left) or 1 (right)")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_string(locale))
        buffer.write(protocol.pack_byte(view_distance))
        buffer.write(protocol.write_varint(chat_mode))
        buffer.write(protocol.pack_bool(chat_colors))
        buffer.write(protocol.pack_ubyte(skin_parts))
        buffer.write(protocol.write_varint(main_hand))
        return self.write_packet(0x04, buffer)

    def chat_message(self, message: str) -> Coroutine[Any, Any, None]:
        """Send a chat message to the server. Message must be 256 characters or fewer."""
        if len(message) > 256:
            raise InvalidDataError("Message cannot exceed 256 characters")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_string(message))
        return self.write_packet(0x02, buffer)

    def chat_command_suggestion(self, text: str, assume_command: bool, has_position: bool,
                                looked_at_block: Optional[math.Vector3D[int]]) -> Coroutine[Any, Any, None]:
        """Send tab-complete request for command or chat suggestions."""
        if len(text) > 32767:
            raise InvalidDataError("Text cannot exceed 32767 characters")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_string(text))
        buffer.write(protocol.pack_bool(assume_command))
        buffer.write(protocol.pack_bool(has_position))
        if has_position and looked_at_block is not None:
            buffer.write(protocol.pack_position(looked_at_block.x, looked_at_block.y, looked_at_block.z))
        return self.write_packet(0x01, buffer)

    def enchant_item(self, window_id: int, enchantment: int) -> Coroutine[Any, Any, None]:
        """Send enchant item packet to apply enchantment from enchantment table."""
        if not (0 <= enchantment <= 2):
            raise InvalidDataError("Enchantment must be between 0 and 2")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_byte(window_id))
        buffer.write(protocol.pack_byte(enchantment))
        return self.write_packet(0x06, buffer)

    def click_window(self, window_id: int, slot: int, button: int, action_number: int,
                     mode: int, clicked_item: Optional[misc.ItemData] = None) -> Coroutine[Any, Any, None]:
        """Send click window packet when player clicks on a slot in a window."""
        if not (0 <= button <= 10):
            raise InvalidDataError("Button must be between 0 and 10")
        if not (0 <= mode <= 6):
            raise InvalidDataError("Mode must be between 0 and 6")
        
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_ubyte(window_id))
        buffer.write(protocol.pack_short(slot))
        buffer.write(protocol.pack_byte(button))
        buffer.write(protocol.pack_short(action_number))
        buffer.write(protocol.write_varint(mode))

        if clicked_item is None:
            # Empty slot - set item ID to -1
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

        return self.write_packet(0x07, buffer)

    def close_window(self, window_id: int) -> Coroutine[Any, Any, None]:
        """Send close window packet to server."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_byte(window_id))
        return self.write_packet(0x08, buffer)

    def spectate(self, target_uuid: str) -> Coroutine[Any, Any, None]:
        """Send spectate packet."""
        buffer = protocol.ProtocolBuffer()
        buffer.write(protocol.pack_uuid(target_uuid))
        return self.write_packet(0x1E, buffer)