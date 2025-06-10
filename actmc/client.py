from .gateway import SocketGateway
from typing import Optional, Literal
import asyncio
from .utils import setup_logging
from .state import ConnectionState
import logging

_logger = logging.getLogger(__name__)

class Client:
    def __init__(self, host, port: Optional[int] = 25565):
        self._connection = ConnectionState(host, port)
        self.loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop()
        self._closing_task: Optional[asyncio.Task] = None
        self.gateway: Optional[SocketGateway] = None
        self._closed = False


    def is_closed(self):
        return self._closed

    async def connect(self) -> None:


        while not self.is_closed():
            socket = SocketGateway.initialize_socket(self._connection)
            self.gateway = await asyncio.wait_for(socket, timeout=60.0)
            while True:
                await self.gateway.poll()


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

