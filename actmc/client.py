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
from .tcp import TcpClient
import asyncio

if TYPE_CHECKING:
    from typing import Optional, Literal, Any, Callable, Dict, Type
    from .ui.scoreboard import Scoreboard
    from .math import Vector2D, Vector3D
    from .ui.tablist import PlayerInfo
    from .ui.border import WorldBorder
    from .ui.actionbar import Title
    from .entities.misc import Item
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
        self.tcp: TcpClient = TcpClient()

        # Connection and state management
        self._connection: ConnectionState = self._get_state(username)
        self._ready: Optional[asyncio.Event] = None
        self._closing_task: Optional[asyncio.Task] = None

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
        return self._closing_task is not None

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

        Warnings
        --------
        Repeated calls to this method without delays may trigger server rate limiting.
        Implement appropriate delays between connection attempts.

        Notes
        -----
        By using this, you agree to Minecraft's EULA:

        https://account.mojang.com/documents/minecraft_eula
        """
        while not self.is_closed():
            try:
                socket = MinecraftSocket.initialize_socket(client=self, host=host, port=port, state=self._connection)
                self.socket = await asyncio.wait_for(socket, timeout=60.0)
                self.dispatch('connect')
                while True:
                    await self.socket.poll()
            except (ConnectionClosed, asyncio.exceptions.IncompleteReadError, asyncio.TimeoutError, OSError) as exc:
                self.dispatch('disconnect')
                await self.close()
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

    async def start(self, host: str, port: int = 25565) -> None:
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

    def clear(self) -> None:
        """
        Clear the internal state of the bot.

        Resets the bot to an uninitialized state, clearing all internal caches
        and connection state.
        """
        self._closing_task = None
        self._ready.clear()
        self._connection.clear()

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

            if self._ready is not None:
                self._ready.clear()

            self.tcp.clear()
            self.loop = None

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
        """Request the server to respawn the player."""
        await self._connection.tcp.client_status(0)

    async def request_stats(self) -> None:
        """
        Request the player's statistics from the server.

        Notes
        -----
        The server responds by sending the statistics,
        which are usually processed in the ``on_statistics`` handler.
        """
        await self._connection.tcp.client_status(1)

    async def request_tab_complete(self, text: str, assume_command: bool = False) -> None:
        """
        Request tab completion suggestions from the server.

        Parameters
        ----------
        text: str
            All text behind the cursor (e.g. to the left of the cursor in left-to-right languages like English).
        assume_command: bool
            If true, the server will parse Text as a command even if it doesn't start with a `/`.
            Used in the command block GUI. Defaults to False.

        Notes
        -----
        The server responds by sending completion suggestions,
        which are usually processed in the ``on_tab_complete`` handler.
        """
        await self._connection.tcp.chat_command_suggestion(text, assume_command, has_position=False,
                                                           looked_at_block=None)

    async def request_tab_complete_with_position(self, text: str, looked_at_block: Vector3D[int],
                                                 assume_command: bool = False) -> None:
        """
        Request tab completion suggestions with block position context.

        Parameters
        ----------
        text: str
            All text behind the cursor.
        looked_at_block: Vector3D[int]
            Position of the block being looked at.
        assume_command: bool
            If True, parse text as command even without `/`.

        Notes
        -----
        The server responds by sending completion suggestions,
        which are usually processed in the ``on_tab_complete`` handler.
        """
        await self._connection.tcp.chat_command_suggestion(text, assume_command, has_position=True,
                                                           looked_at_block=looked_at_block)

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
        skin_parts = (cape << 0) | (jacket << 1) | (left_sleeve << 2) | (right_sleeve << 3) | \
                     (left_pants << 4) | (right_pants << 5) | (hat << 6)
        await self._connection.tcp.client_settings(locale, view_distance, chat_mode, chat_colors, skin_parts, main_hand)

    async def send_message(self, message: str) -> None:
        """
        Send a chat message to the server.

        Parameters
        ----------
        message: str
            The message to send.
        """
        await self._connection.tcp.chat_message(message)

    async def request_advancement_tab(self, tab_id: str) -> None:
        """
        Request to open a specific advancement tab.

        Parameters
        ----------
        tab_id: str
            The advancement tab identifier, Valid tabs:

            - minecraft:story/root

            - minecraft:nether/root

            - minecraft:end/root

            - minecraft:adventure/root

            - minecraft:husbandry/root

        Notes
        -----
        The server responds by sending the advancement data,
        which are usually processed in the ``on_advancements`` handler.
        """
        await self._connection.tcp.advancement_tab(0, tab_id)

    async def close_advancement_tab(self) -> None:
        """Close the advancement tab."""
        await self._connection.tcp.advancement_tab(1)

    async def set_resource_pack_status(self, result: int) -> None:
        """
        Respond to a resource pack request.

        Parameters
        ----------
        result: int
            Status code (0=loaded, 1=declined, 2=failed, 3=accepted).
        """
        await self._connection.tcp.resource_pack_status(result)

    async def set_displayed_recipe(self, recipe_id: int) -> None:
        """
        Set the currently displayed recipe in the crafting book.

        This method sends a Crafting Book Data packet (type 0) to the server to update
        which recipe is currently being shown or highlighted in the crafting book interface.
        The recipe will be visually highlighted for the player.

        Parameters
        ----------
        recipe_id: int
            The internal ID of the recipe to display. This ID corresponds to the
            server's recipe registry and must be a valid recipe identifier.
        """
        await self._connection.tcp.crafting_book_data_displayed_recipe(recipe_id)

    async def set_crafting_book_status(self, crafting_book_open: bool, crafting_filter: bool) -> None:
        """
        Update the crafting book's open state and filter settings.

        This method sends a Crafting Book Data packet (type 1) to the server to update
        the player's crafting book interface state. Controls both the visibility of
        the crafting book and whether the crafting filter is active.

        Parameters
        ----------
        crafting_book_open: bool
            Whether the crafting book is currently opened/active in the UI.
            When True, the crafting book will be visible to the player.
        crafting_filter: bool
            Whether the crafting filter option is currently active.
            When True, only shows recipes that can be crafted with available materials.
        """
        await self._connection.tcp.crafting_book_data_status(crafting_book_open, crafting_filter)

    async def craft_recipe(self, window: Window, recipe_id: int, make_all: bool = False) -> None:
        """
        Request to craft a recipe from the recipe book.

        Sends a craft recipe request packet to the server to craft items using
        a known recipe. This is equivalent to clicking on a recipe in the recipe book.

        Parameters
        ----------
        window: Window
            The crafting window object that contains the crafting interface.
            Must be a valid crafting table or player inventory crafting area.
        recipe_id: int
            The recipe ID to craft. Must correspond to a valid recipe in the
            server's recipe registry.
        make_all: bool
            Whether to craft as many items as possible (shift-click behavior).
            When True, crafts the maximum number of items possible with available materials.
        """
        await self._connection.tcp.craft_recipe_request(window.id, recipe_id, make_all)

    async def enchant_item(self, window: Window, enchantment: int) -> None:
        """
        Request to enchant an item using the enchantment table.

        Sends an enchant item packet to apply the selected enchantment to an item
        in the enchantment table. Requires the player to have sufficient experience
        and lapis lazuli.

        Parameters
        ----------
        window: Window
            The enchantment table window object. Must be a valid enchantment table
            interface with an item placed in the enchantment slot.
        enchantment: int
            The position of the enchantment option in the enchantment table interface.
            Valid values are 0, 1, or 2 (top, middle, bottom enchantment options).
        """
        await self._connection.tcp.enchant_item(window.id, enchantment)

    async def click_window_slot(self, window: Window, slot: int, button: int, mode: int) -> None:
        """
        Perform a raw click operation on a window slot.

        This is the low-level method for all window interactions. Different combinations
        of button and mode parameters create different click behaviors (left click,
        right click, shift click, etc.).

        Parameters
        ----------
        window: Window
            The window object containing the slot to click.
        slot: int
            The slot number to click. Slot numbering starts at 0 and varies by window type.
        button: int
            The mouse button used for the click. 0=left, 1=right, 2=middle.
        mode: int
            The inventory operation mode. Different modes enable different behaviors:
            0=normal click, 1=shift click, 2=number key, 3=middle click, 4=drop, 5=drag, 6=double click.

        Notes
        -----
        Most users should prefer the higher-level methods like pickup_item() or place_item()
        instead of calling this directly.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, button, action_number, mode, clicked_item)

    async def drop_item(self, window: Window, slot: int, drop_stack: bool = False) -> None:
        """
        Drop an item from a window slot onto the ground.

        Removes an item from the specified slot and drops it as an item entity
        in the world near the player. Uses the drop operation mode (4).

        Parameters
        ----------
        window: Window
            The window object containing the slot to drop from.
        slot: int
            The slot number to drop items from. Must contain an item to drop.
        drop_stack: bool
            Whether to drop the entire stack or just one item.
            When True, drops all items in the slot. When False, drops only one item.
        """
        button = 1 if drop_stack else 0
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, button, action_number, 4, clicked_item)

    async def pickup_item(self, window: Window, slot: int) -> None:
        """
        Pick up an item from a window slot (left click).

        Performs a left-click operation on the specified slot to pick up the item.
        If the cursor already holds an item, this will attempt to merge stacks.

        Parameters
        ----------
        window: Window
            The window object containing the slot to pick up from.
        slot: int
            The slot number to pick up from. Must contain an item to pick up.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, 0, action_number, 0, clicked_item)

    async def place_item(self, window: Window, slot: int, single_item: bool = False) -> None:
        """
        Place an item in a window slot.

        Places the item currently held by the cursor into the specified slot.
        Can place either a single item or the entire stack.

        Parameters
        ----------
        window: Window
            The window object containing the slot to place into.
        slot: int
            The slot number to place the item in.
        single_item: bool
            Whether to place only one item (right-click) or the entire stack (left-click).
            When True, places only one item. When False, places the entire stack.
        """
        button = 1 if single_item else 0
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, button, action_number, 0, clicked_item)

    async def shift_click_item(self, window: Window, slot: int) -> None:
        """
        Shift-click an item for quick transfer.

        Performs a shift-click operation to quickly move items between inventory
        sections (e.g., from chest to player inventory or vice versa).

        Parameters
        ----------
        window: Window
            The window object containing the slot to shift-click.
        slot: int
            The slot number to shift-click. Must contain an item to transfer.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, 0, action_number, 1, clicked_item)

    async def hotbar_swap(self, window: Window, slot: int, hotbar_key: int) -> None:
        """
        Swap item with hotbar using number keys 1-9.

        Swaps the item in the specified slot with the item in the corresponding
        hotbar slot. This mimics pressing number keys 1-9 while hovering over a slot.

        Parameters
        ----------
        window: Window
            The window object containing the slot to swap with.
        slot: int
            The slot number to swap with the hotbar.
        hotbar_key: int
            The hotbar key (0-8, corresponding to keys 1-9).
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, hotbar_key, action_number, 2, clicked_item)

    async def middle_click_item(self, window: Window, slot: int) -> None:
        """
        Middle-click an item (creative mode only).

        Performs a middle-click operation on the specified slot. This is only
        functional in creative mode and typically duplicates the item.

        Parameters
        ----------
        window: Window
            The window object containing the slot to middle-click.
        slot: int
            The slot number to middle-click.

        Notes
        -----
        Only works in creative mode and in non-player inventories.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, 2, action_number, 3, clicked_item)

    async def double_click_item(self, window: Window, slot: int) -> None:
        """
        Double-click to collect similar items.

        Performs a double-click operation to gather all similar items from the
        inventory into the clicked slot's stack.

        Parameters
        ----------
        window: Window
            The window object containing the slot to double-click.
        slot: int
            The slot number to double-click. Should contain the item type to collect.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, 0, action_number, 6, clicked_item)

    async def click_outside_window(self, window: Window, right_click: bool = False) -> None:
        """
        Click outside window to drop held item.

        Drops the item currently held by the cursor by clicking outside the window area.
        The item will be dropped as an entity in the world.

        Parameters
        ----------
        window: Window
            The window object to click outside-of.
        right_click: bool
            Whether to perform a right-click or left-click outside the window.
        """
        button = 1 if right_click else 0
        action_number = window.get_next_action_number()
        await self._connection.tcp.click_window(window.id, -999, button, action_number, 4, None)

    async def start_drag(self, window: Window, drag_type: int = 0) -> None:
        """
        Start a drag operation.

        Initiates a drag operation for distributing items across multiple slots.
        A drag operation allows you to spread items from a stack evenly across
        multiple slots by clicking and dragging over them. For example, dragging
        a stack of 64 items over 4 slots will place 16 items in each slot.

        Must be followed by add_drag_slot() calls and end_drag().

        Parameters
        ----------
        window: Window
            The window object to start dragging in.
        drag_type: int
            The type of drag operation:
            - 0: Left drag (distributes entire stack evenly)
            - 4: Right drag (places one item per slot)
            - 8: Middle drag (creative mode only, duplicates items)
        """
        action_number = window.get_next_action_number()
        await self._connection.tcp.click_window(window.id, -999, drag_type, action_number, 5, None)

    async def add_drag_slot(self, window: Window, slot: int, drag_type: int = 1) -> None:
        """
        Add slot to drag operation.

        Adds a slot to the current drag operation. Must be called between
        start_drag() and end_drag().

        Parameters
        ----------
        window: Window
            The window object containing the slot to add.
        slot: int
            The slot number to add to the drag operation.
        drag_type: int
            The drag operation type. 1=left drag, 5=right drag, 9=middle drag.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._connection.tcp.click_window(window.id, slot, drag_type, action_number, 5, clicked_item)

    async def end_drag(self, window: Window, drag_type: int = 2) -> None:
        """
        End drag operation.

        Completes the drag operation and distributes items to all slots that
        were added with add_drag_slot().

        Parameters
        ----------
        window: Window
            The window object to end dragging in.
        drag_type: int
            The drag operation type. 2=left drag, 6=right drag, 10=middle drag.
        """
        action_number = window.get_next_action_number()
        await self._connection.tcp.click_window(window.id, -999, drag_type, action_number, 5, None)

    async def drag_distribute_items(self, window: Window, slots: list[int], drag_type: int = 0) -> None:
        """
        Distribute items across multiple slots using drag.

        Performs a complete drag operation to distribute the held item stack
        across the specified slots. This is a convenience method that combines
        start_drag(), add_drag_slot(), and end_drag().

        Parameters
        ----------
        window: Window
            The window object to perform the drag operation in.
        slots: list[int]
            List of slot numbers to distribute items to.
        drag_type: int
            The drag operation type. 0=left drag, 4=right drag, 8=middle drag.
        """
        await self.start_drag(window, drag_type)

        add_type = drag_type + 1
        for slot in slots:
            await self.add_drag_slot(window, slot, add_type)

        end_type = drag_type + 2
        await self.end_drag(window, end_type)

    async def close_window(self, window: Window) -> None:
        """
        Close a window.

        Sends a close window packet to the server to close the specified window.
        Any items in the window will be handled according to the window type.

        Parameters
        ----------
        window: Window
            The window object to close.

        Notes
        -----
        Clients send window ID 0 to close their inventory even though there's
        never an Open Window packet for the inventory.
        """
        await self._connection.tcp.close_window(window.id)

    async def set_creative_item(self, slot: int, item: Item) -> None:
        """
        Set an item in creative mode inventory slot.

        Places an item directly into the specified creative mode inventory slot.
        This bypasses normal inventory rules and can create items from nothing.

        Parameters
        ----------
        slot: int
            The inventory slot number to set the item in.
        item: Item
            The item object to place in the slot.
        """
        await self._connection.tcp.creative_inventory_action(slot, item.to_dict())

    async def clear_creative_slot(self, slot: int) -> None:
        """
        Clear an item from creative mode inventory slot.

        Removes an item from the specified creative mode inventory slot.
        The item is permanently deleted.

        Parameters
        ----------
        slot: int
            The inventory slot number to clear.
        """
        await self._connection.tcp.creative_inventory_action(slot, None)

    async def drop_creative_item(self, item: Item) -> None:
        """
        Drop an item from creative inventory into the world.

        Spawns an item entity in the world near the player without removing
        it from any inventory slot. Creates the item from nothing.

        Parameters
        ----------
        item: Item
            The item object to drop/spawn in the world.
        """
        await self._connection.tcp.creative_inventory_action(-1, item.to_dict())

    async def creative_inventory_set(self, slot: int, item: Item) -> None:
        """
        Set an item in creative inventory slot.

        Low-level method for placing items directly into creative mode inventory slots.
        This bypasses normal inventory rules and can create items from nothing.

        Parameters
        ----------
        slot: int
            The inventory slot number to set the item in.
            Use -1 to drop an item outside the inventory.
        item: Item
            The item object to place in the slot.
        """
        await self._connection.tcp.creative_inventory_action(slot, item.to_dict())

    async def creative_inventory_clear(self, slot: int) -> None:
        """
        Clear an item from creative inventory slot.

        Low-level method for removing items from creative mode inventory slots.
        The item is permanently deleted from the slot.

        Parameters
        ----------
        slot: int
            The inventory slot number to clear.
        """
        await self._connection.tcp.creative_inventory_action(slot, None)

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

    def _handle_ready(self) -> None:
        """Signal that the connection is ready."""
        self._ready.set()

    def _get_state(self, username: str) -> ConnectionState:
        """Create and return a connection state object."""
        return ConnectionState(username, tcp=self.tcp, dispatcher=self.dispatch, handle_ready=self._handle_ready)

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
        _logger.exception('Ignoring error: %s from %s, args: %s kwargs: %s', error, packet_id, args, kwargs)
