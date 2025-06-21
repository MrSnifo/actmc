from typing import Optional


class Entity:
    """Base class for all entities with unique IDs"""
    __slots__ = ('_id',)

    def __init__(self, entity_id: int):
        self._id: int = entity_id

    @property
    def id(self) -> int:
        """Get the entity ID"""
        return self._id

    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"<Entity id={self.id}>"


class Player(Entity):
    """Minecraft Player class"""
    __slots__ = ('username', 'uuid', 'gamemode', 'dimension')

    def __init__(self, username: str, uuid: str, entity_id: Optional[int] = None):
        super().__init__(entity_id or 0)

        # Basic Identity
        self.username: str = username
        self.uuid: str = uuid

        self.gamemode: Optional[str] = None
        self.dimension: Optional[str] = None

    def update_login_state(self, entity_id: int, gamemode: str, dimension: str) -> None:
        """Update player state with login information from server"""
        self._id = entity_id
        self.gamemode = gamemode
        self.dimension = dimension

    @property
    def is_logged_in(self) -> bool:
        """Check if player has completed login process"""
        return self.gamemode is not None and self.dimension is not None

    def __repr__(self) -> str:
        status = "logged in" if self.is_logged_in else "not logged in"
        return f"<Player id={self.id} username={self.username} ({status})>"