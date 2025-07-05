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
    from typing import Dict, List, Tuple

__all__ = ('Scoreboard',)


class Scoreboard:
    """
    Minecraft Scoreboard Objective representation and packet parser.

    Attributes
    ----------
    name: str
        Unique name for the objective (max 16 chars).
    display_text: str
        Text to be displayed for the score (max 32 chars).
    score_type: str
        Type of score ("integer" or "hearts").
    scores: Dict[str, int]
        Dictionary mapping entity names to their scores.
    is_displayed: bool
        Whether this objective is currently being displayed.
    display_position: int
        Position where the scoreboard is displayed (0-18).
    """

    __slots__ = ('name', 'display_text', 'score_type', 'scores', 'is_displayed', 'display_position')

    def __init__(self, name: str, display_text: str | None = None, score_type: str | None = None) -> None:
        self.name: str = name
        self.display_text: str = display_text or name
        self.score_type: str = score_type or "integer"
        self.scores: Dict[str, int] = {}
        self.is_displayed: bool = False
        self.display_position: int = -1

    def set_score(self, entity_name: str, value: int) -> None:
        """
        Set or update a score for an entity.

        Parameters
        ----------
        entity_name: str
            Name of the entity (username or UUID).
        value: int
            The score value.
        """
        self.scores[entity_name] = value

    def remove_score(self, entity_name: str) -> None:
        """
        Remove an entity's score.

        Parameters
        ----------
        entity_name: str
            Name of the entity to remove.
        """
        self.scores.pop(entity_name, None)

    def get_score(self, entity_name: str) -> int:
        """
        Get the score for a specific entity.

        Parameters
        ----------
        entity_name: str
            Name of the entity.

        Returns
        -------
        int
            The score of the entity, or 0 if not found.
        """
        return self.scores.get(entity_name, 0)

    def get_all_scores(self) -> Dict[str, int]:
        """
        Get a copy of all scores.

        Returns
        -------
        Dict[str, int]
            A dictionary mapping entity names to scores.
        """
        return self.scores.copy()

    def get_sorted_scores(self, reverse: bool = True) -> List[Tuple[str, int]]:
        """
        Get all scores sorted by score value.

        Parameters
        ----------
        reverse: bool
            Whether to sort in descending order.

        Returns
        -------
        List[Tuple[str, int]]
            List of (entity_name, score) tuples sorted by score.
        """
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=reverse)

    def get_player_scores(self) -> Dict[str, int]:
        """
        Get scores for players (entity names without hyphens).

        Returns
        -------
        Dict[str, int]
            Mapping of player names to their scores.
        """
        return {name: score for name, score in self.scores.items() if '-' not in name}

    def get_entity_scores(self) -> Dict[str, int]:
        """
        Get scores for entities (entity names with hyphens, i.e., UUIDs).

        Returns
        -------
        Dict[str, int]
            Mapping of entity UUIDs to their scores.
        """
        return {name: score for name, score in self.scores.items() if '-' in name}

    def clear_scores(self) -> None:
        """
        Remove all scores from the scoreboard.
        """
        self.scores.clear()

    def is_hearts_type(self) -> bool:
        """
        Check if this scoreboard uses the 'hearts' type.

        Returns
        -------
        bool
            True if score_type is "hearts", else False.
        """
        return self.score_type == "hearts"

    def is_integer_type(self) -> bool:
        """
        Check if this scoreboard uses the 'integer' type.

        Returns
        -------
        bool
            True if score_type is "integer", else False.
        """
        return self.score_type == "integer"

    def has_scores(self) -> bool:
        """
        Check if any scores are present.

        Returns
        -------
        bool
            True if at least one score exists.
        """
        return bool(self.scores)

    def score_count(self) -> int:
        """
        Get the number of entities with scores.

        Returns
        -------
        int
            Number of scores.
        """
        return len(self.scores)

    def update_display_info(self, display_text: str, score_type: str) -> None:
        """
        Update the scoreboard's display text and score type.

        Parameters
        ----------
        display_text: str
            New display text.
        score_type: str
            New score type ("integer" or "hearts").
        """
        self.display_text = display_text
        self.score_type = score_type

    def set_displayed(self, displayed: bool, position: int = -1) -> None:
        """
        Mark this scoreboard as displayed or hidden.

        Parameters
        ----------
        displayed: bool
            Whether the scoreboard is displayed.
        position: int, optional
            Display position (0-18).
        """
        self.is_displayed = displayed
        self.display_position = position if displayed else -1

    def get_display_position_name(self) -> str:
        """
        Get a human-readable name for the display position.

        Returns
        -------
        str
            Name of the display position (e.g., "sidebar", "team sidebar (color 5)").
        """
        if not self.is_displayed:
            return "not displayed"

        position_names = {
            0: "list",
            1: "sidebar",
            2: "below name"
        }

        if self.display_position in position_names:
            return position_names[self.display_position]
        elif 3 <= self.display_position <= 18:
            team_color = self.display_position - 3
            return f"team sidebar (color {team_color})"
        else:
            return f"position {self.display_position}"

    def is_team_sidebar(self) -> bool:
        """
        Check if the scoreboard is displayed in a team sidebar.

        Returns
        -------
        bool
            True if displayed in team sidebar (positions 3-18), else False.
        """
        return self.is_displayed and 3 <= self.display_position <= 18

    def get_top_scores(self, count: int = 10) -> List[Tuple[str, int]]:
        """
        Get the top N scores.

        Parameters
        ----------
        count: int
            Number of top scores to return.

        Returns
        -------
        List[Tuple[str, int]]
            List of (entity_name, score) tuples for the top scores.
        """
        return self.get_sorted_scores(reverse=True)[:count]

    def get_bottom_scores(self, count: int = 10) -> List[Tuple[str, int]]:
        """
        Get the bottom N scores.

        Parameters
        ----------
        count: int
            Number of bottom scores to return.

        Returns
        -------
        List[Tuple[str, int]]
            List of (entity_name, score) tuples for the bottom scores.
        """
        return self.get_sorted_scores(reverse=False)[:count]

    def __repr__(self) -> str:
        return f"<Scoreboard name='{self.name}', scores={len(self.scores)}>"
