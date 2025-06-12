from typing import Optional

from .entity import Player
from .tcp import TcpClient
from .world import World
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .gateway import MinecraftSocket

from . import protocol

import logging

_logger = logging.getLogger(__name__)

__all__ = ('ConnectionState',)

class ConnectionState:
    if TYPE_CHECKING:
        _get_socket: Callable[..., MinecraftSocket]

    def __init__(self, tcp: TcpClient):
        self.username: Optional[str] = None
        self.tcp: TcpClient = tcp
        self.player = None
        self.world = World()
        self.entities = []


    async def send_packet(self, packet_id: int, buffer: protocol.ProtocolBuffer) -> None:
        socket = self._get_socket()
        if not socket:
            raise RuntimeError("Socket is not initialized or not connected.")
        await socket.send_packet(packet_id, buffer.getvalue())


    async def send_initial_packets(self):
        await self.send_packet(0x00, self.tcp.build_handshake_packet)
        await self.send_packet(0x00, self.tcp.build_login_packet(self.username))
        _logger.info(f"Sent handshake and login packets")

    def parse(self, packet_id: int, data: protocol.ProtocolBuffer) -> None:
        try:
            func = getattr(self, f'parse_0x{packet_id:02X}'.lower())
            func(data)
        except Exception as error:
            _logger.debug(f'parse_0x{packet_id:02X}'.lower())
            _logger.debug('Failed to parse event: %s', error)

    def parse_0x02(self, data: protocol.ProtocolBuffer) -> None:
        """
        Login Success (Packet ID: 0x02)

        Contains player's UUID (36-character string with hyphens) and username.
        Marks successful login and switches connection state to Play.
        """
        uuid = protocol.read_string(data)
        username = protocol.read_string(data)
        self.player = Player(uid=uuid, username=username)

    def parse_0x23(self, data: protocol.ProtocolBuffer) -> None:
        """
        Join Game (Packet ID: 0x23)

        Sent by the server to indicate that the player has successfully joined the game world.
        This packet sets the connection state to 'Play' and provides essential game settings
        such as the player's entity ID, game mode, world dimension, and more.

        Fields:
        -------
        - Entity ID (int): The unique entity ID of the player.
        - Game Mode (unsigned byte):
            0 = Survival, 1 = Creative, 2 = Adventure, 3 = Spectator.
            Bit 3 (0x8) is the hardcore flag.
        - Dimension (int enum):
            -1 = Nether, 0 = Overworld, 1 = End.
            (Note: Not a VarInt; this is a regular signed int.)
        - Difficulty (unsigned byte):
            0 = Peaceful, 1 = Easy, 2 = Normal, 3 = Hard.
        - Max Players (unsigned byte):
            Legacy field; no longer used by the client.
        - Level Type (string):
            World generation type. E.g., 'default', 'flat', 'amplified'.
        - Reduced Debug Info (bool):
            True if reduced debug screen information is enabled.
        """
        self.player.id = protocol.read_int(data)
        self.player.gamemode = protocol.read_ubyte(data)

        # todo: World
        dimension = protocol.read_int(data)
        difficulty = protocol.read_ubyte(data)
        # todo: Server
        max_players = protocol.read_ubyte(data)
        # todo: World
        level_type = protocol.read_string(data)

        # reduced_debug_info, offset = utils.read_bool(data, offset)

    def parse_0x1a(self, data: protocol.ProtocolBuffer) -> None:
        """
        Disconnect (Packet ID: 0x1A)

        Sent by the server to notify the client that the connection is terminated.

        Fields:
        - Reason (Chat): A chat message explaining the disconnect reason.
        """
        reason = protocol.read_chat(data)
        print(reason)
        _logger.debug(f"Disconnected by server: {reason}")

    def parse_0x41(self, data: protocol.ProtocolBuffer) -> None:
        """
        Update Health (Packet ID: 0x41)

        Sent by the server to update/set the health of the player it is sent to.

        Food saturation acts as a food “overcharge”. Food values will not decrease
        while the saturation is over zero. Players logging in automatically get
        a saturation of 5.0. Eating food increases the saturation as well as the food bar.

        Fields:
        - Health (float): 0 or less = dead, 20 = full HP
        - Food (VarInt): Range from 0 to 20
        - Food Saturation (float): Varies from 0.0 to 5.0
        """
        self.player.health = protocol.read_float(data)
        self.player.food = protocol.read_varint(data)
        self.player.food_saturation = protocol.read_float(data)

    def parse_0x40(self, data: protocol.ProtocolBuffer) -> None:
        """
        Set Experience (Packet ID: 0x40)

        Sent by the server to update the player's experience bar, level, and total experience.

        Fields:
        - Experience bar (float): between 0.0 and 1.0 (progress towards next level)
        - Level (VarInt): current player level
        - Total Experience (VarInt): total XP accumulated by the player
        """
        self.player.experience_bar = protocol.read_float(data)
        self.player.level = protocol.read_varint(data)
        self.player.total_experience = protocol.read_varint(data)

    def parse_0x3a(self, data: protocol.ProtocolBuffer) -> None:
        """
        Held Item Change (Packet ID: 0x3A)

        Sent by the server to update which hotbar slot the player has selected.

        Fields:
        - Slot (Byte): The selected hotbar slot (0–8)
        """
        self.player.selected_slot = data.getvalue()

    def parse_0x20(self, data: protocol.ProtocolBuffer) -> None:
        chunk_x = protocol.read_int(data)
        chunk_z = protocol.read_int(data)
        ground_up_continuous = protocol.read_bool(data)
        primary_bitmask = protocol.read_varint(data)
        chunk_data_size = protocol.read_varint(data)

        print(f"Parsing chunk ({chunk_x}, {chunk_z}), ground_up: {ground_up_continuous}, "
              f"bitmask: {bin(primary_bitmask)}, data_size: {chunk_data_size}")

        
        self.world.load_chunk(data.getvalue())
        f = self.world.get_state(32, 69, -67)
        print(f)


