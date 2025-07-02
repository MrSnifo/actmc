
from __future__ import annotations

from typing import TYPE_CHECKING
from ..entities.misc import Item


if TYPE_CHECKING:
    from typing import Optional, List, Dict, Any
    from ..types.entities import ItemData
    from .chat import Message


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
    item_count: int
        Number of items in this slot, 0 if empty
    """
    __slots__ = ('index', 'item', 'item_count')

    def __init__(self, slot_id: int):
        self.index: int = slot_id
        self.item: Optional[Item] = None
        self.item_count: int = 0

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
        return self.item is None or self.item_count <= 0

    def __repr__(self) -> str:

        return f"<{self.__class__.__name__} index={self.index}, item={self.item}>"


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
    """
    __slots__ = ('id', 'type', 'title', 'slot_count', 'entity_id', 'slots', 'properties', 'is_open')

    def __init__(self, window_id: int, window_type: str, title: Message, slot_count: int) -> None:
        self.id: int = window_id
        self.type: str = window_type
        self.title: Message = title
        self.slot_count: int = slot_count
        self.slots: List[Slot] = [Slot(i) for i in range(slot_count)]
        self.properties: Dict[int, Any] = {}

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
            slot.item = Item(item['item_id'], item['item_damage'], item['nbt'])
            slot.item_count = item['item_count']
        else:
            slot.item = None
            slot.item_count = 0
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
        return f"<{self.__class__.__name__} id={self.id}, slot_count={self.slot_count}>"