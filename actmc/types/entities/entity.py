from typing import TypedDict, Tuple

class SpawnObject(TypedDict):
    entity_id: int
    uuid: str
    type: int
    x: float
    y: float
    z: float
    pitch: float
    yaw: float
    data: int
    velocity: Tuple[int, int, int]