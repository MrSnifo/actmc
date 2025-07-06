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
from ..entities.misc import Item

if TYPE_CHECKING:
    from typing import Optional, List, Dict, Any
    from ..types.entities import ItemData
    from .chat import Message

__all__ = ('Slot', 'Window')

class Slot:
    """
    Represents a single inventory slot that can hold an item.

    A slot is identified by an index and can contain an item with a specific count.
    Slots can be empty (no item or zero count).

    Attributes
    ----------
    index: int
        The slot's position index in the container
    item: Optional[Item]
        The item currently in this slot, None if empty
    """
    __slots__ = ('index', 'item')

    def __init__(self, index: int):
        self.index: int = index
        self.item: Optional[Item] = None

    @property
    def is_empty(self) -> bool:
        """
        Check if the slot is empty.

        A slot is considered empty if it has no item or the item count is zero or negative.

        Returns
        -------
        bool
            True if slot is empty (no item or count <= 0), False otherwise
        """
        return self.item is None

    def __repr__(self) -> str:
        return f"<Slot index={self.index}, item={self.item}>"


class Window:
    """
    Represents a GUI window containing multiple item slots.

    Windows are containers like chests, inventories, or crafting tables that hold
    items in organized slots. Each window has a type, title, and fixed number of slots.

    Attributes
    ----------
    id: int
        The window's unique identifier.
    type: str
        Window type classification.
    title: Message
        Window's display title as a Message object.
    slot_count: int
        Total number of available slots.
    slots: List[Slot]
        List of all slots in this window.
    properties: Dict[int, Any]
        Window-specific properties (furnace progress, etc.).
    _action_counter: int
        Counter for generating unique action numbers for window clicks.
    """
    __slots__ = ('id', 'type', 'title', 'slot_count', 'entity_id', 'slots', 'properties', 'is_open', '_action_counter')

    def __init__(self, window_id: int, window_type: str, title: Message, slot_count: int) -> None:
        self.id: int = window_id
        self.type: str = window_type
        self.title: Message = title
        self.slot_count: int = slot_count
        self.slots: List[Slot] = [Slot(i) for i in range(slot_count)]
        self.properties: Dict[int, Any] = {}
        self._action_counter: int = 0

    def get_next_action_number(self) -> int:
        """
        Generate the next unique action number for window clicks.

        Each window click needs a unique action number that the server uses
        to send back confirmation packets. This counter starts at 1 and
        increments for each action.

        Returns
        -------
        int
            Unique action number for this window
        """
        self._action_counter += 1
        return self._action_counter

    def set_slot(self, slot_index: int, item: Optional[ItemData]) -> Slot:
        """
        Set an item in a specific slot.

        Updates the slot at the given index with item data. If item is None,
        the slot is cleared. The slot's item and item_count are updated accordingly.

        Parameters
        ----------
        slot_index: int
            Index of the slot to modify (0-based)
        item: Optional[ItemData]
            Item data to place in slot, or None to clear the slot
            Expected keys: 'item_id', 'item_damage', 'nbt', 'item_count'

        Returns
        -------
        Slot
            The modified slot object

        Raises
        ------
        IndexError
            If slot_index is out of bounds (< 0 or >= slot_count)
        """
        if not (0 <= slot_index < len(self.slots)):
            raise IndexError(f'Slot index {slot_index} out of bounds (0-{len(self.slots) - 1})')

        slot = self.slots[slot_index]
        if item is not None:
            slot.item = Item(item['item_id'], item['item_count'], item['item_damage'], item['nbt'])
        else:
            slot.item = None
        return slot

    def get_slot(self, slot_id: int) -> Optional[Slot]:
        """
        Retrieve a slot by its index.

        Parameters
        ----------
        slot_id: int
            Index of the slot to retrieve (0-based)

        Returns
        -------
        Optional[Slot]
            The slot at the given index, or None if index is out of bounds
        """
        if 0 <= slot_id < len(self.slots):
            return self.slots[slot_id]
        return None

    def set_property(self, property_id: int, value: int) -> None:
        """
        Set a window-specific property.

        Properties are used for window-specific data like furnace cooking progress,
        enchantment table seed, etc. The meaning depends on the window type.

        Parameters
        ----------
        property_id: int
            Identifier for the property type
        value: int
            New value for the property
        """
        self.properties[property_id] = value

    def __repr__(self) -> str:
        return f"<Window id={self.id}, slot_count={self.slot_count + 1}>"