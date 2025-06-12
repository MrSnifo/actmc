from __future__ import annotations
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import BlockState
    from io import BytesIO


class Palette(ABC):
    """Abstract base class for chunk palettes."""

    @abstractmethod
    def id_for_state(self, state: BlockState) -> int:
        """Get palette ID for a block state."""
        pass

    @abstractmethod
    def state_for_id(self, palette_id: int) -> BlockState:
        """Get block state for a palette ID."""
        pass

    @abstractmethod
    def get_bits_per_block(self) -> int:
        """Get number of bits per block for this palette."""
        pass

    @abstractmethod
    def read(self, buffer: BytesIO) -> None:
        """Read palette data from buffer."""
        pass

    @abstractmethod
    def write(self, buffer: BytesIO) -> None:
        """Write palette data to buffer."""
        pass