from typing import TypedDict, List, NotRequired, Dict, Any, Literal, Required


class BannerPattern(TypedDict):
    """A single pattern layer with color on a banner."""
    Pattern: str
    Color: int

class Banner(TypedDict):
    """Banner block entity with base color and optional patterns."""
    Patterns: NotRequired[List[BannerPattern]]
    Base: int
    CustomName: NotRequired[str]


class Beacon(TypedDict):
    """Beacon block entity data including levels and potion effects."""
    Levels: int
    Primary: int
    Secondary: int
    CustomName: NotRequired[str]
    Lock: str


class Sign(TypedDict):
    """Sign block entity text lines."""
    Text1: str
    Text2: str
    Text3: str
    Text4: str


MobSpawnerEntityData = TypedDict('MobSpawnerEntityData', {'id': Required[int]}, total=False)
MobSpawnerSpawnPotentialEntry = TypedDict('MobSpawnerSpawnPotentialEntry', {'weight': int,
                                                                            'Entity': MobSpawnerEntityData})
class MobSpawner(TypedDict):
    """Mob spawner entity with spawn delays, counts, and potential mobs."""
    Delay: NotRequired[int]
    MinSpawnDelay: NotRequired[int]
    MaxSpawnDelay: NotRequired[int]
    SpawnCount: NotRequired[int]
    MaxNearbyEntities: NotRequired[int]
    RequiredPlayerRange: NotRequired[int]
    SpawnRange: NotRequired[int]
    SpawnData: NotRequired[MobSpawnerEntityData]
    SpawnPotentials: NotRequired[List[MobSpawnerSpawnPotentialEntry]]
    custom_spawn_rules: NotRequired[Dict[str, Any]]


SkullOwner = TypedDict('SkullOwner', {'Id': str, 'Properties': Dict[str, Any], 'Name': str})
class Skull(TypedDict):
    """Skull block entity data including rotation and optional owner info."""
    Rot: int
    SkullType: int
    Owner: NotRequired[SkullOwner]


class FlowerPot(TypedDict):
    """Flower pot block entity holding item type and data value."""
    Item: str
    Data: int


class StructureBlock(TypedDict):
    """Structure block entity with positioning, rotation, mode, and settings."""
    metadata: str
    mirror: Literal['NONE', 'LEFT_RIGHT', 'FRONT_BACK']
    ignoreEntities: int
    powered: int
    seed: int
    author: str
    rotation: Literal['NONE', 'CLOCKWISE_90', 'CLOCKWISE_180', 'COUNTERCLOCKWISE_90']
    posX: int
    mode: Literal['SAVE', 'LOAD', 'CORNER', 'DATA']
    posY: int
    sizeX: int
    posZ: int
    integrity: float
    showair: int
    name: str
    sizeY: int
    sizeZ: int
    showboundingbox: int


EndGatewayExitPortalCords = TypedDict('EndGatewayExitPortalCords', {'X': int, 'Y': int, 'Z': int})
class EndGateway(TypedDict):
    """End gateway block entity with exit portal coordinates and age."""
    ExitPortal: EndGatewayExitPortalCords
    Age: int


class Bed(TypedDict):
    """Bed block entity representing bed color."""
    color: int
