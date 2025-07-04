from typing import Dict

class ScoreboardObjective:
    """
    Minecraft Scoreboard Objective representation and packet parser.

    Attributes
    ----------
    name: str
        Unique name for the objective (max 16 chars)
    display_text: str
        Text to be displayed for the score (max 32 chars)
    score_type: str
        Type of score ("integer" or "hearts")
    scores: dict
        Dictionary mapping entity names to their scores
    is_displayed: bool
        Whether this objective is currently being displayed
    display_position: int
        Position where the scoreboard is displayed (0-18)
    """

    __slots__ = ('name', 'display_text', 'score_type', 'scores', 'is_displayed', 'display_position')


    def __init__(self, name: str, display_text: str = None, score_type: str = None) -> None:
        self.name: str = name
        self.display_text: str = display_text or name
        self.score_type: str = score_type or "integer"
        self.scores: Dict[str, int]  = {}
        self.is_displayed: bool = False
        self.display_position: int = -1

    def set_score(self, entity_name: str, value: int) -> None:
        """
        Set or update a score for an entity.

        Parameters
        ----------
        entity_name : str
            Name of the entity (username for players, UUID for entities)
        value : int
            Score value to set
        """
        self.scores[entity_name] = value

    def remove_score(self, entity_name: str) -> None:
        """
        Remove a score for an entity.

        Parameters
        ----------
        entity_name : str
            Name of the entity to remove score for
        """
        self.scores.pop(entity_name, None)

    def get_score(self, entity_name: str) -> int:
        """
        Get score for an entity.

        Parameters
        ----------
        entity_name : str
            Name of the entity

        Returns
        -------
        int
            Score value, or 0 if not found
        """
        return self.scores.get(entity_name, 0)

    def get_all_scores(self) -> dict:
        """
        Get all scores in this objective.

        Returns
        -------
        dict
            Dictionary mapping entity names to scores
        """
        return self.scores.copy()

    def get_sorted_scores(self, reverse: bool = True) -> list:
        """
        Get scores sorted by value.

        Parameters
        ----------
        reverse : bool, default True
            Sort in descending order (highest first)

        Returns
        -------
        list
            List of (entity_name, score) tuples sorted by score
        """
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=reverse)

    def get_player_scores(self) -> dict:
        """
        Get scores for players only (entity names without hyphens).

        Returns
        -------
        dict
            Dictionary mapping player names to scores
        """
        return {name: score for name, score in self.scores.items() if '-' not in name}

    def get_entity_scores(self) -> dict:
        """
        Get scores for entities only (entity names with hyphens - UUIDs).

        Returns
        -------
        dict
            Dictionary mapping entity UUIDs to scores
        """
        return {name: score for name, score in self.scores.items() if '-' in name}

    def clear_scores(self) -> None:
        """Clear all scores from this objective."""
        self.scores.clear()

    def is_hearts_type(self) -> bool:
        """
        Check if score type is hearts.

        Returns
        -------
        bool
            True if score_type is "hearts"
        """
        return self.score_type == "hearts"

    def is_integer_type(self) -> bool:
        """
        Check if score type is integer.

        Returns
        -------
        bool
            True if score_type is "integer"
        """
        return self.score_type == "integer"

    def has_scores(self) -> bool:
        """
        Check if this objective has any scores.

        Returns
        -------
        bool
            True if there are any scores
        """
        return bool(self.scores)

    def score_count(self) -> int:
        """
        Get the number of scores in this objective.

        Returns
        -------
        int
            Number of entities with scores
        """
        return len(self.scores)

    def update_display_info(self, display_text: str, score_type: str) -> None:
        """
        Update the display information for this objective.

        Parameters
        ----------
        display_text : str
            New display text
        score_type : str
            New score type ("integer" or "hearts")
        """
        self.display_text = display_text
        self.score_type = score_type

    def set_displayed(self, displayed: bool, position: int = -1) -> None:
        """
        Set whether this objective is currently displayed.

        Parameters
        ----------
        displayed : bool
            True if objective is being displayed
        position : int, optional
            Display position (0-18), -1 if not displayed
        """
        self.is_displayed = displayed
        self.display_position = position if displayed else -1

    def get_display_position_name(self) -> str:
        """
        Get human-readable name for display position.

        Returns
        -------
        str
            Name of the display position
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
        Check if this objective is displayed in a team-specific sidebar.

        Returns
        -------
        bool
            True if displayed in team sidebar (positions 3-18)
        """
        return self.is_displayed and 3 <= self.display_position <= 18

    def get_top_scores(self, count: int = 10) -> list:
        """
        Get the top N scores from this objective.

        Parameters
        ----------
        count : int, default 10
            Number of top scores to return

        Returns
        -------
        list
            List of (entity_name, score) tuples for top scores
        """
        return self.get_sorted_scores(reverse=True)[:count]

    def get_bottom_scores(self, count: int = 10) -> list:
        """
        Get the bottom N scores from this objective.

        Parameters
        ----------
        count : int, default 10
            Number of bottom scores to return

        Returns
        -------
        list
            List of (entity_name, score) tuples for bottom scores
        """
        return self.get_sorted_scores(reverse=False)[:count]

    def __eq__(self, other) -> bool:
        """Check equality based on objective name."""
        if not isinstance(other, ScoreboardObjective):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Hash based on objective name for use in sets/dicts."""
        return hash(self.name)

    def __repr__(self) -> str:
        return f"<ScoreboardObjective name='{self.name}', scores={len(self.scores)}>"

