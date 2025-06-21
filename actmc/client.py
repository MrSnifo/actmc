from __future__ import annotations

from .gateway import MinecraftSocket
from typing import Optional, Literal, Any, Callable, TYPE_CHECKING, Dict
import asyncio
from .utils import setup_logging
from .tcp import TcpClient


if TYPE_CHECKING:
    from .chunk import Chunk, BlockState, BlockEntity
    from .math import Vector2D, Vector3D
    from .entity import Player
from .state import ConnectionState

import logging
_logger = logging.getLogger(__name__)

class Client:
    def __init__(self, host: str, port: Optional[int] = 25565):
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.socket: Optional[MinecraftSocket] = None
        self.tcp: TcpClient = TcpClient(host=host, port=port)
        self._connection: ConnectionState = self._get_state()
        self._closing_task: Optional[asyncio.Task] = None
        self._closed = False
        self._connection._get_socket = self._get_socket

    # -------------------+ Player +-------------------
    @property
    def player(self) -> Optional[Player]:
        return self._connection.player

    async def perform_respawn(self) -> None:
        """
        Informs the server that the client is ready to respawn
        or complete login. This sends a Client Status packet with action ID 0.
        """
        await self._connection.send_client_status(0)

    async def get_statistics(self) -> Dict[str, int]:
        """
        Requests updated statistics from the server.
        This sends a Client Status packet with action ID 1.

        <Warrning calling it many times may reutrn difriet sattustis and sotmiesm empty.

        """

        # todo: improve this, and cache it for few seconds to prevent extra requests
        return await self._connection.get_statistics()

    # -------------------+ Chunk +-------------------
    @property
    def chunks(self) -> Dict[Vector2D[int], Chunk]:
        return self._connection.chunks

    def get_block(self, pos: Vector3D[int]) -> Optional[BlockState]:
        return self._connection.get_block_state(pos)

    def set_block_state(self, block: BlockState) -> None:
        self._connection.set_block_state(block)

    def set_block_entity(self, pos: Vector3D[int], entity: BlockEntity) -> None:
        self._connection.set_block_entity(pos, entity)

    # -----------------------------------------------

    def _get_socket(self) -> MinecraftSocket:
        return self.socket

    def _get_state(self) -> ConnectionState:
        return ConnectionState(tcp=self.tcp, dispatcher=self.dispatch)

    def is_closed(self):
        return self._closed

    async def connect(self, username: str) -> None:
        try:
            while not self.is_closed():
                socket = MinecraftSocket.initialize_socket(client=self, state=self._connection)
                self.socket = await asyncio.wait_for(socket, timeout=60.0)
                self.dispatch('connect')
                await self._connection.send_initial_packets(username)
                while True:
                    await self.socket.poll()

        except asyncio.exceptions.IncompleteReadError:
            print("ERROR - Something went wrong")

    @staticmethod
    async def on_error(packet_id: str, error: Exception, /, *args: Any, **kwargs: Any) -> None:
        """
        Handle errors occurring during event dispatch.

        This static method logs an exception that occurred during the processing of an event.

        Parameters
        ----------
        packet_id: str
            The packet id of the event that caused the error.
        error: Exception
            The exception that was raised.
        *args: Any
            Positional arguments passed to the event.
        **kwargs: Any
            Keyword arguments passed to the event.
        """
        _logger.exception('Ignoring error: %s from %s, args: %s kwargs: %s', error, packet_id,
                          args, kwargs)

    async def _run_event(self, coro: Callable[..., Any], event_name: str, *args: Any, **kwargs: Any) -> None:
        # Run an event coroutine and handle exceptions.
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as error:
            await self.on_error(event_name, error, *args, **kwargs)

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        # Dispatch a specified event with a coroutine callback.
        method = 'on_' + event
        try:
            coro = getattr(self, method)
            if coro is not None and asyncio.iscoroutinefunction(coro):
                _logger.trace('Dispatching event %s', event) # type: ignore
                wrapped = self._run_event(coro, method, *args, **kwargs)
                # Schedule the task
                self.loop.create_task(wrapped, name=f'twitch:{method}')
        except AttributeError:
            pass
        except Exception as error:
            _logger.error('Event: %s Error: %s', event, error)

    def event(self, coro: Callable[..., Any], /) -> None:
        """
        Register a coroutine function as an event handler.

        This method assigns the given coroutine function to be used as an event handler with the same
        name as the coroutine function.

        Parameters
        ----------
        coro: Callable[..., Any]
            The coroutine function to register as an event handler.

        Example
        -------
        ```py
        @client.event
        async def on_ready():
            print('Ready!')
        ```
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The registered event must be a coroutine function')
        setattr(self, coro.__name__, coro)


    async def _async_loop(self) -> None:
        # Starts the asynchronous loop for managing client operations.
        loop = asyncio.get_running_loop()
        self.loop = loop

    async def start(self, username: str):
        if self.loop is None:
            await self._async_loop()
        await self.connect(username)

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

