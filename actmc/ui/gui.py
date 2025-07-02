from typing import Dict, List, Optional, Any
from .chat import Message
from ..entities.misc import Item
import logging

_logger = logging.getLogger(__name__)


class Slot:
    __slots__ = ('id', 'item', 'item_count')
    
    
    def __init__(self, slot_id:  int):
        self.id: int = slot_id
        self.item: Optional[Item] = None
        self.item_count: int = 0

    @property
    def is_empty(self) -> bool:
        """
        Check if the slot is empty.

        Returns
        -------
        bool
            True if slot is empty, False otherwise
        """
        return self.item is None or self.item_count <= 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, item={self.item}, item_count={self.item_count}>"


class Window:
    __slots__ = ('id', 'type', 'title', 'slot_count', 'entity_id', 'slots', 'properties', 'is_open')

    def __init__(self, window_id: int, window_type: str, title: str, slot_count: int) -> None:
        self.id: int = window_id
        self.type: str = window_type
        self.title: Message = Message(title)
        self.slot_count: int = slot_count
        self.slots: List[Slot] = [Slot(i) for i in range(slot_count)]
        self.properties: Dict[int, Any] = {}
        self.is_open = True

    def set_item(self, slot_index: int, item: Item, item_count: int) -> bool:
        if 0 <= slot_index < len(self.slots):
            slot = self.slots[slot_index]
            slot.item = item
            slot.item_count =item_count
            return True
        return False

    def get_slot(self, slot_id: int) -> Optional[Slot]:
        if 0 <= slot_id < len(self.slots):
            return self.slots[slot_id]
        return None

    def set_property(self, property_id: int, value: int) -> None:
        self.properties[property_id] = value
    
    def close(self) -> None:
        self.is_open = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, slot_count={self.slot_count}, is_open={self.is_open}>"


class FurnaceWindow(Window):
    """
    Furnace window with smelting functionality.

    Attributes
    ----------
    fuel_left: int
        Remaining fuel time in ticks
    max_fuel_time: int
        Maximum fuel burn time in ticks
    cook_progress: int
        Current cooking progress in ticks
    max_cook_time: int
        Maximum cooking time in ticks
    """
    __slots__ = ('fuel_left', 'max_fuel_time', 'cook_progress', 'max_cook_time')

    def __init__(self, window_id: int, window_type: str, title: str) -> None:
        super().__init__(window_id, window_type, title, 3)
        self.fuel_left = 0
        self.max_fuel_time = 0
        self.cook_progress = 0
        self.max_cook_time = 0

    def on_property_changed(self, property_id: int, value: int) -> None:
        """
        Handle furnace property changes.

        Parameters
        ----------
        property_id: int
            Property ID (0=fuel_left, 1=max_fuel_time, 2=cook_progress, 3=max_cook_time)
        value: int
            Property value
        """
        if property_id == 0:
            self.fuel_left = value
        elif property_id == 1:
            self.max_fuel_time = value
        elif property_id == 2:
            self.cook_progress = value
        elif property_id == 3:
            self.max_cook_time = value

    @property
    def fuel_progress(self) -> float:
        """
        Get fuel progress as percentage.

        Returns
        -------
        float
            Fuel progress (0.0 to 1.0)
        """
        if self.max_fuel_time == 0:
            return 0.0
        return self.fuel_left / self.max_fuel_time

    @property
    def cooking_progress(self) -> float:
        """
        Get cooking progress as percentage.

        Returns
        -------
        float
            Cooking progress (0.0 to 1.0)
        """
        if self.max_cook_time == 0:
            return 0.0
        return self.cook_progress / self.max_cook_time

    @property
    def is_burning(self) -> bool:
        """
        Check if furnace is currently burning fuel.

        Returns
        -------
        bool
            True if burning, False otherwise
        """
        return self.fuel_left > 0

    @property
    def is_cooking(self) -> bool:
        """
        Check if furnace is currently cooking.

        Returns
        -------
        bool
            True if cooking, False otherwise
        """
        return self.cook_progress > 0


