from enum import IntEnum


class NBTTagType(IntEnum):
    """NBT Tag Types"""
    TAG_END = 0
    TAG_BYTE = 1
    TAG_SHORT = 2
    TAG_INT = 3
    TAG_LONG = 4
    TAG_FLOAT = 5
    TAG_DOUBLE = 6
    TAG_BYTE_ARRAY = 7
    TAG_STRING = 8
    TAG_LIST = 9
    TAG_COMPOUND = 10
    TAG_INT_ARRAY = 11
    TAG_LONG_ARRAY = 12


class BlockEntityAction(IntEnum):
    """
    Enumeration of block entity action types.

    Each action type corresponds to a specific type of block entity update
    as defined in the Minecraft protocol.
    """
    MOB_SPAWNER = 1
    COMMAND_BLOCK = 2
    BEACON = 3
    MOB_HEAD = 4
    FLOWER_POT = 5
    BANNER = 6
    STRUCTURE = 7
    END_GATEWAY = 8
    SIGN = 9
    SHULKER_BOX = 10
    BED = 11

