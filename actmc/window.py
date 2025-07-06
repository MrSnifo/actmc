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

from typing import TYPE_CHECKING
from .entities import misc

if TYPE_CHECKING:
    from .state import ConnectionState
    from typing import Optional
    from .ui import gui

__slots__ = ('UserWindow',)

class UserWindow:
    """Window management utilities for Minecraft user interactions"""

    def __init__(self, state: ConnectionState) -> None:
        self._state: ConnectionState = state


    async def set_displayed_recipe(self, recipe_id: int) -> None:
        """
        Set the currently displayed recipe in the crafting book.

        This sends a Crafting Book Data packet (type 0) to the server to update
        which recipe is currently being shown or highlighted in the crafting book.

        Parameters
        ----------
        recipe_id: int
            The internal ID of the recipe to display.
        """
        await self._state.tcp.crafting_book_data_displayed_recipe(recipe_id)

    async def set_crafting_book_status(self, crafting_book_open: bool, crafting_filter: bool) -> None:
        """
        Update the crafting book's open state and filter settings.

        This sends a Crafting Book Data packet (type 1) to the server to update
        the player's crafting book interface state, including whether it's currently
        open and whether the crafting filter is active.

        Parameters
        ----------
        crafting_book_open: bool
            Whether the crafting book is currently opened/active.
        crafting_filter: bool
            Whether the crafting filter option is currently active.
            The filter typically shows only craftable recipes.
        """
        await self._state.tcp.crafting_book_data_status(crafting_book_open, crafting_filter)

    async def craft_recipe(self, window: gui.Window, recipe_id: int, make_all: bool = False) -> None:
        """
        Request to craft a recipe from the recipe book.

        Parameters
        ----------
        window: gui.Window
            The crafting window.
        recipe_id: int
            The recipe ID to craft.
        make_all: bool
            Whether to craft as many as possible (shift-click behavior).
        """
        await self._state.tcp.craft_recipe_request(window.id, recipe_id, make_all)


    async def enchant_item(self, window: gui.Window, enchantment: int) -> None:
        """
        Request to enchant an item from the enchantment table.

        Parameters
        ----------
        window: gui.Window
            The enchantment table window.
        enchantment: int
            The position of the enchantment on the enchantment table window,
            starting with 0 as the topmost one.
        """
        await self._state.tcp.enchant_item(window.id, enchantment)

    async def click_window_slot(self, window: gui.Window, slot: int, button: int, mode: int) -> None:
        """
        Click on a slot in a window with a specific item.

        Parameters
        ----------
        window: gui.Window
            The window to click in.
        slot: int
            The clicked slot number.
        button: int
            The button used in the click.
        mode: int
            Inventory operation mode.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, button, action_number, mode, clicked_item)

    async def drop_window_item(self, window: gui.Window, slot: int, drop_stack: bool = False) -> None:
        """
        Drop an item from a window slot.

        Parameters
        ----------
        window: gui.Window
            The window containing the slot.
        slot: int
            The slot number to drop from.
        drop_stack: bool, optional
            Whether to drop the entire stack (True) or just one item (False).
            Default is False.
        """
        button = 1 if drop_stack else 0
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, button, action_number, 4, clicked_item)

    async def pickup_window_item(self, window: gui.Window, slot: int) -> None:
        """
        Pick up an item from a window slot (left click).

        Parameters
        ----------
        window: gui.Window
            The window containing the slot.
        slot: int
            The slot number to pick up from.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, 0, action_number, 0, clicked_item)

    async def place_window_item(self, window: gui.Window, slot: int, right_click: bool = False) -> None:
        """
        Place an item in a window slot.

        Parameters
        ----------
        window: gui.Window
            The window containing the slot.
        slot: int
            The slot number to place in.
        right_click: bool, optional
            Whether to right-click (place one item) or left click (place stack).
            Default is False.
        """
        button = 1 if right_click else 0
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, button, action_number, 0, clicked_item)

    async def shift_click_window_item(self, window: gui.Window, slot: int) -> None:
        """
        Shift-click an item in a window slot (quick transfer).

        Parameters
        ----------
        window: gui.Window
            The window containing the slot.
        slot: int
            The slot number to shift-click.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, 0, action_number, 1, clicked_item)

    async def hotbar_key_window_item(self, window: gui.Window, slot: int, hotbar_key: int) -> None:
        """
        Use a hotbar key (1-9) to swap with a window slot.

        Parameters
        ----------
        window: gui.Window
            The window containing the slot.
        slot: int
            The slot number to swap with.
        hotbar_key: int
            The hotbar key (0-8, corresponding to keys 1-9).

        Raises
        ------
        ValueError
            If hotbar_key is not between 0 and 8.
        """
        if not (0 <= hotbar_key <= 8):
            raise ValueError("Hotbar key must be between 0 and 8 (keys 1-9)")

        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, hotbar_key, action_number, 2, clicked_item)

    async def middle_click_window_item(self, window: gui.Window, slot: int) -> None:
        """
        Middle-click an item in a window slot (creative mode only).

        Parameters
        ----------
        window: gui.Window
            The window containing the slot.
        slot: int
            The slot number to middle-click.

        Notes
        -----
        Only defined for creative players in non-player inventories.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, 2, action_number, 3, clicked_item)

    async def double_click_window_item(self, window: gui.Window, slot: int) -> None:
        """
        Double-click an item in a window slot to collect similar items.

        Parameters
        ----------
        window: gui.Window
            The window containing the slot.
        slot: int
            The slot number to double-click.
        """
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, 0, action_number, 6, clicked_item)

    async def click_outside_window(self, window: gui.Window, right_click: bool = False) -> None:
        """
        Click outside the window (drops held item).

        Parameters
        ----------
        window: gui.Window
            The window to click outside-of.
        right_click: bool, optional
            Whether to right-click or left-click outside.
            Default is False.
        """
        button = 1 if right_click else 0
        action_number = window.get_next_action_number()
        await self._state.tcp.click_window(window.id, -999, button, action_number, 4, None)

    async def start_drag_window(self, window: gui.Window, drag_type: str = "left") -> None:
        """
        Start a drag operation in a window.

        Parameters
        ----------
        window: gui.Window
            The window to start dragging in.
        drag_type: str, optional
            The type of drag: "left", "right", or "middle".
            Default is "left".

        Raises
        ------
        ValueError
            If drag_type is not "left", "right", or "middle".
        """
        button_map = {
            "left": 0,
            "right": 4,
            "middle": 8
        }

        if drag_type not in button_map:
            raise ValueError("drag_type must be 'left', 'right', or 'middle'")

        button = button_map[drag_type]
        action_number = window.get_next_action_number()
        await self._state.tcp.click_window(window.id, -999, button, action_number, 5, None)

    async def add_drag_slot_window(self, window: gui.Window, slot: int, drag_type: str = "left") -> None:
        """
        Add a slot to the current drag operation.

        Parameters
        ----------
        window: gui.Window
            The window containing the slot.
        slot: int
            The slot to add to the drag.
        drag_type: str, optional
            The type of drag: "left", "right", or "middle".
            Default is "left".

        Raises
        ------
        ValueError
            If drag_type is not "left", "right", or "middle".
        """
        button_map = {
            "left": 1,
            "right": 5,
            "middle": 9
        }

        if drag_type not in button_map:
            raise ValueError("drag_type must be 'left', 'right', or 'middle'")

        button = button_map[drag_type]
        action_number = window.get_next_action_number()
        clicked_item = window.slots[slot].item if 0 <= slot < len(window.slots) else None
        await self._state.tcp.click_window(window.id, slot, button, action_number, 5, clicked_item)

    async def end_drag_window(self, window: gui.Window, drag_type: str = "left") -> None:
        """
        End a drag operation in a window.

        Parameters
        ----------
        window: gui.Window
            The window to end dragging in.
        drag_type: str, optional
            The type of drag: "left", "right", or "middle".
            Default is "left".

        Raises
        ------
        ValueError
            If drag_type is not "left", "right", or "middle".
        """
        button_map = {
            "left": 2,
            "right": 6,
            "middle": 10
        }

        if drag_type not in button_map:
            raise ValueError("drag_type must be 'left', 'right', or 'middle'")

        button = button_map[drag_type]
        action_number = window.get_next_action_number()
        await self._state.tcp.click_window(window.id, -999, button, action_number, 5, None)

    async def drag_distribute_items(self, window: gui.Window, slots: list[int], drag_type: str = "left") -> None:
        """
        Perform a complete drag operation to distribute items across multiple slots.

        Parameters
        ----------
        window: gui.Window
            The window to perform the drag in.
        slots: list[int]
            List of slots to distribute items to.
        drag_type: str, optional
            The type of drag: "left", "right", or "middle".
            Default is "left".

        Notes
        -----
        This method performs the complete drag sequence:
        1. Start drag
        2. Add each slot to the drag
        3. End drag
        """
        await self.start_drag_window(window, drag_type)

        for slot in slots:
            await self.add_drag_slot_window(window, slot, drag_type)

        await self.end_drag_window(window, drag_type)

    async def close_window_gui(self, window: gui.Window) -> None:
        """
        Close a window.

        Parameters
        ----------
        window: gui.Window
            The window to close.

        Notes
        -----
        Notchian clients send a Close Window packet with Window ID 0 to close
        their inventory even though there is never an Open Window packet for the inventory.
        """
        await self._state.tcp.close_window(window.id)

    # Creative mode inventory methods
    async def set_creative_item(self, slot: int, item: misc.Item) -> None:
        """
        Set an item in a creative mode inventory slot.

        Parameters
        ----------
        slot: int
            The inventory slot number to set the item in.
        item: misc.Item
            The item to place in the slot.
        """
        await self._state.tcp.creative_inventory_action(slot, item.to_dict())

    async def clear_creative_slot(self, slot: int) -> None:
        """
        Clear (delete) an item from a creative mode inventory slot.

        Parameters
        ----------
        slot: int
            The inventory slot number to clear.
        """
        await self._state.tcp.creative_inventory_action(slot, None)

    async def drop_creative_item(self, item: misc.Item) -> None:
        """
        Drop an item from creative inventory (spawn it in the world).

        Parameters
        ----------
        item: misc.Item
            The item to drop/spawn in the world.
        """
        await self._state.tcp.creative_inventory_action(-1, item.to_dict())

    async def pickup_creative_item(self, slot: int) -> None:
        """
        Pick up (delete) an item from a creative inventory slot.

        In creative mode, "picking up" an item actually deletes it from the server.
        This is equivalent to clearing the slot.

        Parameters
        ----------
        slot: int
            The inventory slot number to pick up from.
        """
        await self._state.tcp.creative_inventory_action(slot, None)

    async def creative_inventory_action(self, slot: int, clicked_item: Optional[misc.Item]) -> None:
        """
        Perform a raw creative inventory action.

        This is the underlying method that handles all creative inventory interactions.
        Consider using the more specific methods like set_creative_item(), clear_creative_slot(),
        drop_creative_item(), or pickup_creative_item() instead.

        Parameters
        ----------
        slot: int
            The inventory slot number to interact with.
            Use -1 to drop an item outside the inventory.
        clicked_item: Optional[misc.Item]
            The item to set in the slot, or None to clear the slot.
        """
        item_data = clicked_item.to_dict() if clicked_item else None
        await self._state.tcp.creative_inventory_action(slot, item_data)

