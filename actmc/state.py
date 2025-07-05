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

from . import entities, math, protocol
from typing import TYPE_CHECKING
from .ui.chat import Message
from .ui import tablist, gui, bossbar, border, scoreboard, actionbar, advancement
from .user import User
from .chunk import *
from .utils import position_to_chunk_relative

from .entities import BLOCK_ENTITY_TYPES, MOB_ENTITY_TYPES, OBJECT_ENTITY_TYPES

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional
    from .tcp import TcpClient

import logging
_logger = logging.getLogger(__name__)

__all__ = ('ConnectionState',)

class ConnectionState:

    # Class-level packet parser cache for performance
    _packet_parsers: Dict[int, str] = {}

    def __init__(self, username: str, dispatcher: Callable[..., Any]) -> None:
        self.tcp: Optional[TcpClient] = None
        self._dispatch = dispatcher
        self._load_chunks = True
        # Player state
        self.username: Optional[str] = username
        self.uid: Optional[str] = None
        self.user: Optional[User] = None

        # Server information
        self.difficulty: Optional[int] = None
        self.max_players: Optional[int] = None
        self.world_type: Optional[str] = None
        self.world_age: Optional[int] = None
        self.time_of_day: Optional[int] = None

        # World state
        self.chunks: Dict[math.Vector2D, Chunk] = {}
        self.world_border: Optional[border.WorldBorder] = None

        self.entities: Dict[int, entities.entity.Entity] = {}
        self.tablist: Dict[str, tablist.TabPlayer] = {}
        self.windows: Dict[int, gui.Window] = {}
        self.boss_bars: Dict[str, bossbar.BossBar] = {}
        self.scoreboard_objectives: Dict[str, scoreboard.Scoreboard] = {}
        self.action_bar: actionbar.Title =  actionbar.Title()

        # Initialize packet parser cache
        if not self._packet_parsers:
            self._build_parser_cache()

    def clear(self) -> None:
        """Clear all connection state data."""
        self.tcp = None

        # Clear player state (keep username as it's set during init)
        self.uid = None
        self.user = None

        # Clear server information
        self.difficulty = None
        self.max_players = None
        self.world_type = None
        self.world_age = None
        self.time_of_day = None

        # Clear world state
        self.chunks.clear()
        self.world_border = None

        # Clear game objects
        self.entities.clear()
        self.tablist.clear()
        self.windows.clear()
        self.boss_bars.clear()
        self.scoreboard_objectives.clear()
        self.action_bar = actionbar.Title()

    @classmethod
    def _build_parser_cache(cls) -> None:
        """Build a performance cache mapping packet IDs to parser methods."""
        for attr_name in dir(cls):
            if attr_name.startswith('parse_0x'):
                try:
                    packet_id = int(attr_name[8:], 16)
                    cls._packet_parsers[packet_id] = attr_name
                except ValueError:
                    _logger.warning(f"Invalid packet parser method name: %s", attr_name)
                    continue

    # ------------------------------
    async def respawn(self) -> None:
        """Perform a respawn"""
        await self.tcp.client_status(0)

    async def send_client_settings(self, locale: str, view_distance: int, chat_mode: int, chat_colors: bool,
                                   cape: bool, jacket: bool, left_sleeve: bool, right_sleeve: bool, left_pants: bool,
                                   right_pants: bool, hat: bool, main_hand: int) -> None:
        """Send client settings to the server."""
        skin_parts = 0
        if cape:
            skin_parts |= 0x01
        if jacket:
            skin_parts |= 0x02
        if left_sleeve:
            skin_parts |= 0x04
        if right_sleeve:
            skin_parts |= 0x08
        if left_pants:
            skin_parts |= 0x10
        if right_pants:
            skin_parts |= 0x20
        if hat:
            skin_parts |= 0x40
        await self.tcp.client_settings(locale, view_distance, chat_mode, chat_colors, skin_parts, main_hand)


    async def open_advancement_tab(self, tab_id: str) -> None:
        """Open a specific advancement tab."""
        await self.tcp.advancement_tab(0, tab_id)

    async def close_advancement_tab(self) -> None:
        """Close the advancement tab."""
        await self.tcp.advancement_tab(1)

    async def set_resource_pack_status(self, result: int) -> None:
        """Respond to a resource pack request."""
        await self.tcp.resource_pack_status(result)

    # ============================== Network Operations ==============================

    async def send_initial_packets(self) -> None:
        await self.tcp.handshake_packet()
        await self.tcp.login_packet(self.username)

        # Performance warning for chunk loading
        if self._load_chunks:
            _logger.warning(
                "Chunk loading is enabled - may cause performance issues "
                "and increased memory usage on large worlds"
            )

        self._dispatch('handshake')

    # ============================== World State Management ==============================
    def get_block_state(self, position: math.Vector3D[int]) -> Optional[Block]:
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled - cannot query block states")

        chunk_coords, block_pos, section_y = position_to_chunk_relative(position)

        chunk = self.chunks.get(chunk_coords)
        if chunk is None:
            return None

        section = chunk.get_section(section_y)
        if section is None:
            return None

        return section.get_state(block_pos)

    def set_block_state(self, state: Block) -> None:
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled - cannot modify block states")

        chunk_coords, block_pos, section_y = position_to_chunk_relative(state.position)

        chunk = self.chunks.get(chunk_coords)
        if chunk is None:
            return

        section = chunk.get_section(section_y)
        if section is None:
            section = ChunkSection(math.Vector2D(0, 0))
            chunk.set_section(section_y, section)

        section.set_state(block_pos, state)

    def set_block_entity(self, pos: math.Vector3D[int], block_entity: entities.entity.BaseEntity[str]) -> None:
        if not self._load_chunks:
            raise RuntimeError("Chunk loading is disabled - cannot modify block entities")

        chunk_coords, block_pos, section_y = position_to_chunk_relative(pos)

        chunk = self.chunks.get(chunk_coords)
        if chunk is None:
            return

        section = chunk.get_section(section_y)
        if section is None:
            section = ChunkSection(math.Vector2D(0, 0))
            chunk.set_section(section_y, section)

        section.set_entity(block_pos, block_entity)

    @staticmethod
    def _create_block_entity(entity_id: str, data: Any) -> entities.entity.BaseEntity[str]:
        entity = BLOCK_ENTITY_TYPES.get(entity_id)

        if entity:
            return entity(entity_id, data)
        else:
            # Create generic entity for unknown types
            block_entity = entities.entity.BaseEntity(entity_id)
            if data:
                _logger.warning(f"Unknown block entity: %s, with data: %s", entity_id, data)
            return block_entity

    @staticmethod
    def _create_mob_entity(mob_type: int,
                           entity_id: int,
                           uuid: str,
                           position: math.Vector3D[float],
                           rotation: math.Rotation,
                           metadata: Dict[int, Dict[str, Any]]) -> Any:
        entity_class = MOB_ENTITY_TYPES.get(mob_type)
        if entity_class:
            return entity_class(entity_id, uuid, position, rotation, metadata)
        else:
            mob_entity = entities.entity.Entity(entity_id, uuid, position, rotation, metadata)
            if mob_type:
                _logger.warning(f"Unknown mob entity: %s, Type: '%s, With data: %s", entity_id, mob_entity,
                                metadata)
            return mob_entity

    @staticmethod
    def _create_object_entity(object_type: int,
                           entity_id: int,
                           uuid: str,
                           position: math.Vector3D[float],
                           rotation: math.Rotation,
                           data: int) -> Any:
        entity = OBJECT_ENTITY_TYPES.get(object_type)
        if entity:
            if isinstance(entity, dict):
                entity = entity.get(data)
            return entity(entity_id, uuid, position, rotation, {-1: {'value': data}})
        else:
            mob_entity = entities.entity.Entity(entity_id, uuid, position, rotation, {-1: {'value': data}})
            if object_type:
                _logger.warning(f"Unknown object entity: %s, Type: '%s', With data: %s", entity_id,
                                object_type, data)
            return mob_entity

    async def parse(self, packet_id: int, buffer: protocol.ProtocolBuffer) -> None:
        try:
            parser_name = self._packet_parsers.get(packet_id)
            if parser_name:
                func = getattr(self, parser_name)
                await func(buffer)

        except Exception as error:
            _logger.exception(f"Failed to parse packet 0x{packet_id:02X}: {error}")
            self._dispatch('error', packet_id, error)

    async def parse_0x23(self, buffer: protocol.ProtocolBuffer) -> None:
        # Parse player information
        entity_id = protocol.read_int(buffer)
        gamemode = protocol.read_ubyte(buffer)
        dimension = protocol.read_int(buffer)

        # Parse server information
        self.difficulty = protocol.read_ubyte(buffer)
        self.max_players = protocol.read_ubyte(buffer)
        self.world_type = protocol.read_string(buffer).lower()

        # Update player state
        self.user = User(entity_id, self.username, self.uid, state=self)
        self.user.gamemode = gamemode
        self.user.dimension = dimension
        # Player's inventory.
        self.windows[0] = gui.Window(0, 'container', Message('inventory'), 45)
        # Needed to update user properties and metadata.
        self.entities[entity_id] = self.user
        self._dispatch('join')

    async def parse_0x1a(self, buffer: protocol.ProtocolBuffer) -> None:
        reason = protocol.read_chat(buffer)
        message = Message(reason)

        self._dispatch('disconnect', message)

    async def parse_0x0f(self, buffer: protocol.ProtocolBuffer) -> None:
        chat = protocol.read_chat(buffer)
        position = protocol.read_ubyte(buffer)

        message = Message(chat)
        message_type = {0: 'chat_message', 1: 'system_message', 2: 'action_bar'}.get(position)
        if message_type:
            self._dispatch(message_type, message)
        else:
            _logger.warning(f"Unknown chat Position: %s, For message: %s", position, message)

    async def parse_0x0d(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Server Difficulty packet (0x0D)."""
        difficulty = protocol.read_ubyte(buffer)
        self.difficulty = difficulty

    async def parse_0x20(self, buffer: protocol.ProtocolBuffer) -> None:
        # Parse chunk metadata
        chunk_x = protocol.read_int(buffer)
        chunk_z = protocol.read_int(buffer)
        ground_up_continuous = protocol.read_bool(buffer)
        primary_bit_mask = protocol.read_varint(buffer)
        size = protocol.read_varint(buffer)
        chunk_buffer = protocol.read_byte_array(buffer, size)
        num_block_entities = protocol.read_varint(buffer)

        # Create and load chunk
        chunk = Chunk(math.Vector2D(chunk_x, chunk_z))
        chunk.load_chunk_column(ground_up_continuous, primary_bit_mask, chunk_buffer)

        # Process block entities
        for _ in range(num_block_entities):
            data = protocol.read_nbt(buffer)
            entity_pos = math.Vector3D(data.pop('x'), data.pop('y'), data.pop('z')).to_int()
            entity_id = data.pop('id')

            # Add block entity to appropriate chunk section
            chunk_coords, block_pos, section_y = position_to_chunk_relative(entity_pos)
            section = chunk.get_section(section_y)

            if section is None:
                section = ChunkSection(math.Vector2D(0, 0))
                chunk.set_section(section_y, section)

            block_entity = self._create_block_entity(entity_id, data)
            section.set_entity(block_pos, block_entity)

        # Store chunk if loading is enabled
        if self._load_chunks:
            self.chunks[math.Vector2D(chunk_x, chunk_z)] = chunk

        self._dispatch('chunk_load', chunk)

    async def parse_0x1d(self, buffer: protocol.ProtocolBuffer) -> None:
        chunk_x = protocol.read_int(buffer)
        chunk_z = protocol.read_int(buffer)
        pos = math.Vector2D(chunk_x, chunk_z)

        # Remove chunk from memory if loading is enabled
        if self._load_chunks:
            self.chunks.pop(pos, None)

        self._dispatch('chunk_unload', pos)

    async def parse_0x0a(self, buffer: protocol.ProtocolBuffer) -> None:
        location = protocol.read_position(buffer)
        action_id = protocol.read_ubyte(buffer)
        action_param = protocol.read_ubyte(buffer)
        block_type = protocol.read_varint(buffer)
        self._dispatch('block_action', location, action_id, action_param, block_type)

    async def parse_0x0b(self, buffer: protocol.ProtocolBuffer) -> None:
        position = protocol.read_position(buffer)
        block_state_id = protocol.read_varint(buffer)

        # Extract block type and metadata
        block_type = block_state_id >> 4
        block_meta = block_state_id & 0xF

        state = Block(block_type, block_meta, math.Vector3D(*position).to_int())

        if self._load_chunks:
            self.set_block_state(state)

        self._dispatch('block_change', state)

    async def parse_0x39(self, buffer: protocol.ProtocolBuffer) -> None:
        camera_entity_id = protocol.read_varint(buffer)

        if camera_entity_id in self.entities:
            self._dispatch('camera', self.entities[camera_entity_id])
        else:
            _logger.warning(f"Unknown entity ID: '%s', to handle camera", camera_entity_id)


    async def parse_0x10(self, buffer: protocol.ProtocolBuffer) -> None:
        chunk_x = protocol.read_int(buffer)
        chunk_z = protocol.read_int(buffer)
        record_count = protocol.read_varint(buffer)

        states = []

        for _ in range(record_count):
            horizontal = protocol.read_ubyte(buffer)
            y = protocol.read_ubyte(buffer)
            block_state_id = protocol.read_varint(buffer)

            # Extract relative coordinates within chunk
            rel_x = (horizontal >> 4) & 0x0F
            rel_z = horizontal & 0x0F

            # Calculate absolute world coordinates
            x = (chunk_x * 16) + rel_x
            z = (chunk_z * 16) + rel_z

            # Extract block type and metadata
            block_type = block_state_id >> 4
            block_meta = block_state_id & 0xF

            state = Block(block_type, block_meta, math.Vector3D(x, y, z).to_int())

            if self._load_chunks:
                self.set_block_state(state)

            states.append(state)

        self._dispatch('multi_block_change', states)

    async def parse_0x0c(self, buffer) -> None:
        bar_uuid = protocol.read_uuid(buffer)
        action = protocol.read_varint(buffer)
        uuid_str = str(bar_uuid)

        if action == 0:  # Add
            title = protocol.read_chat(buffer)
            health = protocol.read_float(buffer)
            color = protocol.read_varint(buffer)
            division = protocol.read_varint(buffer)
            flags = protocol.read_ubyte(buffer)

            boss_bar = bossbar.BossBar(bar_uuid, title, health, color, division, flags)
            self.boss_bars[uuid_str] = boss_bar
            self._dispatch('boss_bar_add', boss_bar)

        elif action == 1:  # Remove
            removed_bar = self.boss_bars.pop(uuid_str, None)
            self._dispatch('boss_bar_remove', removed_bar)

        else:
            bar = self.boss_bars.get(uuid_str)
            if not bar:
                _logger.warning(f"BossBar not found for UUID: %s", uuid_str)
                return

            if action == 2:
                bar.health = protocol.read_float(buffer)
                self._dispatch('boss_bar_update_health', bar)
            elif action == 3:
                bar.title = protocol.read_chat(buffer)
                self._dispatch('boss_bar_update_title', bar)
            elif action == 4:
                bar.color = protocol.read_varint(buffer)
                bar.division = protocol.read_varint(buffer)
                self._dispatch('boss_bar_update_style', bar)
            elif action == 5:
                bar.flags = protocol.read_ubyte(buffer)
                self._dispatch('boss_bar_update_flags', bar)

    async def parse_0x09(self, buffer: protocol.ProtocolBuffer) -> None:
        # Parse packet data
        _ = protocol.read_position(buffer)
        _ = protocol.read_ubyte(buffer)
        data = protocol.read_nbt(buffer)

        # Extract position and entity ID from NBT
        pos = math.Vector3D(data.pop('x'), data.pop('y'), data.pop('z'))
        entity_id = data.pop('id')

        block_entity = self._create_block_entity(entity_id, data)
        if self._load_chunks:
            self.set_block_entity(pos.to_int(), block_entity)

        self._dispatch('block_entity_update', pos, block_entity)

    # USER
    async def parse_0x41(self, data: protocol.ProtocolBuffer) -> None:
        self.user.health = protocol.read_float(data)
        self.user.food = protocol.read_varint(data)
        self.user.food_saturation = protocol.read_float(data)
        self._dispatch('player_health_update', self.user.health, self.user.food, self.user.food_saturation)

    async def parse_0x40(self, data: protocol.ProtocolBuffer) -> None:
        self.user.experience_bar = protocol.read_float(data)
        self.user.level = protocol.read_varint(data)
        self.user.total_experience = protocol.read_varint(data)
        self._dispatch('player_experience_set', self.user.level, self.user.total_experience, self.user.experience_bar)

    async def parse_0x21(self, buffer: protocol.ProtocolBuffer) -> None:
        effect_id = protocol.read_int(buffer)
        location = protocol.read_position(buffer)
        data = protocol.read_int(buffer)
        disable_relative_volume = protocol.read_bool(buffer)

        self._dispatch('effect', effect_id, location, data, disable_relative_volume)

    async def parse_0x3a(self, data: protocol.ProtocolBuffer) -> None:
        self.user.held_slot = protocol.read_byte(data)
        self._dispatch('held_slot_change', self.user.held_slot)


    async def parse_0x1e(self, data: protocol.ProtocolBuffer) -> None:
        reason = protocol.read_ubyte(data)
        value = protocol.read_float(data)

        if reason == 3:
            self.user.gamemode =int(value)

        self._dispatch('game_state_change', reason, value)

    async def parse_0x2f(self, data: protocol.ProtocolBuffer) -> None:
        x = protocol.read_double(data)
        y = protocol.read_double(data)
        z = protocol.read_double(data)
        yaw = protocol.read_float(data)
        pitch = protocol.read_float(data)
        flags = protocol.read_ubyte(data)
        teleport_id = protocol.read_varint(data)

        if flags & 0x01:
            x += self.user.position.x
        if flags & 0x02:
            y += self.user.position.y
        if flags & 0x04:
            z += self.user.position.z
        if flags & 0x08:
            yaw += self.user.rotation.yaw
        if flags & 0x10:
            pitch += self.user.rotation.pitch

        self.user.position = math.Vector3D(x, y, z)
        self.user.rotation = math.Rotation(yaw, pitch)

        await self.tcp.player_teleport_confirmation(teleport_id)
        self._dispatch('player_position_and_look', self.user.position, self.user.rotation)

    async def parse_0x22(self, data: protocol.ProtocolBuffer) -> None:
        particle_id = protocol.read_int(data)
        long_distance = protocol.read_bool(data)
        x = protocol.read_float(data)
        y = protocol.read_float(data)
        z = protocol.read_float(data)
        offset_x = protocol.read_float(data)
        offset_y = protocol.read_float(data)
        offset_z = protocol.read_float(data)
        particle_data = protocol.read_float(data)
        particle_count = protocol.read_int(data)

        # Read remaining data as variable-length array
        data_array = []
        while data.remaining() > 0:
            data_array.append(protocol.read_varint(data))

        position = math.Vector3D(x, y, z)
        offset = math.Vector3D(offset_x, offset_y, offset_z)

        self._dispatch('particle', particle_id, long_distance, position, offset,
                       particle_data, particle_count, data_array)

    async def parse_0x24(self, data: protocol.ProtocolBuffer) -> None:
        item_damage = protocol.read_varint(data)
        scale = protocol.read_byte(data)
        tracking_position = protocol.read_bool(data)
        icon_count = protocol.read_varint(data)

        # Read icons
        icons = []
        for _ in range(icon_count):
            direction_and_type = protocol.read_byte(data)
            icon_type = (direction_and_type & 0xF0) >> 4
            direction = direction_and_type & 0x0F
            x = protocol.read_byte(data)
            z = protocol.read_byte(data)
            icons.append({
                'type': icon_type,
                'direction': direction,
                'x': x,
                'z': z
            })

        columns = protocol.read_byte(data)

        # Optional fields only if columns > 0
        rows = None
        x_offset = None
        z_offset = None
        map_data = None

        if columns > 0:
            rows = protocol.read_byte(data)
            x_offset = protocol.read_byte(data)
            z_offset = protocol.read_byte(data)
            length = protocol.read_varint(data)

            map_data = []
            for _ in range(length):
                map_data.append(protocol.read_ubyte(data))

        self._dispatch('map', item_damage, scale, tracking_position, icons, columns, rows, x_offset, z_offset, map_data)

    async def parse_0x46(self, data: protocol.ProtocolBuffer) -> None:
        x, y, z = protocol.read_position(data)
        self.user.spawn_point = math.Vector3D(x, y, z)
        self._dispatch('spawn_position', self.user.spawn_point)

    async def parse_0x35(self, data: protocol.ProtocolBuffer) -> None:
        dimension = protocol.read_int(data)
        difficulty = protocol.read_ubyte(data)
        gamemode = protocol.read_ubyte(data)
        level_type = protocol.read_string(data)

        self.user.dimension = dimension
        self.difficulty = difficulty
        self.user.gamemode = gamemode
        self.world_type = level_type

        self._dispatch('respawn', dimension, difficulty, gamemode, level_type)

    async def parse_0x25(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)

        if entity_id in self.entities:
            self._dispatch('entity_keep_alive', self.entities[entity_id])
        else:
            _logger.warning(f"Entity keep-alive received for untracked entity ID: %s", entity_id)

    async def parse_0x2a(self, buffer: protocol.ProtocolBuffer) -> None:
        location = protocol.read_position(buffer)
        self._dispatch('open_sign_editor', math.Vector3D(*location))

    async def parse_0x2d(self, buffer: protocol.ProtocolBuffer) -> None:
        event = protocol.read_varint(buffer)

        if event == 0:
            self._dispatch('enter_combat')
        elif event == 1:
            duration = protocol.read_varint(buffer)
            entity_id = protocol.read_int(buffer)
            entity = self.entities.get(entity_id)

            if not entity:
                _logger.warning(f"Combat ended for untracked entity ID: %s", entity_id)
                return

            self._dispatch('end_combat', entity, duration)
        elif event == 2:
            player_id = protocol.read_varint(buffer)
            entity_id = protocol.read_int(buffer)
            message = protocol.read_chat(buffer)

            player = self.entities.get(player_id)
            entity = self.entities.get(entity_id)

            if not player:
                _logger.warning(f"Entity death for untracked player ID: %s", player_id)
                return

            if not entity:
                _logger.warning(f"Entity death for untracked entity ID: %s", entity_id)
                return

            self._dispatch('player_death', player, entity, Message(message))

    async def parse_0x18(self, buffer: protocol.ProtocolBuffer) -> None:
        channel = protocol.read_string(buffer)
        self._dispatch('plugin_message', channel, buffer.getvalue())

    async def parse_0x19(self, buffer: protocol.ProtocolBuffer) -> None:
        sound_name = protocol.read_string(buffer)
        sound_category = protocol.read_varint(buffer)

        x = protocol.read_int(buffer) / 8.0
        y = protocol.read_int(buffer) / 8.0
        z = protocol.read_int(buffer) / 8.0
        position = math.Vector3D(x, y, z)

        volume = protocol.read_float(buffer)
        pitch = protocol.read_float(buffer)

        self._dispatch('named_sound_effect', sound_name, sound_category, position, volume, pitch)

    async def parse_0x07(self, buffer: protocol.ProtocolBuffer) -> None:
        count = protocol.read_varint(buffer)
        statistics = []

        for _ in range(count):
            name = protocol.read_string(buffer)
            value = protocol.read_varint(buffer)
            statistics.append((name, value))

        self._dispatch('statistics', statistics)

    async def parse_0x06(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        animation_id = protocol.read_ubyte(buffer)

        if entity_id in self.entities:
            entity = self.entities[entity_id]
            self._dispatch('entity_animation', entity, animation_id)

    async def parse_0x08(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        location = protocol.read_position(buffer)
        destroy_stage = protocol.read_byte(buffer)

        if entity_id in self.entities:
            entity = self.entities[entity_id]
            self._dispatch('block_break_animation', entity, location, destroy_stage)

    async def parse_0x2b(self, data: protocol.ProtocolBuffer) -> None:
        window_id = protocol.read_byte(data)
        recipe = protocol.read_varint(data)

        if window_id in self.windows:
            window = self.windows[window_id]
            self._dispatch('craft_recipe_response', window, recipe)
        else:
            _logger.warning(f"Received craft recipe response for unknown window ID: %s", window_id)

    async def parse_0x2e(self, buffer: protocol.ProtocolBuffer) -> None:
        action = protocol.read_varint(buffer)
        number_of_players = protocol.read_varint(buffer)

        players_affected = []

        for _ in range(number_of_players):
            player_uuid = protocol.read_uuid(buffer)
            uuid_str = str(player_uuid)

            if action == 0:  # add player
                name = protocol.read_string(buffer, 16)
                number_of_properties = protocol.read_varint(buffer)

                properties = []
                for _ in range(number_of_properties):
                    property_name = protocol.read_string(buffer, 32767)
                    value = protocol.read_string(buffer, 32767)
                    is_signed = protocol.read_bool(buffer)
                    signature = protocol.read_string(buffer, 32767) if is_signed else None
                    properties.append(tablist.Property(property_name, value, signature))

                gamemode = protocol.read_varint(buffer)
                ping = protocol.read_varint(buffer)
                has_display_name = protocol.read_bool(buffer)
                display_name = Message(protocol.read_chat(buffer)) if has_display_name else None

                player = tablist.TabPlayer(
                    name=name,
                    properties=properties,
                    gamemode=gamemode,
                    ping=ping,
                    display_name=display_name
                )
                self.tablist[uuid_str] = player
                players_affected.append(player)

            elif action == 1:  # update gamemode
                gamemode = protocol.read_varint(buffer)
                if uuid_str in self.tablist:
                    player = self.tablist[uuid_str]
                    player.gamemode = gamemode
                    players_affected.append(player)

            elif action == 2:  # update latency
                ping = protocol.read_varint(buffer)
                if uuid_str in self.tablist:
                    player = self.tablist[uuid_str]
                    player.ping = ping
                    players_affected.append(player)

            elif action == 3:  # update display name
                has_display_name = protocol.read_bool(buffer)
                display_name = protocol.read_chat(buffer) if has_display_name else None
                if uuid_str in self.tablist:
                    player = self.tablist[uuid_str]
                    player.display_name = display_name
                    players_affected.append(player)

            elif action == 4:  # remove player
                if uuid_str in self.tablist:
                    player = self.tablist[uuid_str]
                    del self.tablist[uuid_str]
                    players_affected.append(player)

        if players_affected:
            action_names = {
                0: 'players_add',
                1: 'players_gamemode_update',
                2: 'players_ping_update',
                3: 'players_display_name_update',
                4: 'players_remove'
            }
            event_name = action_names.get(action)
            if event_name:
                self._dispatch(event_name, players_affected)

    async def parse_0x05(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        player_uuid = protocol.read_uuid(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        yaw = protocol.read_angle(buffer)
        pitch = protocol.read_angle(buffer)
        metadata = protocol.read_entity_metadata(buffer)
        player = entities.player.Player(entity_id, player_uuid, math.Vector3D(x, y, z), math.Rotation(yaw, pitch),
                                        metadata, self.tablist)
        self.entities[entity_id] = player
        self._dispatch('spawn_player', player)

    async def parse_0x0e(self, buffer: protocol.ProtocolBuffer) -> None:
        count = protocol.read_varint(buffer)
        matches = [protocol.read_string(buffer) for _ in range(count)]
        self._dispatch('tab_complete', matches)

    async def parse_0x4e(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        num_properties = protocol.read_int(buffer)

        properties = {}
        for _ in range(num_properties):
            key = protocol.read_string(buffer, max_length=64)
            value = protocol.read_double(buffer)
            num_modifiers = protocol.read_varint(buffer)

            modifiers = {}
            for _ in range(num_modifiers):
                modifier_uuid = protocol.read_uuid(buffer)
                amount = protocol.read_double(buffer)
                operation = protocol.read_byte(buffer)
                modifiers[modifier_uuid] = {'amount': amount, 'operation': operation}
            properties[key] = {'value': value, 'modifiers': modifiers}

        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.update_properties(properties)
            self._dispatch('entity_properties', entity, properties)
        else:
            _logger.warning(f"Unknown entity ID: '%s', with properties: %s", entity_id, properties)

    async def parse_0x4c(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        yaw = protocol.read_angle(buffer)
        pitch = protocol.read_angle(buffer)
        on_ground = protocol.read_bool(buffer)

        if entity_id in self.entities:
            self.entities[entity_id].position = math.Vector3D(x, y, z)
            self.entities[entity_id].rotation = math.Rotation(yaw, pitch)
            self._dispatch('entity_teleport', self.entities[entity_id], on_ground)



    async def parse_0x29(self, buffer: protocol.ProtocolBuffer) -> None:
        """Vehicle Move (Packet ID: 0x29)"""
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        yaw = protocol.read_float(buffer)
        pitch = protocol.read_float(buffer)
        self._dispatch('vehicle_move', math.Vector3D(x, y, z), math.Rotation(yaw, pitch))

    async def parse_0x26(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        delta_x = protocol.read_short(buffer)
        delta_y = protocol.read_short(buffer)
        delta_z = protocol.read_short(buffer)
        on_ground = protocol.read_bool(buffer)

        delta = math.Vector3D(delta_x / 4096.0, delta_y / 4096.0, delta_z / 4096.0)

        # Update entity if it exists
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            current_pos = entity.position

            # Apply relative movement
            new_x = current_pos.x + delta.x
            new_y = current_pos.y + delta.y
            new_z = current_pos.z + delta.z

            entity.position = math.Vector3D(new_x, new_y, new_z)
            self._dispatch('entity_move', entity, delta, on_ground)

    async def parse_0x27(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        delta_x_raw = protocol.read_short(buffer)  # Change in position * 4096
        delta_y_raw = protocol.read_short(buffer)
        delta_z_raw = protocol.read_short(buffer)
        yaw = protocol.read_angle(buffer)  # Absolute yaw
        pitch = protocol.read_angle(buffer)  # Absolute pitch
        on_ground = protocol.read_bool(buffer)

        # Convert raw delta values to actual coordinate changes
        delta_x = delta_x_raw / 4096.0
        delta_y = delta_y_raw / 4096.0
        delta_z = delta_z_raw / 4096.0

        delta = math.Vector3D(delta_x, delta_y, delta_z)

        # Update entity if it exists
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            current_pos = entity.position

            # Apply relative movement
            new_x = current_pos.x + delta.x
            new_y = current_pos.y + delta.y
            new_z = current_pos.z + delta.z

            entity.position = math.Vector3D(new_x, new_y, new_z)
            entity.rotation = math.Rotation(yaw, pitch)

            self._dispatch('entity_move_look', entity, delta, on_ground)

    async def parse_0x28(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        yaw = protocol.read_angle(buffer)
        pitch = protocol.read_angle(buffer)
        on_ground = protocol.read_bool(buffer)

        # Update entity if it exists
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.rotation = math.Rotation(yaw, pitch)
            self._dispatch('entity_look', entity, on_ground)

    async def parse_0x36(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        head_yaw = protocol.read_angle(buffer)

        # Update entity if it exists
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.rotation.yaw = head_yaw
            self._dispatch('entity_head_look', entity)

    async def parse_0x03(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        entity_uuid = protocol.read_uuid(buffer)
        mob_type = protocol.read_varint(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        yaw = protocol.read_angle(buffer)
        pitch = protocol.read_angle(buffer)
        head_pitch = protocol.read_angle(buffer)
        # Entity Velocity
        v_x = protocol.read_short(buffer)
        v_y = protocol.read_short(buffer)
        v_z = protocol.read_short(buffer)
        metadata = protocol.read_entity_metadata(buffer)

        mob_entity = self._create_mob_entity(mob_type, entity_id, entity_uuid, math.Vector3D(x, y, z),
                                             math.Rotation(yaw, pitch), metadata)
        self.entities[entity_id] = mob_entity
        velocity = math.Vector3D(v_x, v_y, v_z)
        self._dispatch('spawn_mob', mob_entity, math.Rotation(0, head_pitch), velocity)


    async def parse_0x3e(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        v_x = protocol.read_short(buffer) / 8000.0 * 20
        v_y = protocol.read_short(buffer) / 8000.0 * 20
        v_z = protocol.read_short(buffer) / 8000.0 * 20

        if entity_id in self.entities:
            self._dispatch('entity_velocity', self.entities[entity_id],  math.Vector3D(v_x, v_y, v_z))

    async def parse_0x3c(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        metadata = protocol.read_entity_metadata(buffer)

        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.update_metadata(metadata)
            self._dispatch('entity_metadata', entity, metadata)

    async def parse_0x3d(self, buffer: protocol.ProtocolBuffer) -> None:
        attached_entity_id = protocol.read_int(buffer)
        holding_entity_id = protocol.read_int(buffer)
        self._dispatch('entity_leash', attached_entity_id, holding_entity_id)

    async def parse_0x3f(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        slot_index = protocol.read_varint(buffer)
        item_data = protocol.read_slot(buffer)

        if entity_id in self.entities:
            entity = self.entities[entity_id]

            if not isinstance(entity, entities.entity.Living):
                _logger.debug(f"Entity {entity_id} is not a Living entity, skipping equipment")
                return

            slot = gui.Slot(slot_index)
            if item_data:
                slot.item = entities.misc.Item(
                    item_data['item_id'],
                    item_data['item_count'],
                    item_data['item_damage'],
                    item_data['nbt'])
            else:
                slot.item = None

            entity.set_equipment(slot)
            self._dispatch('entity_equipment', entity, slot)

    async def parse_0x32(self, buffer: protocol.ProtocolBuffer) -> None:
        count = protocol.read_varint(buffer)
        entity_ids = [protocol.read_varint(buffer) for _ in range(count)]
        destroyed = {eid: self.entities.pop(eid, None) for eid in entity_ids if eid in self.entities}

        if destroyed:
            self._dispatch('destroy_entities', list(destroyed.values()))

    async def parse_0x1b(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_int(buffer)
        status = protocol.read_byte(buffer)

        if entity_id in self.entities:
            self._dispatch('entity_status', self.entities[entity_id], status)
        else:
            _logger.warning(f"Unknown entity ID: '%s', with status: %s", entity_id, status)

    async def parse_0x1c(self, buffer: protocol.ProtocolBuffer) -> None:
        x = protocol.read_float(buffer)
        y = protocol.read_float(buffer)
        z = protocol.read_float(buffer)
        position = math.Vector3D(x, y, z)

        radius = protocol.read_float(buffer)

        record_count = protocol.read_int(buffer)
        records = [(protocol.read_byte(buffer), protocol.read_byte(buffer),
                    protocol.read_byte(buffer)) for _ in range(record_count)]

        motion_x = protocol.read_float(buffer)
        motion_y = protocol.read_float(buffer)
        motion_z = protocol.read_float(buffer)
        player_motion = math.Vector3D(motion_x, motion_y, motion_z)

        self._dispatch('explosion', position,radius, records, player_motion)

    async def parse_0x00(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        entity_uuid = protocol.read_uuid(buffer)
        obj_type = protocol.read_byte(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        pitch = protocol.read_angle(buffer)
        yaw = protocol.read_angle(buffer)
        data = protocol.read_int(buffer)
        # 20 ticks.
        vel_x = protocol.read_short(buffer) / 8000.0 * 20
        vel_y = protocol.read_short(buffer) / 8000.0 * 20
        vel_z = protocol.read_short(buffer) / 8000.0 * 20

        velocity = math.Vector3D(vel_x, vel_y, vel_z)
        entity = self._create_object_entity(obj_type, entity_id, entity_uuid, math.Vector3D(x, y, z),
                                             math.Rotation(yaw, pitch), data)
        self.entities[entity_id] = entity
        self._dispatch('spawn_object', entity, velocity)


    async def parse_0x04(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        entity_uuid = protocol.read_uuid(buffer)
        title = protocol.read_string(buffer, max_length=13)
        position = protocol.read_position(buffer)
        direction = protocol.read_byte(buffer)

        entity = self._create_object_entity(83, entity_id, entity_uuid, math.Vector3D(*position),
                                            math.Rotation(0, 0), direction)
        entity.set_painting_type(title)
        self.entities[entity_id] = entity
        self._dispatch('spawn_painting', entity)

    async def parse_0x47(self, buffer: protocol.ProtocolBuffer) -> None:
        world_age = protocol.read_long(buffer)
        time_of_day = protocol.read_long(buffer)
        self.world_age = world_age
        self.time_of_day = time_of_day
        self._dispatch('time_update', world_age, time_of_day)


    async def parse_0x02(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        entity_type = protocol.read_byte(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)

        entity = self._create_object_entity(200, entity_id, '00000000-0000-0000-0000-000000000000',
                                            math.Vector3D(x, y, z),
                                            math.Rotation(0, 0), entity_type)
        self._dispatch('spawn_global_entity', entity)

    async def parse_0x01(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        x = protocol.read_double(buffer)
        y = protocol.read_double(buffer)
        z = protocol.read_double(buffer)
        count = protocol.read_short(buffer)

        entity = self._create_object_entity(69, entity_id, '00000000-0000-0000-0000-000000000000',
                                            math.Vector3D(x, y, z),
                                            math.Rotation(0, 0), count)
        self.entities[entity_id] = entity
        self._dispatch('spawn_experience_orb', entity)

    async def parse_0x11(self, buffer: protocol.ProtocolBuffer) -> None:
        window_id = protocol.read_byte(buffer)
        action_number = protocol.read_short(buffer)
        accepted = protocol.read_bool(buffer)
        await self.tcp.confirm_window_transaction(window_id, action_number, accepted)
        self._dispatch('transaction_confirmed', window_id, action_number, accepted)

    async def parse_0x12(self, buffer: protocol.ProtocolBuffer) -> None:
        window_id = protocol.read_ubyte(buffer)

        if window_id in self.windows:
            del self.windows[window_id]

        self._dispatch('window_closed', window_id)

    async def parse_0x13(self, buffer: protocol.ProtocolBuffer) -> None:
        window_id = protocol.read_ubyte(buffer)
        window_type = protocol.read_string(buffer, max_length=32)
        window_title = protocol.read_chat(buffer)
        number_of_slots = protocol.read_ubyte(buffer)

        window = gui.Window(window_id, window_type, Message(window_title), number_of_slots)

        if window_type == 'EntityHorse':
            # Custom property.
            entity_id = protocol.read_int(buffer)
            window.set_property(-1, entity_id)

        self.windows[window_id] = window
        self._dispatch('window_opened', window)

    async def parse_0x14(self, buffer: protocol.ProtocolBuffer) -> None:
        window_id = protocol.read_ubyte(buffer)
        count = protocol.read_short(buffer)

        if window_id not in self.windows:
            window = gui.Window(window_id, 'container', Message('inventory'), count)
            self.windows[window_id] = window
            return

        window = self.windows[window_id]

        for i in range(count):
            slot_data = protocol.read_slot(buffer)
            if slot_data is not None:
                window.set_slot(i, slot_data)

        self._dispatch('window_items_updated', window)

    async def parse_0x15(self, buffer: protocol.ProtocolBuffer) -> None:
        window_id = protocol.read_ubyte(buffer)
        property_id = protocol.read_short(buffer)
        value = protocol.read_short(buffer)

        if window_id not in self.windows:
            _logger.warning( f"Received property update for unknown window ID: %s", window_id)
            return

        window = self.windows[window_id]
        window.set_property(property_id, value)
        self._dispatch('window_property_changed', window, property_id, value)

    async def parse_0x16(self, buffer: protocol.ProtocolBuffer) -> None:
        window_id = protocol.read_byte(buffer)
        slot_index = protocol.read_short(buffer)
        slot_data = protocol.read_slot(buffer)

        # Handle special window IDs
        if window_id == -1:
            # Cursor slot (dragged item)
            self._dispatch('cursor_slot_changed', slot_data)
        elif window_id == -2:
            if 0 in self.windows:
                updated_slot = self.windows[0].set_slot(slot_index, slot_data)
                self._dispatch('inventory_slot_changed', updated_slot)
            else:
                _logger.warning("Received inventory update but no player inventory window found")
        else:
            # Regular window slot update
            if window_id not in self.windows:
                _logger.warning(f"Received slot update for unknown window ID: %s", window_id)
                return

            window = self.windows[window_id]
            updated_slot = window.set_slot(slot_index, slot_data)
            self._dispatch('window_slot_changed', window, updated_slot)

    async def parse_0x30(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        location = protocol.read_position(buffer)

        if entity_id in self.entities:
            self._dispatch('use_bed', self.entities[entity_id], math.Vector3D(*location))
        else:
            _logger.warning(f"Untracked entity ID: %s, used bed", entity_id)

    async def parse_0x17(self, buffer: protocol.ProtocolBuffer) -> None:
        item_id = protocol.read_varint(buffer)
        cooldown_ticks = protocol.read_varint(buffer)

        self._dispatch('set_cooldown', item_id, cooldown_ticks)

    async def parse_0x4f(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        effect_id = protocol.read_byte(buffer)
        amplifier = protocol.read_byte(buffer)
        duration = protocol.read_varint(buffer)
        flags = protocol.read_byte(buffer)

        is_ambient = bool(flags & 0x01)
        show_particles = bool(flags & 0x02)

        if entity_id in self.entities:
            self._dispatch( 'entity_effect', self.entities[entity_id], effect_id,  amplifier, duration, is_ambient,
                            show_particles)
        else:
            _logger.warning(f"Untracked entity ID: %s, effect added ID: %s", entity_id, effect_id)

    async def parse_0x33(self, buffer: protocol.ProtocolBuffer) -> None:
        entity_id = protocol.read_varint(buffer)
        effect_id = protocol.read_byte(buffer)

        if entity_id in self.entities:
            self._dispatch('remove_entity_effect', self.entities[entity_id], effect_id)
        else:
            _logger.warning(f"Untracked entity ID: %s, effect removed", entity_id)

    async def parse_0x34(self, buffer: protocol.ProtocolBuffer) -> None:
        url = protocol.read_string(buffer)
        hash_ = protocol.read_string(buffer)

        self._dispatch('resource_pack_send', url, hash_)

    async def parse_0x31(self, buffer: protocol.ProtocolBuffer) -> None:
        action = protocol.read_varint(buffer)
        crafting_book_open = protocol.read_bool(buffer)
        filtering_craftable = protocol.read_bool(buffer)

        recipe_count_1 = protocol.read_varint(buffer)
        recipes_1 = [protocol.read_varint(buffer) for _ in range(recipe_count_1)]

        recipes_2 = None
        if action == 0:  # Init mode
            recipe_count_2 = protocol.read_varint(buffer)
            recipes_2 = [protocol.read_varint(buffer) for _ in range(recipe_count_2)]

        self._dispatch('unlock_recipes', action, crafting_book_open, filtering_craftable, recipes_1, recipes_2)

    async def parse_0x2c(self, data: protocol.ProtocolBuffer) -> None:
        flags = protocol.read_byte(data)
        flying_speed = protocol.read_float(data)
        fov_modifier = protocol.read_float(data)

        self.user.invulnerable =  bool(flags & 0x01)
        self.user.flying = bool(flags & 0x02)
        self.user.allow_flying = bool(flags & 0x04)
        self.user.creative_mode =  bool(flags & 0x08)
        self.user.flying_speed = flying_speed
        self.user.fov_modifier = fov_modifier
        self._dispatch('player_abilities_change')

    async def parse_0x38(self, buffer: protocol.ProtocolBuffer) -> None:
        """World Border (Packet ID: 0x38)"""
        action = protocol.read_varint(buffer)

        if action == 0:
            diameter = protocol.read_double(buffer)
            if self.world_border is not None:
                self.world_border.set_size(diameter)
            self._dispatch('world_border_set_size', diameter)

        elif action == 1:
            old_diameter = protocol.read_double(buffer)
            new_diameter = protocol.read_double(buffer)
            speed = protocol.read_varlong(buffer)
            if self.world_border is not None:
                self.world_border.lerp_size(old_diameter, new_diameter, speed)
            self._dispatch('world_border_lerp_size', old_diameter, new_diameter, speed)

        elif action == 2:
            x = protocol.read_double(buffer)
            z = protocol.read_double(buffer)
            if self.world_border is not None:
                self.world_border.set_center(math.Vector2D(x, z))
            center = math.Vector3D(x, 0, z)
            self._dispatch('world_border_set_center', center)

        elif action == 3:
            x = protocol.read_double(buffer)
            z = protocol.read_double(buffer)
            old_diameter = protocol.read_double(buffer)
            new_diameter = protocol.read_double(buffer)
            speed = protocol.read_varlong(buffer)
            portal_teleport_boundary = protocol.read_varint(buffer)
            warning_time = protocol.read_varint(buffer)
            warning_blocks = protocol.read_varint(buffer)
            self.world_border = border.WorldBorder(
                center=math.Vector2D(x, z),
                current_diameter=old_diameter,
                target_diameter=new_diameter,
                speed=speed,
                portal_teleport_boundary=portal_teleport_boundary,
                warning_time=warning_time,
                warning_blocks=warning_blocks
            )
            self._dispatch('world_border_initialize', self.world_border)

        elif action == 4:
            warning_time = protocol.read_varint(buffer)
            if self.world_border is not None:
                self.world_border.set_warning_time(warning_time)
            self._dispatch('world_border_set_warning_time', warning_time)

        elif action == 5:
            warning_blocks = protocol.read_varint(buffer)
            if self.world_border is not None:
                self.world_border.set_warning_blocks(warning_blocks)
            self._dispatch('world_border_set_warning_blocks', warning_blocks)

    # Enhanced packet parsing methods
    async def parse_0x3b(self, data: protocol.ProtocolBuffer) -> None:
        position = protocol.read_byte(data)
        score_name = protocol.read_string(data, 16)

        for objective in self.scoreboard_objectives.values():
            objective.set_displayed(False)

        if score_name and score_name in self.scoreboard_objectives:
            self.scoreboard_objectives[score_name].set_displayed(True, position)
        self._dispatch('scoreboard_display', position, score_name)

    async def parse_0x42(self, data: protocol.ProtocolBuffer) -> None:
        objective_name = protocol.read_string(data, 16)
        mode = protocol.read_byte(data)

        if mode == 0:
            objective_value = protocol.read_string(data, 32)
            score_type = protocol.read_string(data, 16)

            objective = scoreboard.Scoreboard(objective_name, objective_value, score_type)
            self.scoreboard_objectives[objective_name] = objective

        elif mode == 1:
            self.scoreboard_objectives.pop(objective_name, None)

        elif mode == 2:
            objective_value = protocol.read_string(data, 32)
            score_type = protocol.read_string(data, 16)

            if objective_name in self.scoreboard_objectives:
                self.scoreboard_objectives[objective_name].update_display_info(objective_value, score_type)

        self._dispatch('scoreboard_objective', objective_name, mode)

    async def parse_0x45(self, data: protocol.ProtocolBuffer) -> None:
        entity_name = protocol.read_string(data, 40)
        action = protocol.read_byte(data)
        objective_name = protocol.read_string(data, 16)

        value = None
        if action != 1:
            value = protocol.read_varint(data)

        if objective_name in self.scoreboard_objectives:
            objective = self.scoreboard_objectives[objective_name]
            if action == 0:
                objective.set_score(entity_name, value)
            elif action == 1:
                objective.remove_score(entity_name)

        self._dispatch('scoreboard_score_update', entity_name, objective_name, action, value)

    async def parse_0x48(self, data: protocol.ProtocolBuffer) -> None:
        action = protocol.read_varint(data)

        if action == 0:
            title_text = protocol.read_string(data)
            self.action_bar.set_title(title_text)
            self.action_bar.show()
            self._dispatch('title_set_title', title_text)

        elif action == 1:
            subtitle_text = protocol.read_string(data)
            self.action_bar.set_subtitle(subtitle_text)
            self.action_bar.show()
            self._dispatch('title_set_subtitle', subtitle_text)

        elif action == 2:
            action_bar_text = protocol.read_string(data)
            self.action_bar.set_action_bar(action_bar_text)
            self._dispatch('title_set_action_bar', action_bar_text)

        elif action == 3:
            fade_in = protocol.read_int(data)
            stay = protocol.read_int(data)
            fade_out = protocol.read_int(data)
            self.action_bar.set_times(fade_in, stay, fade_out)
            self.action_bar.show()
            self._dispatch('title_set_times', fade_in, stay, fade_out)

        elif action == 4:
            self.action_bar.hide()
            self._dispatch('title_hide')

        elif action == 5:
            self.action_bar.reset()
            self._dispatch('title_reset')

    async def parse_0x49(self, buffer: protocol.ProtocolBuffer) -> None:
        sound_id = protocol.read_varint(buffer)
        category = protocol.read_varint(buffer)
        x = protocol.read_int(buffer)
        y = protocol.read_int(buffer)
        z = protocol.read_int(buffer)
        volume = protocol.read_float(buffer)
        pitch = protocol.read_float(buffer)

        position = math.Vector3D(x, y, z)
        self._dispatch('sound_effect', sound_id, category, position, volume, pitch)

    async def parse_0x4a(self, buffer: protocol.ProtocolBuffer) -> None:
        header = protocol.read_chat(buffer)
        footer = protocol.read_chat(buffer)
        self._dispatch('player_list_header_footer', Message(header), Message(footer))

    async def parse_0x4b(self, buffer: protocol.ProtocolBuffer) -> None:
        """Handle Collect Item packet (0x4B)."""
        collected_entity_id = protocol.read_varint(buffer)
        collector_entity_id = protocol.read_varint(buffer)
        pickup_count = protocol.read_varint(buffer)

        if collected_entity_id not in self.entities:
            _logger.warning("CollectItem: Unknown collected entity ID: %s", collected_entity_id)
            return

        if collector_entity_id not in self.entities:
            _logger.warning("CollectItem: Unknown collector entity ID: %s", collector_entity_id)
            return

        self._dispatch('collect_item', self.entities[collected_entity_id], pickup_count,
                       self.entities[collector_entity_id])

    async def parse_0x4d(self, buffer: protocol.ProtocolBuffer) -> None:
        reset_clear = protocol.read_bool(buffer)
        mapping_size = protocol.read_varint(buffer)
        advancements = {}

        for _ in range(mapping_size):
            advancement_id = protocol.read_string(buffer)
            advancement_dict = protocol.read_advancement(buffer)

            display_data = None
            if advancement_dict['display_data'] is not None:
                display_data = advancement.AdvancementDisplay(
                    advancement_dict['display_data']['title'],
                    advancement_dict['display_data']['description'],
                    advancement_dict['display_data']['icon'],
                    advancement_dict['display_data']['frame_type'],
                    advancement_dict['display_data']['flags'],
                    advancement_dict['display_data']['background_texture'],
                    advancement_dict['display_data']['x_coord'],
                    advancement_dict['display_data']['y_coord']
                )

            ad = advancement.Advancement(
                advancement_dict['parent_id'],
                display_data,
                advancement_dict['criteria'],
                advancement_dict['requirements']
            )
            advancements[advancement_id] = ad

        removed_list_size = protocol.read_varint(buffer)
        removed_advancements = []
        for _ in range(removed_list_size):
            removed_id = protocol.read_string(buffer)
            removed_advancements.append(removed_id)

        progress_size = protocol.read_varint(buffer)
        progress = {}
        for _ in range(progress_size):
            advancement_id = protocol.read_string(buffer)
            progress_dict = protocol.read_advancement_progress(buffer)

            criteria = {}
            for criterion_id, criterion_data in progress_dict['criteria'].items():
                criteria[criterion_id] = advancement.CriterionProgress(
                    criterion_data['achieved'],
                    criterion_data['date_of_achieving']
                )

            advancement_progress = advancement.AdvancementProgress(criteria)
            progress[advancement_id] = advancement_progress

        advancements_data = advancement.AdvancementsData(reset_clear, advancements, removed_advancements, progress)

        self._dispatch('advancements_update', advancements_data)
    async def parse_0x57(self, buffer: protocol.ProtocolBuffer) -> None:
        reset = protocol.read_bool(buffer)
        advancement_count = protocol.read_varint(buffer)
        self._dispatch('advancements', reset, advancement_count, buffer.getvalue())

    async def parse_0x37(self, buffer: protocol.ProtocolBuffer) -> None:
        has_id = protocol.read_bool(buffer)
        identifier = protocol.read_string(buffer) if has_id else None
        self._dispatch('select_advancement_tab', identifier)





