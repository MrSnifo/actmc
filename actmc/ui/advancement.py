from typing import Dict, List, Optional, Any


class CriterionProgress:
    __slots__ = ('achieved', 'date_of_achieving')

    def __init__(self, achieved: bool, date_of_achieving: Optional[int] = None):
        self.achieved = achieved
        self.date_of_achieving = date_of_achieving

    def __repr__(self) -> str:
        return f"CriterionProgress(achieved={self.achieved}, date_of_achieving={self.date_of_achieving})"

    def is_completed(self) -> bool:
        return self.achieved

    def get_completion_date(self) -> Optional[int]:
        return self.date_of_achieving if self.achieved else None


class AdvancementProgress:
    __slots__ = ('criteria',)

    def __init__(self, criteria: Dict[str, CriterionProgress]):
        self.criteria = criteria

    def __repr__(self) -> str:
        return f"AdvancementProgress(criteria={self.criteria})"

    def get_criterion(self, criterion_id: str) -> Optional[CriterionProgress]:
        return self.criteria.get(criterion_id)

    def is_completed(self) -> bool:
        return all(criterion.achieved for criterion in self.criteria.values())

    def get_completion_percentage(self) -> float:
        if not self.criteria:
            return 0.0
        completed = sum(1 for criterion in self.criteria.values() if criterion.achieved)
        return (completed / len(self.criteria)) * 100.0


class AdvancementDisplay:
    __slots__ = ('title', 'description', 'icon', 'frame_type', 'flags',
                 'background_texture', 'x_coord', 'y_coord')

    def __init__(self, title: Any, description: Any, icon: Any, frame_type: int,
                 flags: int, background_texture: Optional[str], x_coord: float, y_coord: float):
        self.title = title
        self.description = description
        self.icon = icon
        self.frame_type = frame_type
        self.flags = flags
        self.background_texture = background_texture
        self.x_coord = x_coord
        self.y_coord = y_coord

    def __repr__(self) -> str:
        return (f"AdvancementDisplay(title={self.title}, frame_type={self.frame_type},"
                f" pos=({self.x_coord}, {self.y_coord}))")

    def has_background_texture(self) -> bool:
        return bool(self.flags & 0x1)

    def get_position(self) -> tuple[float, float]:
        return (self.x_coord, self.y_coord)


class Advancement:
    __slots__ = ('parent_id', 'display_data', 'criteria', 'requirements')

    def __init__(self, parent_id: Optional[str], display_data: Optional[AdvancementDisplay],
                 criteria: Dict[str, None], requirements: List[List[str]]):
        self.parent_id = parent_id
        self.display_data = display_data
        self.criteria = criteria
        self.requirements = requirements

    def __repr__(self) -> str:
        return (f"Advancement(parent_id={self.parent_id}, has_display={self.display_data is not None},"
                f" criteria_count={len(self.criteria)})")

    def has_parent(self) -> bool:
        return self.parent_id is not None

    def has_display(self) -> bool:
        return self.display_data is not None

    def get_criteria_ids(self) -> List[str]:
        return list(self.criteria.keys())

    def get_all_requirements(self) -> List[str]:
        """Get all requirement strings flattened"""
        return [req for req_array in self.requirements for req in req_array]


class AdvancementsData:
    __slots__ = ('reset_clear', 'advancements', 'removed_advancements', 'progress')

    def __init__(self, reset_clear: bool, advancements: Dict[str, Advancement],
                 removed_advancements: List[str], progress: Dict[str, AdvancementProgress]):
        self.reset_clear = reset_clear
        self.advancements = advancements
        self.removed_advancements = removed_advancements
        self.progress = progress

    def __repr__(self) -> str:
        return (f"AdvancementsData(reset_clear={self.reset_clear}, advancements={len(self.advancements)},"
                f" removed={len(self.removed_advancements)}, progress={len(self.progress)})")

    def get_advancement(self, advancement_id: str) -> Optional[Advancement]:
        return self.advancements.get(advancement_id)

    def get_progress(self, advancement_id: str) -> Optional[AdvancementProgress]:
        return self.progress.get(advancement_id)

    def get_completed_advancements(self) -> List[str]:
        return [adv_id for adv_id, prog in self.progress.items() if prog.is_completed()]

    def get_advancement_count(self) -> int:
        return len(self.advancements)

    def is_reset_clear(self) -> bool:
        return self.reset_clear

