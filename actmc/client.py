from __future__ import annotations

from .gateway import MinecraftSocket
from typing import Optional, Literal, Any, Self
import asyncio
from .utils import setup_logging
from .tcp import TcpClient
from .state import ConnectionState
import logging

_logger = logging.getLogger(__name__)

class Client:
    def __init__(self, host: str, port: Optional[int] = 25565):
        # todo: To None later...
        self.loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop()
        self.socket: Optional[MinecraftSocket] = None
        self.tcp: TcpClient = TcpClient(host=host, port=port)
        self._connection: ConnectionState = self._get_state()
        self._closing_task: Optional[asyncio.Task] = None
        self._closed = False
        self._connection._get_socket = self._get_socket

    def _get_socket(self) -> MinecraftSocket:
        return self.socket

    def _get_state(self) -> ConnectionState:
        return ConnectionState(tcp=self.tcp)

    def is_closed(self):
        return self._closed

    async def connect(self) -> None:


        try:
            while not self.is_closed():
                socket = MinecraftSocket.initialize_socket(client=self, state=self._connection)
                self.socket = await asyncio.wait_for(socket, timeout=60.0)
                await self._connection.send_initial_packets()
                while True:
                    await self.socket.poll()

        except asyncio.exceptions.IncompleteReadError:
            print("ERROR - Something went wrong")


    async def auth(self, username: str):
        self._connection.username = username

    async def start(self, username: str):
        await self.auth(username)
        await self.connect()

    @staticmethod
    async def handle_packet(data: bytes):
        print(f"[Client] Received packet: {data.hex()}")

    def run(self,
            username: str,
            log_handler: Optional[logging.Handler] = None,
            log_level: Optional[Literal[0, 5, 10, 20, 30, 40, 50]] = None,
            root_logger: bool = False) -> None:
        if log_handler is None:
            setup_logging(handler=log_handler, level=log_level, root=root_logger)

        async def runner() -> None:
            await self.start(username)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            return

