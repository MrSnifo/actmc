from __future__ import annotations

from .gateway import MinecraftSocket
from typing import Optional, Literal, Any, Callable, TYPE_CHECKING, Dict
import asyncio
from .utils import setup_logging
from .tcp import TcpClient


if TYPE_CHECKING:
    from .chunk import Chunk, Block
    from .math import Vector2D, Vector3D
    from .user import User
from .state import ConnectionState

import logging
_logger = logging.getLogger(__name__)

class Client:
    def __init__(self, username: str):
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.socket: Optional[MinecraftSocket] = None
        self.tcp: Optional[TcpClient] = None
        self._connection: ConnectionState = self._get_state(username)
        self._closing_task: Optional[asyncio.Task] = None
        self._closed = False

    # -------------------+ Player +-------------------

    @property
    def user(self) -> Optional[User]:
        return self._connection.user

    @property
    def chunks(self) -> Dict[Vector2D[int], Chunk]:
        return self._connection.chunks

    @property
    async def difficulty(self) ->  Optional[int]:
        return self._connection.difficulty

    @property
    async def max_players(self) -> Optional[int]:
        return self._connection.max_players

    @property
    async def world_type(self) -> Optional[str]:
        return self._connection.world_type

    @property
    async def world_age(self) -> Optional[int]:
        return self._connection.world_age

    @property
    async def time_of_day(self) -> Optional[int]:
        return self._connection.time_of_day

    def get_block(self, pos: Vector3D[int]) -> Optional[Block]:
        return self._connection.get_block_state(pos)

    # -----------------------------------------------
    def _get_socket(self) -> MinecraftSocket:
        return self.socket

    def _get_state(self, username: str) -> ConnectionState:
        return ConnectionState(username=username, dispatcher=self.dispatch)

    def is_closed(self):
        return self._closed

    async def connect(self, host: str, port: Optional[int]) -> None:
        try:
            while not self.is_closed():
                socket = MinecraftSocket.initialize_socket(client=self, host=host, port=port, state=self._connection)
                self.socket = await asyncio.wait_for(socket, timeout=60.0)
                self.dispatch('connect')
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

    async def start(self, host: str, port: Optional[int]):
        if self.loop is None:
            await self._async_loop()
        await self.connect(host, port)


    async def respawn_user(self) -> None:
        """Perform a respawn"""
        await self._connection.respawn()

    async def send_client_settings(self, locale: str = 'en_US', view_distance: int = 10,
                                   chat_mode: int = 0, chat_colors: bool = True,
                                   cape: bool = True, jacket: bool = True, left_sleeve: bool = True,
                                   right_sleeve: bool = True, left_pants: bool = True,
                                   right_pants: bool = True, hat: bool = True,
                                   main_hand: int = 1) -> None:
        """
        Send client settings to the server.

        Parameters
        ----------
        locale: str
            Client locale (e.g., "en_US").
        view_distance: int
            Render distance (2-32).
        chat_mode: int
            Chat mode (0=enabled, 1=commands only, 2=hidden).
        chat_colors: bool
            Whether to display chat colors.
        cape: bool
            Whether to display cape.
        jacket: bool
            Whether to display jacket overlay.
        left_sleeve: bool
            Whether to display left sleeve overlay.
        right_sleeve: bool
            Whether to display right sleeve overlay.
        left_pants: bool
            Whether to display left pants overlay.
        right_pants: bool
            Whether to display right pants overlay.
        hat: bool
            Whether to display hat overlay.
        main_hand: int
            Main hand (0=left, 1=right).
        """
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
        await self._connection.send_client_settings(locale, view_distance, chat_mode, chat_colors, cape, jacket,
                                                    left_sleeve, right_sleeve, left_pants, right_pants, hat, main_hand)

    async def open_advancement_tab(self, tab_id: str) -> None:
        """
        Open a specific advancement tab.

        Parameters
        ----------
        tab_id: str
            The advancement tab identifier.
        """
        await self._connection.open_advancement_tab( tab_id)

    async def close_advancement_tab(self) -> None:
        """Close the advancement tab."""
        await self.tcp.advancement_tab(1)

    async def set_resource_pack_status(self, result: int) -> None:
        """
        Respond to a resource pack request.

        Parameters
        ----------
        result: int
            Status code (0=loaded, 1=declined, 2=failed, 3=accepted).
        """
        await self._connection.set_resource_pack_status(result)

    def run(self,
            host: str, port: Optional[int] = 25565,
            log_handler: Optional[logging.Handler] = None,
            log_level: Optional[Literal[0, 5, 10, 20, 30, 40, 50]] = None,
            root_logger: bool = False) -> None:
        if log_handler is None:
            setup_logging(handler=log_handler, level=log_level, root=root_logger)

        # https://account.mojang.com/documents/minecraft_eula README

        async def runner() -> None:
            await self.start(host, port)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            return

