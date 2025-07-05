"""
The MIT License (MIT)

Copyright (c) 2025-present Snifo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Any
    from ..math import Vector2D

__all__ = ('CriterionProgress', 'AdvancementProgress', 'AdvancementDisplay', 'Advancement', 'AdvancementsData')

class CriterionProgress:
    """
    Represents the progress of a single advancement criterion.

    Attributes
    ----------
    achieved: bool
        Whether the criterion has been achieved.
    date_of_achieving: Optional[int]
        The timestamp of when the criterion was achieved.
    """
    __slots__ = ('achieved', 'date_of_achieving')

    def __init__(self, achieved: bool, date_of_achieving: Optional[int] = None) -> None:
        self.achieved = achieved
        self.date_of_achieving = date_of_achieving

    def __repr__(self) -> str:
        return f"<CriterionProgress achieved={self.achieved}, date_of_achieving={self.date_of_achieving}>"

    def is_completed(self) -> bool:
        """
        Check if the criterion is completed.

        Returns
        -------
        bool
            True if achieved, False otherwise.
        """
        return self.achieved

    def get_completion_date(self) -> Optional[int]:
        """
        Get the completion date if the criterion is achieved.

        Returns
        -------
        Optional[int]
            The completion timestamp, or None if not achieved.
        """
        return self.date_of_achieving if self.achieved else None

class AdvancementProgress:
    """
    Represents the progress across multiple advancement criteria.

    Attributes
    ----------
    criteria: Dict[str, CriterionProgress]
        Mapping of criterion IDs to their progress state.
    """
    __slots__ = ('criteria',)

    def __init__(self, criteria: Dict[str, CriterionProgress]) -> None:
        self.criteria = criteria

    def get_criterion(self, criterion_id: str) -> Optional[CriterionProgress]:
        """
        Retrieve progress for a specific criterion.

        Parameters
        ----------
        criterion_id: str
            The identifier of the criterion.

        Returns
        -------
        Optional[CriterionProgress]
            The progress state for the criterion, or None if not found.
        """
        return self.criteria.get(criterion_id)

    def is_completed(self) -> bool:
        """
        Check if all criteria are completed.

        Returns
        -------
        bool
            True if all criteria are achieved, False otherwise.
        """
        return all(criterion.achieved for criterion in self.criteria.values())

    def get_completion_percentage(self) -> float:
        """
        Calculate the percentage of completed criteria.

        Returns
        -------
        float
            The completion percentage (0.0 to 100.0).
        """
        if not self.criteria:
            return 0.0
        completed = sum(1 for criterion in self.criteria.values() if criterion.achieved)
        return (completed / len(self.criteria)) * 100.0

    def __repr__(self) -> str:
        return f"<AdvancementProgress criteria={self.criteria}>"

class AdvancementDisplay:
    """
    Holds display-related data for an advancement.

    Attributes
    ----------
    title: Any
        The title of the advancement.
    description: Any
        The description text.
    icon: Any
        The icon representation.
    frame_type: int
        Type of the frame (e.g., task, challenge).
    flags: int
        Flags controlling display features.
    background_texture: Optional[str]
        Optional background texture resource.
    position: float
        position in the advancement tree.
    """
    __slots__ = ('title', 'description', 'icon', 'frame_type', 'flags',
                 'background_texture', 'position')

    def __init__(self, title: Any, description: Any, icon: Any, frame_type: int,
                 flags: int, background_texture: Optional[str], position: Vector2D[int]) -> None:
        self.title = title
        self.description = description
        self.icon = icon
        self.frame_type = frame_type
        self.flags = flags
        self.background_texture = background_texture
        self.position = position

    def has_background_texture(self) -> bool:
        """
        Check if a background texture is present.

        Returns
        -------
        bool
            True if a background texture is set, False otherwise.
        """
        return bool(self.flags & 0x1)

    def __repr__(self) -> str:
        return f"<AdvancementDisplay title={self.title}, frame_type={self.frame_type} position={self.position}>"

class Advancement:
    """
    Represents a single advancement definition.

    Attributes
    ----------
    parent_id: Optional[str]
        The identifier of the parent advancement.
    display_data: Optional[AdvancementDisplay]
        Display information for the advancement.
    criteria: Dict[str, None]
        The criteria required for this advancement.
    requirements: List[List[str]]
        Requirement groups, where each sublist is an OR-group.
    """
    __slots__ = ('parent_id', 'display_data', 'criteria', 'requirements')

    def __init__(self, parent_id: Optional[str], display_data: Optional[AdvancementDisplay],
                 criteria: Dict[str, None], requirements: List[List[str]]) -> None:
        self.parent_id = parent_id
        self.display_data = display_data
        self.criteria = criteria
        self.requirements = requirements

    def has_parent(self) -> bool:
        """
        Check if the advancement has a parent.

        Returns
        -------
        bool
            True if a parent exists, False otherwise.
        """
        return self.parent_id is not None

    def has_display(self) -> bool:
        """
        Check if the advancement has display data.

        Returns
        -------
        bool
            True if display data is present, False otherwise.
        """
        return self.display_data is not None

    def get_criteria_ids(self) -> List[str]:
        """
        Get all criterion IDs.

        Returns
        -------
        List[str]
            List of criterion identifiers.
        """
        return list(self.criteria.keys())

    def get_all_requirements(self) -> List[str]:
        """
        Get a flattened list of all requirement IDs.

        Returns
        -------
        List[str]
            List of all requirement IDs.
        """
        return [req for req_array in self.requirements for req in req_array]

    def __repr__(self) -> str:
        return f"<Advancement parent_id={self.parent_id}, has_display={self.has_display}>"

class AdvancementsData:
    """
    Represents the full advancement data for a player/session.

    Attributes
    ----------
    reset_clear: bool
        Indicates whether all advancement data should be reset.
    advancements: Dict[str, Advancement]
        All defined advancements.
    removed_advancements: List[str]
        Advancement IDs that have been removed.
    progress: Dict[str, AdvancementProgress]
        The player's progress on each advancement.
    """
    __slots__ = ('reset_clear', 'advancements', 'removed_advancements', 'progress')

    def __init__(self, reset_clear: bool, advancements: Dict[str, Advancement],
                 removed_advancements: List[str], progress: Dict[str, AdvancementProgress]) -> None:
        self.reset_clear = reset_clear
        self.advancements = advancements
        self.removed_advancements = removed_advancements
        self.progress = progress

    def get_advancement(self, advancement_id: str) -> Optional[Advancement]:
        """
        Retrieve an advancement definition.

        Parameters
        ----------
        advancement_id: str
            The ID of the advancement.

        Returns
        -------
        Optional[Advancement]
            The advancement, or None if not found.
        """
        return self.advancements.get(advancement_id)

    def get_progress(self, advancement_id: str) -> Optional[AdvancementProgress]:
        """
        Retrieve the progress for a specific advancement.

        Parameters
        ----------
        advancement_id: str
            The ID of the advancement.

        Returns
        -------
        Optional[AdvancementProgress]
            The progress data, or None if not found.
        """
        return self.progress.get(advancement_id)

    def get_completed_advancements(self) -> List[str]:
        """
        Get a list of advancement IDs that are completed.

        Returns
        -------
        List[str]
            List of completed advancement IDs.
        """
        return [adv_id for adv_id, prog in self.progress.items() if prog.is_completed()]

    def get_advancement_count(self) -> int:
        """
        Get the number of defined advancements.

        Returns
        -------
        int
            The count of advancements.
        """
        return len(self.advancements)

    def is_reset_clear(self) -> bool:
        """
        Check if advancement data is marked for reset.

        Returns
        -------
        bool
            True if reset_clear is set, False otherwise.
        """
        return self.reset_clear

    def __repr__(self) -> str:
        return (f"<AdvancementsData reset_clear={self.reset_clear}, advancements={len(self.advancements)},"
                f" removed={len(self.removed_advancements)}, progress={len(self.progress)}>")

