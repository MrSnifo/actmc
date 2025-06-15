from typing import Optional

from .entity import Player, ObjectData, Entity
from .tcp import TcpClient
from .world import World, BlockState
from typing import TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from .gateway import MinecraftSocket

from . import math
from . import protocol


import logging

_logger = logging.getLogger(__name__)

__all__ = ('ConnectionState',)

class ConnectionState:
    if TYPE_CHECKING:
        _get_socket: Callable[..., MinecraftSocket]

    def __init__(self, tcp: TcpClient, dispatcher: Callable[..., Any], load_chunk: bool):
        self._dispatch = dispatcher
        self.username: Optional[str] = None
        self.tcp: TcpClient = tcp
        self.player: Optional[Player] = None
        self.load_chunk = load_chunk
        self.world = World()
        self.entities = []
        self.dimension = 0
        self.difficulty = 0
        self.max_players = 0
        self.level_type = ""
        self.player_teleport_id: Optional[int] = None

    async def send_packet(self, packet_id: int, buffer: protocol.ProtocolBuffer) -> None:
        socket = self._get_socket()
        if not socket:
            raise RuntimeError("Socket is not initialized or not connected.")
        await socket.write_packet(packet_id, buffer.getvalue())

    async def send_player_position_and_look(self, x: float, y: float, z: float, yaw: float, pitch: float,
                                            on_ground: bool):
        packet = self.tcp.build_player_position_and_look_packet(x, y, z, yaw, pitch, on_ground)
        await self.send_packet(0x0E, packet)

    async def send_initial_packets(self):
        await self.send_packet(0x00, self.tcp.build_handshake_packet)
        await self.send_packet(0x00, self.tcp.build_login_packet(self.username))
        _logger.debug(f"Sent handshake and login packets")
        self._dispatch('ready')

    def parse(self, packet_id: int, data: protocol.ProtocolBuffer) -> None:
        try:
            func = getattr(self, f'parse_0x{packet_id:02X}'.lower())
            func(data)
        except Exception as error:
            # todo: change
            _logger.debug(f'parse_0x{packet_id:02X}'.lower())
            _logger.exception('Failed to parse event: %s', error)

    def parse_0x02(self, data: protocol.ProtocolBuffer) -> None:
        """
        Login Success (Packet ID: 0x02)

        Contains player's UUID (36-character string with hyphens) and username.
        Marks successful login and switches connection state to Play.
        """
        uuid = protocol.read_string(data)
        username = protocol.read_string(data)
        self.player = Player(uid=uuid, username=username)
        self.player.position = math.Vector3D(0.0, 0.0, 0.0)
        self.player.rotation = math.Rotation(0.0, 0.0)
        self._dispatch('login')

    def parse_0x23(self, data: protocol.ProtocolBuffer) -> None:
        """
        Join Game (Packet ID: 0x23)


        Sent by the server to indicate that the player has successfully joined the game world.
        This packet sets the connection state to 'Play' and provides essential game settings
        such as the player's entity ID, game mode, world dimension, and more.
        """
        self.player.id = protocol.read_int(data)
        self.player.gamemode = protocol.read_ubyte(data)
        self.dimension = protocol.read_int(data)
        self.difficulty = protocol.read_ubyte(data)
        self.max_players = protocol.read_ubyte(data)
        self.level_type = protocol.read_string(data)
        # reduced_debug_info, offset = utils.read_bool(data, offset)
        self._dispatch('join')

    def parse_0x1a(self, data: protocol.ProtocolBuffer) -> None:
        """
        Disconnect (Packet ID: 0x1A)

        Sent by the server to notify the client that the connection is terminated.
        """
        reason = protocol.read_chat(data)
        _logger.debug(f"Disconnected by server: {reason}")
        self._dispatch('disconnect', reason)

    def parse_0x41(self, data: protocol.ProtocolBuffer) -> None:
        """
        Update Health (Packet ID: 0x41)

        Sent by the server to update/set the health of the player it is sent to.
        """
        self.player.health = protocol.read_float(data)
        self.player.food = protocol.read_varint(data)
        self.player.food_saturation = protocol.read_float(data)
        self._dispatch('player_health', self.player.health, self.player.food, self.player.food_saturation)

    def parse_0x40(self, data: protocol.ProtocolBuffer) -> None:
        """
        Set Experience (Packet ID: 0x40)

        Sent by the server to update the player's experience bar, level, and total experience.
        """
        self.player.experience_bar = protocol.read_float(data)
        self.player.level = protocol.read_varint(data)
        self.player.total_experience = protocol.read_varint(data)
        self._dispatch('player_experience',
                       self.player.level, self.player.total_experience, self.player.experience_bar)

    def parse_0x3a(self, data: protocol.ProtocolBuffer) -> None:
        """
        Held Item Change (Packet ID: 0x3A)

        Sent by the server to update which hotbar slot the player has selected.
        """
        self.player.selected_slot = protocol.read_byte(data)
        self._dispatch('player_held_slot', self.player.selected_slot)

    def parse_0x20(self, data: protocol.ProtocolBuffer) -> None:
        chunk_x = protocol.read_int(data)
        chunk_z = protocol.read_int(data)
        ground_up_continuous = protocol.read_bool(data)
        primary_bitmask = protocol.read_varint(data)
        chunk_data_size = protocol.read_varint(data)
        if self.load_chunk:
            _logger.trace( # type: ignore
                f"Parsing chunk ({chunk_x}, {chunk_z}), ground_up: {ground_up_continuous}, "
                f"bitmask: {bin(primary_bitmask)}, data_size: {chunk_data_size}")
            self.world.load_chunk(data.getvalue())
        self._dispatch('load_chunk', data.getvalue())


    def parse_0x2f(self, data: protocol.ProtocolBuffer) -> None:
        """
        Player Position and Look (Packet ID: 0x2F, clientbound)

        Updates the player's position and orientation.
        """
        x = protocol.read_double(data)
        y = protocol.read_double(data)
        z = protocol.read_double(data)
        yaw = protocol.read_float(data)
        pitch = protocol.read_float(data)
        flags = protocol.read_byte(data)
        teleport_id = protocol.read_varint(data)

        if flags & 0x01:  # X relative
            x += self.player.position.x
        if flags & 0x02:  # Y relative
            y += self.player.position.y
        if flags & 0x04:  # Z relative
            z += self.player.position.z
        if flags & 0x08:  # Yaw relative
            yaw += self.player.rotation.yaw_angle
        if flags & 0x10:  # Pitch relative
            pitch += self.player.rotation.pitch_angle

        self.player.position = math.Vector3D(x, y, z)
        self.player.rotation = math.Rotation(pitch, yaw)

        self._dispatch('player_position_look', self.player.position, self.player.rotation, teleport_id)

    def parse_0x30(self, data: protocol.ProtocolBuffer) -> None:
        """
        Use Bed (Packet ID: 0x30)

        Sent when a player goes into bed. Notifies nearby players.
        """
        entity_id = protocol.read_varint(data)
        x, y, z = protocol.read_position(data)
        self._dispatch('player_use_bed', Entity(entity_id, entity_type='player'), math.Vector3D(x, y, z))

    def parse_0x26(self, data: protocol.ProtocolBuffer) -> None:
        """
        Entity Relative Move (Packet ID: 0x26)

        Sent by the server when an entity moves less than 8 blocks. For movements larger than that,
        the server uses Entity Teleport.
        """
        entity_id = protocol.read_varint(data)
        delta_x = protocol.read_short(data)
        delta_y = protocol.read_short(data)
        delta_z = protocol.read_short(data)

        on_ground = protocol.read_bool(data)
        delta_position = math.Vector3D(delta_x, delta_y, delta_z)

        self._dispatch('entity_teleport', Entity(entity_id), delta_position, on_ground)

    def parse_0x27(self, data: protocol.ProtocolBuffer) -> None:
        """
        Entity Look And Relative Move (Packet ID: 0x27)

        Sent by the server when an entity moves up to 8 blocks and changes rotation.

        Fields:
            - Entity ID (VarInt): The entity that is moving and rotating.
            - Delta X (Short): Change in X position (fixed-point).
            - Delta Y (Short): Change in Y position (fixed-point).
            - Delta Z (Short): Change in Z position (fixed-point).
            - Yaw (Byte/Angle): New yaw angle (not a delta).
            - Pitch (Byte/Angle): New pitch angle (not a delta).
            - On Ground (Boolean): Whether the entity is on the ground.
        """
        entity_id = protocol.read_varint(data)

        delta_x = protocol.read_short(data)
        delta_y = protocol.read_short(data)
        delta_z = protocol.read_short(data)

        yaw = protocol.read_ubyte(data)
        pitch = protocol.read_ubyte(data)

        on_ground = protocol.read_bool(data)

        delta_position = math.Vector3D(delta_x, delta_y, delta_z)
        rotation = math.Rotation(yaw, pitch)

        self._dispatch('entity_look_move', entity_id, delta_position, rotation, on_ground)

    def parse_0x0b(self, data: protocol.ProtocolBuffer) -> None:
        """
        Block Change (Packet ID: 0x0B)

        Fired whenever a block is changed within the render distance.
        """
        position = protocol.read_position(data)
        block_state_id = protocol.read_varint(data)
        vector = math.Vector3D(*position)

        block_type = block_state_id >> 4
        block_meta = block_state_id & 0xF

        state =  BlockState(block_type, block_meta)


        self._dispatch('block_change', state, vector)
        if self.load_chunk:
            self.world.set_state(vector, state)

    def parse_0x10(self, data: protocol.ProtocolBuffer) -> None:
        """
        Multi Block Change (Packet ID: 0x10)

        Fired whenever 2 or more blocks are changed within the same chunk on the same tick.
        Dispatches a single 'multi_block_change' event with a list of (BlockState, Vector3D).
        """
        chunk_x = protocol.read_int(data)
        chunk_z = protocol.read_int(data)
        record_count = protocol.read_varint(data)

        changes = []

        for _ in range(record_count):
            horizontal = protocol.read_ubyte(data)
            y = protocol.read_ubyte(data)
            block_state_id = protocol.read_varint(data)

            # Extract relative coordinates in the chunk (0-15)
            rel_x = (horizontal >> 4) & 0x0F
            rel_z = horizontal & 0x0F

            # Absolute coordinates
            x = (chunk_x * 16) + rel_x
            z = (chunk_z * 16) + rel_z

            block_type = block_state_id >> 4
            block_meta = block_state_id & 0xF
            state = BlockState(block_type, block_meta)
            vector = math.Vector3D(int(x), int(y), int(z))
            changes.append((state, vector))
            if self.load_chunk:
                self.world.set_state(vector, state)

        # Dispatch once with all changes
        self._dispatch('multi_block_change', changes)

    def parse_0x0f(self, data: protocol.ProtocolBuffer) -> None:
        """
        Chat Message (Packet ID: 0x0F)

        Sent by the server to deliver chat, system, or game info messages.

        Fields:
            - JSON Data (Chat): The message content in JSON format.
            - Position (Byte): The display location:
                0 = Chat (chat box),
                1 = System message (chat box),
                2 = Game info (above hotbar).
        """
        message = protocol.read_chat(data)
        display = protocol.read_ubyte(data)

        display_str = {0: 'chat', 1: 'system', 2: 'game'}.get(display, f"unknown ({display})")
        self._dispatch('chat_message', display_str, message)



