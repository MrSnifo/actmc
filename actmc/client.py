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

from .errors import ClientException, ConnectionClosed
from .gateway import MinecraftSocket
from .state import ConnectionState
from typing import TYPE_CHECKING
from .utils import setup_logging
import asyncio

if TYPE_CHECKING:
    from typing import Optional, Literal, Any, Callable, Dict, Type
    from .ui.scoreboard import Scoreboard
    from .math import Vector2D, Vector3D
    from .ui.border import WorldBorder
    from .ui.tablist import PlayerInfo
    from .ui.actionbar import Title
    from .chunk import Chunk, Block
    from types import TracebackType
    from .ui.bossbar import BossBar
    from .ui.gui import Window
    from .user import User

import logging
_logger = logging.getLogger(__name__)

__all__ = ('Client',)


class Client:
    """
    A Minecraft client for connecting to and interacting with Minecraft servers.

    Parameters
    ----------
    username: str
        The username to use for the connection.
    """

    def __init__(self, username: str) -> None:
        # Core event loop and networking
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.socket: Optional[MinecraftSocket] = None

        # Connection and state management
        self._connection: ConnectionState = self._get_state(username)
        self._ready: Optional[asyncio.Event] = None
        self._closed = False
        self._closing_task: Optional[asyncio.Task] = None

    def _handle_ready(self) -> None:
        self._ready.set()

    @property
    def user(self) -> Optional[User]:
        """
        Get the current user.

        Returns
        -------
        Optional[User]
            The current user object, or None if not connected.
        """
        return self._connection.user

    @property
    def chunks(self) -> Dict[Vector2D[int], Chunk]:
        """
        Get the loaded chunks.

        Returns
        -------
        Dict[Vector2D[int], Chunk]
            Dictionary mapping chunk coordinates to chunk objects.
        """
        return self._connection.chunks

    @property
    async def difficulty(self) -> Optional[int]:
        """
        Get the current world difficulty.

        Returns
        -------
        Optional[int]
            The difficulty level, or None if not available.
        """
        return self._connection.difficulty

    @property
    async def max_players(self) -> Optional[int]:
        """
        Get the maximum number of players allowed on the server.

        Returns
        -------
        Optional[int]
            The maximum player count, or None if not available.
        """
        return self._connection.max_players

    @property
    async def world_type(self) -> Optional[str]:
        """
        Get the world type.

        Returns
        -------
        Optional[str]
            The world type string, or None if not available.
        """
        return self._connection.world_type

    @property
    async def world_age(self) -> Optional[int]:
        """
        Get the age of the world in ticks.

        Returns
        -------
        Optional[int]
            The world age in ticks, or None if not available.
        """
        return self._connection.world_age

    @property
    async def time_of_day(self) -> Optional[int]:
        """
        Get the current time of day.

        Returns
        -------
        Optional[int]
            The time of day in ticks, or None if not available.
        """
        return self._connection.time_of_day

    @property
    def world_border(self) -> Optional[WorldBorder]:
        """
        Get the world border information.

        Returns
        -------
        Optional[WorldBorder]
            The world border object, or None if not available.
        """
        return self._connection.world_border

    @property
    def tablist(self) -> Dict[str, PlayerInfo]:
        """
        Get the player tab list.

        Returns
        -------
        Dict[str, PlayerInfo]
            A dictionary mapping player UIDs to TabPlayer objects.
        """
        return self._connection.tablist

    @property
    def windows(self) -> Dict[int, Window]:
        """
        Get the open windows/inventories.

        Returns
        -------
        Dict[int, Window]
            Dictionary mapping window IDs to Window objects.
        """
        return self._connection.windows

    @property
    def boss_bars(self) -> Dict[str, BossBar]:
        """
        Get the active boss bars.

        Returns
        -------
        Dict[str, BossBar]
            Dictionary mapping boss bar UUIDs to BossBar objects.
        """
        return self._connection.boss_bars

    @property
    def scoreboard(self) -> Dict[str, Scoreboard]:
        """
        Get the scoreboard objectives.

        Returns
        -------
        Dict[str, Scoreboard]
            Dictionary mapping objective names to ScoreboardObjective objects.
        """
        return self._connection.scoreboard_objectives

    @property
    def action_bar(self) -> Title:
        """
        Get the action bar title.

        Returns
        -------
        Title
            The current action bar title object.
        """
        return self._connection.action_bar

    def get_block(self, pos: Vector3D[int]) -> Optional[Block]:
        """
        Get the block at the specified position.

        Parameters
        ----------
        pos: Vector3D[int]
            The position coordinates of the block.

        Returns
        -------
        Optional[Block]
            The block at the specified position, or None if not available.
        """
        return self._connection.get_block_state(pos)

    def is_closed(self) -> bool:
        """
        Check if the client connection is closed.

        Returns
        -------
        bool
            True if the connection is closed, False otherwise.
        """
        return self._closed

    async def connect(self, host: str, port: int) -> None:
        """
        Connect to a Minecraft server.

        Parameters
        ----------
        host: str
            The server hostname or IP address.
        port: int
            The server port number.

        Raises
        ------
        ConnectionClosed
            If the connection is interrupted unexpectedly.
        ClientException
            If the client fails to connect.

        Notes
        -----
        By using this, you agree to Minecraft's EULA:

        https://account.mojang.com/documents/minecraft_eula
        """
        while not self.is_closed():
            try:
                socket = MinecraftSocket.initialize_socket(host=host, port=port, state=self._connection)
                self.socket = await asyncio.wait_for(socket, timeout=60.0)
                self.dispatch('connect')
                while True:
                    await self.socket.poll()
            except (ConnectionClosed, asyncio.exceptions.IncompleteReadError, asyncio.TimeoutError, OSError) as exc:
                self.dispatch('disconnect')
                if self.is_closed():
                    return
                if isinstance(exc, ConnectionClosed):
                    raise
                elif isinstance(exc, asyncio.exceptions.IncompleteReadError):
                    raise ConnectionClosed("Connection interrupted unexpectedly") from exc
                elif isinstance(exc, asyncio.TimeoutError):
                    raise ClientException(f"Connection timeout to {host}:{port}") from None
                elif isinstance(exc, OSError):
                    if hasattr(exc, 'winerror') and exc.winerror == 121:
                        raise ClientException(f"Network timeout connecting to {host}:{port}") from None
                    else:
                        raise ClientException(f"Failed to connect to {host}:{port}") from None

    async def start(self, host: str, port: int) -> None:
        """
        Start the client and connect to the server.

        Parameters
        ----------
        host: str
            The server hostname or IP address.
        port: int
            The server port number.
        """
        if self.loop is None:
            await self._async_loop()
        await self.connect(host, port)

    async def close(self) -> None:
        """
        Close the connection to the Minecraft server.

        If a closing task is already running, it waits for it to complete.

        If the socket is open, it is closed with proper cleanup. After closing
        the socket, it clears the connection state and closes the TCP client.
        """
        if self._closing_task:
            return await self._closing_task

        async def _close():
            if self.socket is not None:
                await self.socket.close()

            self._connection.clear()
            self._closed = True
            self.loop = None

            if self._ready is not None:
                self._ready.clear()

            self._ready = None

        self._closing_task = asyncio.create_task(_close())
        return await self._closing_task

    async def __aenter__(self) -> Client:
        """Asynchronous context manager entry method."""
        await self._async_loop()
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_value: Optional[BaseException],
                        traceback: Optional[TracebackType]) -> None:
        """Asynchronous context manager exit method."""
        if self._closing_task:
            await self._closing_task
        else:
            await self.close()

    def run(self,
            host: str,
            port: int = 25565,
            *,
            log_handler: Optional[logging.Handler] = None,
            log_level: Optional[Literal[0, 5, 10, 20, 30, 40, 50]] = None,
            root_logger: bool = False) -> None:
        """
        Start the client.

        Parameters
        ----------
        host: str
            The server hostname or IP address.
        port: int
            The server port number.
        log_handler: Optional[logging.Handler]
            A logging handler to be used for logging output.
        log_level: Optional[Literal[0, 5, 10, 20, 30, 40, 50]]
            The logging level to be used (NOTSET=0, TRACE=5, DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50).
        root_logger: bool
            If True, the logging configuration applies to the root logger;
            otherwise, it applies to a new logger.

        Warning
        -------
        The client does NOT perform automatic SRV record lookups.
        To connect to domains using SRV records (e.g., Minecraft hosts),
        you must resolve the port yourself and provide it explicitly.
        If omitted, the default port 25565 is used.
        """
        if log_handler is None:
            setup_logging(handler=log_handler, level=log_level, root=root_logger)

        async def runner() -> None:
            """
            Inner function to run the main process asynchronously.
            """
            async with self:
                await self.start(host, port)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            return

    async def perform_respawn(self) -> None:
        """
        Request the server to respawn the player.

        Notes
        -----
        Typically used after death to rejoin the world.
        """
        await self._connection.send_client_status(0)

    async def request_stats(self) -> None:
        """
        Request the player's statistics from the server.

        Notes
        -----
        The server responds by sending the statistics,
        which are usually processed in the ``on_statistics`` handler.
        """
        await self._connection.send_client_status(1)

    async def send_client_settings(self,
                                   locale: str = 'en_US',
                                   view_distance: int = 10,
                                   chat_mode: int = 0,
                                   chat_colors: bool = True,
                                   cape: bool = True,
                                   jacket: bool = True,
                                   left_sleeve: bool = True,
                                   right_sleeve: bool = True,
                                   left_pants: bool = True,
                                   right_pants: bool = True,
                                   hat: bool = True,
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

    async def send_message(self, message: str) -> None:
        """
        Send a chat message to the server.

        Parameters
        ----------
        message: str
            The message to send.
        """
        await self._connection.send_chat_message(message)

    async def open_advancement_tab(self, tab_id: str) -> None:
        """
        Open a specific advancement tab.

        Parameters
        ----------
        tab_id: str
            The advancement tab identifier.
        """
        await self._connection.open_advancement_tab(tab_id)

    async def close_advancement_tab(self) -> None:
        """
        Close the advancement tab.

        Notes
        -----
        close the currently open advancement tab.
        """
        await self._connection.close_advancement_tab()

    async def set_resource_pack_status(self, result: int) -> None:
        """
        Respond to a resource pack request.

        Parameters
        ----------
        result: int
            Status code (0=loaded, 1=declined, 2=failed, 3=accepted).
        """
        await self._connection.set_resource_pack_status(result)

    def event(self, coro: Callable[..., Any], /) -> None:
        """
        Register a coroutine function as an event handler.

        This method assigns the given coroutine function to be used as an event handler with the same
        name as the coroutine function.

        Parameters
        ----------
        coro: Callable[..., Any]
            The coroutine function to register as an event handler.

        Raises
        ------
        TypeError
            If the provided function is not a coroutine function.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The registered event must be a coroutine function')
        setattr(self, coro.__name__, coro)

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Dispatch a specified event with a coroutine callback.

        Parameters
        ----------
        event: str
            The name of the event to dispatch.
        *args: Any
            Positional arguments to pass to the event handler.
        **kwargs: Any
            Keyword arguments to pass to the event handler.
        """
        method = 'on_' + event
        try:
            coro = getattr(self, method)
            if coro is not None and asyncio.iscoroutinefunction(coro):
                _logger.trace('Dispatching event %s', event)  # type: ignore
                wrapped = self._run_event(coro, method, *args, **kwargs)
                self.loop.create_task(wrapped, name=f'actmc:{method}')
        except AttributeError:
            pass
        except Exception as error:
            _logger.error('Event: %s Error: %s', event, error)

    def _get_state(self, username: str) -> ConnectionState:
        """Create and return a connection state object."""
        return ConnectionState(username=username, dispatcher=self.dispatch, ready=self._handle_ready)

    async def _async_loop(self) -> None:
        """Initialize the asynchronous event loop for managing client operations."""
        loop = asyncio.get_running_loop()
        self.loop = loop
        self._ready = asyncio.Event()

    async def _run_event(self, coro: Callable[..., Any], event_name: str, *args: Any, **kwargs: Any) -> None:
        """Run an event coroutine and handle exceptions."""
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as error:
            await self.on_error(event_name, error, *args, **kwargs)

    async def wait_until_ready(self) -> None:
        """
        Wait until the client's internal cache is ready.

        This coroutine blocks until the client's internal state is fully initialized
        and ready to be used.

        Raises
        ------
        RuntimeError
            If the client has not been initialized. Ensure that you use the asynchronous
            context manager to initialize the client.

        Warnings
        --------
        Calling this method inside `setup_hook()` may cause a deadlock.
        """
        if self._ready is not None:
            await self._ready.wait()
        else:
            raise RuntimeError(
                "The client is not initialized. Use the asynchronous context manager to initialize the client."
            )

    @property
    def is_ready(self) -> bool:
        """
        Check whether the client's internal cache is ready.

        Returns
        -------
        bool
            True if the client is fully initialized and ready to be used, False otherwise.
        """
        return self._ready is not None and self._ready.is_set()

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