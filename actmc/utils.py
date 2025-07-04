from typing import Optional, Tuple
import logging
from . import math


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

LOGGER_TRACE: int = 5
logging.addLevelName(LOGGER_TRACE, "TRACE")

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


