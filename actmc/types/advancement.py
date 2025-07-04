from typing import TypedDict, Dict, Any, Optional, List

class CriterionProgress(TypedDict):
    achieved: bool
    date_of_achieving: Optional[int]


class AdvancementProgress(TypedDict):
    criteria: Dict[str, CriterionProgress]


class AdvancementDisplay(TypedDict):
    title: Any
    description: Any
    icon: Optional[Any]
    frame_type: int
    flags: int
    background_texture: Optional[str]
    x_coord: float
    y_coord: float


class Advancement(TypedDict):
    parent_id: Optional[str]
    display_data: Optional[AdvancementDisplay]
    criteria: Dict[str, None]
    requirements: List[List[str]]