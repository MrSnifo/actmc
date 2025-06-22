from __future__ import annotations

from typing import List, Optional, Dict, Any, Literal
from ..types.entities import block
from ..ui.chat import Message
from ..math import Vector3D

class BlockEntity:
    __slots__ = ('id',)

    def __init__(self, entity_id: str) -> None:
        self.id: str = entity_id

    def __eq__(self, other: BlockEntity) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f"<BlockEntity id={self.id}>"


class Banner(BlockEntity):
    __slots__ = ('base', 'patterns', 'custom_name')

    def __init__(self, entity_id: str, data: block.Banner) -> None:
        super().__init__(entity_id)
        self.base: int = data['Base']
        self.patterns: List[block.BannerPattern] = data.get('Patterns', [])
        self.custom_name: Optional[str] = data.get('CustomName', None)

    def __repr__(self) -> str:
        return f"<Banner id={self.id}, base={self.base}>"


class Beacon(BlockEntity):
    __slots__ = ('primary', 'secondary', 'levels', 'lock', 'custom_name')

    def __init__(self, entity_id: str, data: block.Beacon) -> None:
        super().__init__(entity_id)
        self.primary: int = data['Primary']
        self.secondary: int = data['Secondary']
        self.levels: int = data['Levels']
        self.lock: Optional[str] = data['Lock'] or None
        self.custom_name: Optional[str] = data.get('CustomName', None)

    def __repr__(self) -> str:
        return f"<Beacon id={self.id}, primary={self.primary}, secondary={self.secondary}, levels={self.levels}>"


class Sign(BlockEntity):
    __slots__ = ('text_1', 'text_2', 'text_3', 'text_4')

    def __init__(self, entity_id: str, data: block.Sign) -> None:
        super().__init__(entity_id)
        self.text_1: Message = Message(data['Text1'], to_json=True)
        self.text_2: Message = Message(data['Text2'], to_json=True)
        self.text_3: Message = Message(data['Text3'], to_json=True)
        self.text_4: Message = Message(data['Text4'], to_json=True)

    def __repr__(self) -> str:
        return f"<Beacon id={self.id}>"



class MobSpawner(BlockEntity):
    __slots__ = (
        'delay',
        'min_spawn_delay',
        'max_spawn_delay',
        'spawn_count',
        'max_nearby_entities',
        'required_player_range',
        'spawn_range',
        'spawn_data',
        'spawn_potentials',
        'custom_spawn_rules',
    )

    def __init__(self, entity_id: str, data: block.MobSpawner) -> None:
        super().__init__(entity_id)
        self.delay: int = data.get('Delay', 20)
        self.min_spawn_delay: int = data.get('MinSpawnDelay', 200)
        self.max_spawn_delay: int = data.get('MaxSpawnDelay', 800)
        self.spawn_count: int = data.get('SpawnCount', 4)
        self.max_nearby_entities: int = data.get('MaxNearbyEntities', 6)
        self.required_player_range: int = data.get('RequiredPlayerRange', 16)
        self.spawn_range: int = data.get('SpawnRange', 4)
        self.spawn_data: Optional[block.MobSpawnerEntityData] = data.get('SpawnData')
        self.spawn_potentials: Optional[List[block.MobSpawnerSpawnPotentialEntry]] = data.get('SpawnPotentials')
        self.custom_spawn_rules: Optional[Dict[str, Any]] = data.get('custom_spawn_rules')

    def __repr__(self) -> str:
        return f"<MobSpawner id={self.id} delay={self.delay}, spawn_count={self.spawn_count}>"
    
class Skull(BlockEntity):
    __slots__ = ('rotation', 'skull_type', 'owner')

    def __init__(self, entity_id: str, data: block.Skull) -> None:
        super().__init__(entity_id)
        self.rotation: int = data['Rot']
        self.skull_type: int = data['SkullType']
        self.owner: Optional[block.SkullOwner] = data.get('Owner')

    @property
    def has_owner(self):
        return self.owner is not None

    def __repr__(self) -> str:
        return f"<Skull id={self.id} type={self.skull_type} rotation={self.rotation}>"


class StructureBlock(BlockEntity):
    __slots__ = (
        'metadata', 'mirror', 'ignoreEntities', 'powered', 'seed', 'author',
        'rotation', 'mode', 'size', 'position', 'integrity',
        'showair', 'name', 'showboundingbox'
    )

    def __init__(self, entity_id: str, data: block.StructureBlock) -> None:
        super().__init__(entity_id)
        self.metadata: str = data['metadata']
        self.mirror: Literal['NONE', 'LEFT_RIGHT', 'FRONT_BACK'] = data['mirror']
        self.ignoreEntities: int = data['ignoreEntities']
        self.powered: int = data['powered']
        self.seed: int = data['seed']
        self.author: str = data['author']
        self.rotation: Literal['NONE', 'CLOCKWISE_90', 'CLOCKWISE_180', 'COUNTERCLOCKWISE_90'] = data['rotation']
        self.mode: Literal['SAVE', 'LOAD', 'CORNER', 'DATA'] = data['mode']
        self.position: Vector3D = Vector3D(data['posX'], data['posY'], data['posZ'])
        self.integrity: float = data['integrity']
        self.showair: int = data['showair']
        self.name: str = data['name']
        self.size: Vector3D = Vector3D(data['sizeX'], data['sizeY'], data['sizeZ'])
        self.showboundingbox: int = data['showboundingbox']

    def __repr__(self) -> str:
        return (
            f"<StructureBlock mode={self.mode} name={self.name!r} position={self.position} size={self.size} "
            f"rotation={self.rotation} mirror={self.mirror}>"
        )


class EndGateway(BlockEntity):
    __slots__ = ('age', 'exit_portal')

    def __init__(self, entity_id: str, data: block.EndGateway) -> None:
        super().__init__(entity_id)
        self.age: int = data['Age']
        self.exit_portal: Optional[Vector3D] = Vector3D(data['ExitPortal']['X'],
                                                        data['ExitPortal']['Y'],
                                                        data['ExitPortal']['Z']) if data.get('ExitPortal') else None


    def __repr__(self) -> str:
        return f"<EndGateway id={self.id} exit_portal={self.exit_portal}>"


class ShulkerBox(BlockEntity):
    def __init__(self, entity_id: str) -> None:
        super().__init__(entity_id)

    def __repr__(self) -> str:
        return f"<ShulkerBox id={self.id}>"


class Bed(BlockEntity):
    def __init__(self, entity_id: str, data: block.Bed) -> None:
        super().__init__(entity_id)
        self.color: int = data['color']

    def __repr__(self) -> str:
        return f"<Bed id={self.id} color={self.color}>"



class FlowerPot(BlockEntity):
    __slots__ = ('item', 'data')

    def __init__(self, entity_id: str, data: block.FlowerPot) -> None:
        super().__init__(entity_id)
        self.item: str = data['Item']
        self.data: int = data['Data']

    @property
    def is_empty(self):
        return self.item == 'minecraft:air'

    def __repr__(self) -> str:
        return f"<FlowerPot item={self.item} data={self.data}>"
