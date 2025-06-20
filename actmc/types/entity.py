from typing import Literal, AnyStr, Union

BlockEntityActionName = Union[Literal[
    'mob_spawner',
    'command_block',
    'beacon',
    'mob_head',
    'flower_pot',
    'banner',
    'structure',
    'end_gateway',
    'sign',
    'shulker_box',
    'bed'
], AnyStr]