class EnchantingWindow(Window):
    """
    Enchanting table window with enchantment functionality.

    Attributes
    ----------
    enchantment_seed: int
        Random seed for enchantments
    level_requirements: list of int
        XP level requirements for each slot
    enchantment_ids: list of int
        Enchantment IDs for each slot
    enchantment_levels: list of int
        Enchantment levels for each slot
    """

    __slots__ = ('enchantment_seed', 'level_requirements', 'enchantment_ids', 'enchantment_levels')

    def __init__(self, window_id: int, window_type: str, title: str) -> None:
        super().__init__(window_id, window_type, title, 2)
        self.enchantment_seed = 0
        self.level_requirements = [0, 0, 0]
        self.enchantment_ids = [-1, -1, -1]
        self.enchantment_levels = [-1, -1, -1]


    def on_property_changed(self, property_id: int, value: int) -> None:
        """
        Handle enchanting table property changes.

        Parameters
        ----------
        property_id: int
            Property ID (0-2=level requirements, 3=seed, 4-6=enchant IDs, 7-9=enchant levels)
        value: int
            Property value
        """
        if 0 <= property_id <= 2:
            # Level requirements for slots
            self.level_requirements[property_id] = value
            slot_name = ['top', 'middle', 'bottom'][property_id]
            _logger.debug(f"Enchanting {slot_name} slot level requirement: {value}")
        elif property_id == 3:
            # Enchantment seed
            self.enchantment_seed = value
        elif 4 <= property_id <= 6:
            # Enchantment IDs for hover
            slot_index = property_id - 4
            self.enchantment_ids[slot_index] = value
            slot_name = ['top', 'middle', 'bottom'][slot_index]
            if value == -1:
                _logger.debug(f"Enchanting {slot_name} slot: No enchantment")
            else:
                _logger.debug(f"Enchanting {slot_name} slot enchantment ID: {value}")
        elif 7 <= property_id <= 9:
            # Enchantment levels for hover
            slot_index = property_id - 7
            self.enchantment_levels[slot_index] = value
            slot_name = ['top', 'middle', 'bottom'][slot_index]
            if value == -1:
                _logger.debug(f"Enchanting {slot_name} slot: No level")
            else:
                _logger.debug(f"Enchanting {slot_name} slot level: {value}")

    def get_enchantment_info(self, slot_index: int) -> Optional[Dict[str, int]]:
        """
        Get enchantment information for a specific slot.

        Parameters
        ----------
        slot_index: int
            Slot index (0=top, 1=middle, 2=bottom)

        Returns
        -------
        dict
            Dictionary with level_requirement, enchantment_id, and enchantment_level
        """
        if 0 <= slot_index <= 2:
            return {
                'level_requirement': self.level_requirements[slot_index],
                'enchantment_id': self.enchantment_ids[slot_index],
                'enchantment_level': self.enchantment_levels[slot_index]
            }
        return None


class BeaconWindow(Window):
    """
    Beacon window with effect functionality.

    Attributes
    ----------
    power_level: int
        Beacon power level (0-4)
    first_effect: int or None
        Primary effect ID
    second_effect: int or None
        Secondary effect ID
    """

    __slots__ = ('power_level', 'first_effect', 'second_effect')

    def __init__(self, window_id: int, window_type: str, title: str) -> None:
        super().__init__(window_id, window_type, title, 1)
        self.power_level = 0
        self.first_effect = None
        self.second_effect = None

    def on_property_changed(self, property_id: int, value: int) -> None:
        """
        Handle beacon property changes.

        Parameters
        ----------
        property_id: int
            Property ID (0=power_level, 1=first_effect, 2=second_effect)
        value: int
            Property value
        """
        if property_id == 0:
            self.power_level = value
            _logger.debug(f"Beacon power level: {value}")
        elif property_id == 1:
            self.first_effect = value if value != -1 else None
        elif property_id == 2:
            self.second_effect = value if value != -1 else None


class AnvilWindow(Window):
    """
    Anvil window with repair functionality.

    Attributes
    ----------
    repair_cost: int
        XP cost for the current repair/rename operation
    """

    __slots__ = ('repair_cost',)

    def __init__(self, window_id: int, window_type: str, title: str) -> None:
        super().__init__(window_id, window_type, title, 3)
        self.repair_cost = 0


    def on_property_changed(self, property_id: int, value: int) -> None:
        """
        Handle anvil property changes.

        Parameters
        ----------
        property_id: int
            Property ID (0=repair_cost)
        value: int
            Property value
        """
        if property_id == 0:
            self.repair_cost = value
            _logger.debug(f"Anvil repair cost: {value} XP levels")


class BrewingStandWindow(Window):
    """
    Brewing stand window with brewing functionality.

    Attributes
    ----------
    brew_time: int
        Current brewing time (0-400 ticks)
    fuel_time: int
        Current fuel time (0-20 ticks)
    """

    __slots__ = ('brew_time', 'fuel_time')

    def __init__(self, window_id: int, window_type: str, title: str) -> None:
        super().__init__(window_id, window_type, title, 5)
        self.brew_time = 0
        self.fuel_time = 0

    def on_property_changed(self, property_id: int, value: int) -> None:
        """
        Handle brewing stand property changes.

        Parameters
        ----------
        property_id: int
            Property ID (0=brew_time, 1=fuel_time)
        value: int
            Property value
        """
        if property_id == 0:
            # Brew time (0-400)
            self.brew_time = value
        elif property_id == 1:
            # Fuel time (0-20)
            self.fuel_time = value

    @property
    def brew_progress(self) -> float:
        """
        Get brewing progress as percentage.

        Returns
        -------
        float
            Brewing progress (0.0 to 1.0)
        """
        return (400 - self.brew_time) / 400.0

    @property
    def fuel_progress(self) -> float:
        """
        Get fuel progress as percentage.

        Returns
        -------
        float
            Fuel progress (0.0 to 1.0)
        """
        return self.fuel_time / 20.0

    @property
    def is_brewing(self) -> bool:
        """
        Check if brewing stand is currently brewing.

        Returns
        -------
        bool
            True if brewing, False otherwise
        """
        return self.brew_time > 0


class ChestWindow(Window):
    """Standard chest window."""

    def __init__(self, window_id: int, window_type: str, slot_count: int, title: str) -> None:
        super().__init__(window_id, window_type, title, slot_count)


class HopperWindow(Window):
    """Hopper window with 5 slots."""

    def __init__(self, window_id: int, window_type: str, title: str) -> None:
        super().__init__(window_id, window_type, title, 5)
