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
from . import math
import logging
import time

if TYPE_CHECKING:
    from typing import Optional, Tuple

__all__ = ('position_to_chunk_relative', 'calculate_block_face', 'ExponentialBackoff', 'setup_logging')

def position_to_chunk_relative(position: math.Vector3D[int]) -> Tuple[math.Vector2D[int], math.Vector3D[int], int]:
    """
    Split absolute world position into chunk, relative block position, and section.

    Parameters
    ----------
    position: Vector3D[int]
        Absolute world position (x, y, z).

    Returns
    -------
    Tuple[math.Vector2D[int], math.Vector3D[int], int]
        Chunk coordinates (chunk_x, chunk_z),
        Relative position in chunk and section (rel_x, rel_y, rel_z),
        Section Y coordinate.
    """
    x, y, z = position

    # Horizontal chunk coords (16x16 blocks)
    chunk_x, rel_x = x >> 4, x & 0xF
    chunk_z, rel_z = z >> 4, z & 0xF

    # Vertical section (16 blocks tall)
    section_y, rel_y = y // 16, y % 16

    return (
        math.Vector2D(chunk_x, chunk_z),
        math.Vector3D(rel_x, rel_y, rel_z),
        section_y
    )


def calculate_block_face(player: math.Vector3D[float], block: math.Vector3D[int]) -> int:
    """
    Calculate which face of a block the player is most likely targeting.

    Parameters
    ----------
    player: Vector3D[float]
        Player's current position (usually eye level).
    block: Vector3D[int]
        Block position (x, y, z).

    Returns
    -------
    int
        Face being targeted:
        - 0: down
        - 1: up
        - 2: north
        - 3: south
        - 4: west
        - 5: east
    """

    center_x = block.x + 0.5
    center_y = block.y + 0.5
    center_z = block.z + 0.5

    dx = player.x - center_x
    dy = player.y - center_y
    dz = player.z - center_z


    abs_dx = abs(dx)
    abs_dy = abs(dy)
    abs_dz = abs(dz)

    if abs_dx >= abs_dy and abs_dx >= abs_dz:
        return 4 if dx > 0 else 5
    elif abs_dy >= abs_dx and abs_dy >= abs_dz:
        return 1 if dy > 0 else 0
    else:
        return 2 if dz < 0 else 3


class ExponentialBackoff:
    """
    Handles retry intervals with exponential backoff.

    Parameters
    ----------
    base_delay: int
        The initial delay in seconds. The delay starts at this value and increases
        exponentially with each retry.
    max_delay: int
        The maximum delay between retries. The exponential increase is capped
        at this value.
    reset_interval: int
        The period in seconds after which the retry count is reset if no errors occur.
    """

    __slots__ = ('base_delay', 'max_delay', 'reset_interval', 'retry_count', 'last_failure_time')

    def __init__(self, base_delay: int = 1, max_delay: int = 180, reset_interval: int = 300) -> None:
        self.base_delay: int = base_delay
        self.max_delay: int = max_delay
        self.reset_interval: int = reset_interval
        self.retry_count: int = 0
        self.last_failure_time: float = time.monotonic()

    def get_delay(self) -> int:
        """

        Determine the delay before the next retry attempt.

        Returns
        -------
        int
            The delay in seconds before the next retry attempt.
        """
        current_time = time.monotonic()
        elapsed_time = current_time - self.last_failure_time

        if elapsed_time > self.reset_interval:
            self.retry_count = 0

        delay = min(self.base_delay * 2 ** self.retry_count, self.max_delay)
        self.retry_count += 1
        self.last_failure_time = current_time
        return delay

LOGGER_TRACE: int = 5
logging.addLevelName(LOGGER_TRACE, 'TRACE')

def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(LOGGER_TRACE):
        self._log(LOGGER_TRACE, message, args, **kwargs)

logging.Logger.trace = trace

def setup_logging(handler: Optional[logging.Handler] = None,
                  level: Optional[int] = None,
                  root: bool = True) -> None:
    """Setup logging configuration, including custom TRACE level.
    """
    if level is None:
        level = logging.INFO

    # Accept level as string 'TRACE' or int
    if isinstance(level, str):
        level = level.upper()
        if level == "TRACE":
            level = LOGGER_TRACE
        else:
            level = getattr(logging, level, logging.INFO)

    if handler is None:
        handler = logging.StreamHandler()

    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', dt_fmt, style='{')

    if root:
        logger = logging.getLogger()
    else:
        library, _, _ = __name__.partition('.')
        logger = logging.getLogger(library)

    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
