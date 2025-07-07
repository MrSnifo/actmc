"""
actmc

Real-time Minecraft Event Handling and Protocol Integration in Python

:copyright: (c) 2025-present Snifo
:license: MIT, see LICENSE for more details.
"""

__title__ = 'actmc'
__version__ = '1.12.2.post1'
__license__ = 'MIT License'
__author__ = 'Snifo'
__email__ = 'Snifo@mail.com'
__github__ = 'https://github.com/mrsnifo/actmc'

from .chunk import *
from .client import *
from .errors import *
from .gateway import *
from .math import *
from .protocol import *
from .state import *
from .tcp import *
from .user import *
from . import (
    utils as utils,
    entities as entities,
    ui as ui,
)