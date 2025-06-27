from typing import TypedDict, Tuple

class Painting(TypedDict):
    entity_id: int
    uuid: str
    title: str
    direction: int
    pos: Tuple[int, int, int]
