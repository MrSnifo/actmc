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

from .math import Vector3D, Vector2D, Rotation
from typing import TYPE_CHECKING
import logging
import math

if TYPE_CHECKING:
    from typing import Optional, Tuple

__all__ = ('position_to_chunk_relative', 'calculate_block_face', 'calculate_rotation', 'setup_logging')

def position_to_chunk_relative(position: Vector3D[int]) -> Tuple[Vector2D[int], Vector3D[int], int]:
    """
    Split absolute world position into chunk, relative block position, and section.

    Parameters
    ----------
    position: Vector3D[int]
        Absolute world position (x, y, z).

    Returns
    -------
    Tuple[Vector2D[int], Vector3D[int], int]
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
        Vector2D(chunk_x, chunk_z),
        Vector3D(rel_x, rel_y, rel_z),
        section_y
    )


def calculate_block_face(observer: Vector3D[float], block: Vector3D[int]) -> int:
    """
    Calculate which face of a block the observer is most likely targeting.

    Parameters
    ----------
    observer: Vector3D[float]
        Observer's current position (usually eye level).
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
    dx = observer.x - (block.x + 0.5)
    dy = observer.y - (block.y + 0.5)
    dz = observer.z - (block.z + 0.5)

    abs_dx = abs(dx)
    abs_dy = abs(dy)
    abs_dz = abs(dz)

    if abs_dx >= abs_dy and abs_dx >= abs_dz:
        return 4 if dx > 0 else 5
    elif abs_dy >= abs_dx and abs_dy >= abs_dz:
        return 1 if dy > 0 else 0
    else:
        return 2 if dz < 0 else 3


def calculate_rotation(from_pos: Vector3D, to_pos: Vector3D) -> Rotation:
    """
    Calculates the yaw and pitch rotation to look from one position to another.

    Parameters
    ----------
    from_pos : Vector3D
        The origin position (e.g., the bot's position).
    to_pos : Vector3D
        The target position (e.g., a player's position).

    Returns
    -------
    Rotation
        A Rotation object with yaw and pitch.
    """
    dx = to_pos.x - from_pos.x
    dy = to_pos.y - from_pos.y
    dz = to_pos.z - from_pos.z

    distance_xz = math.sqrt(dx * dx + dz * dz)

    # Avoid division by zero
    if distance_xz == 0:
        pitch = -90 if dy > 0 else 90
    else:
        pitch = -math.degrees(math.atan2(dy, distance_xz))

    yaw = math.degrees(math.atan2(-dx, dz))  # Minecraft yaw: -X is positive yaw
    yaw = (yaw + 360) % 360  # Normalize to [0, 360)

    return Rotation(yaw, pitch)


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
