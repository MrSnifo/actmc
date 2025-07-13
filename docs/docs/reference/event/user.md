## Player Events

### Player Health Update
- **Description**: Player health/food updated
- **Parameters**:
  - `health`: [`float`][float] - Current health
  - `food`: [`int`][int] - Food level
  - `saturation`: [`float`][float] - Food saturation
- **Usage**:
  ```python
  @client.event
  async def on_player_health_update(health: float, food: int, saturation: float) -> None:
      ...
  ```

### Player Experience Set
- **Description**: Player XP updated
- **Parameters**:
  - `level`: [`int`][int] - Current level
  - `total_xp`: [`int`][int] - Total experience
  - `progress`: [`float`][float] - Progress to next level (0.0-1.0)
- **Usage**:
  ```python
  @client.event
  async def on_player_experience_set(level: int, total_xp: int, progress: float) -> None:
      ...
  ```

### Held Slot Change
- **Description**: Hotbar slot changed
- **Parameters**:
  - `slot`: [`int`][int] - New selected slot (0-8)
- **Usage**:
  ```python
  @client.event
  async def on_held_slot_change(slot: int) -> None:
      ...
  ```

### Player Position And Look
- **Description**: Player position/orientation updated
- **Parameters**:
  - `position`: [`Vector3D`][actmc.math.Vector3D] - New position
  - `rotation`: [`Rotation`][actmc.math.Rotation] - New rotation
- **Usage**:
  ```python
  @client.event
  async def on_player_position_and_look(position: Vector3D, rotation: Rotation) -> None:
      ...
  ```

### Player Abilities Change
- **Description**: Player abilities changed
- **Usage**:
  ```python
  @client.event
  async def on_player_abilities_change() -> None:
      ...
  ```

## Player Combat

### Player Death
- **Description**: Player died
- **Parameters**:
  - `player`: [`Player`][actmc.entities.player.Player] - The player who died
  - `message`: [`Message`][actmc.ui.chat.Message] - Death message
- **Usage**:
  ```python
  @client.event
  async def on_player_death(player: Player, message: Message) -> None:
      ...
  ```

### Player Killed
- **Description**: Player killed by entity
- **Parameters**:
  - `player`: [`Player`][actmc.entities.player.Player] - The killed player
  - `killer`: [`Entity`][actmc.entities.entity.Entity] - The killer entity
  - `message`: [`Message`][actmc.ui.chat.Message] - Kill message
- **Usage**:
  ```python
  @client.event
  async def on_player_killed(player: Player, killer: Entity, message: Message) -> None:
      ...
  ```

## Use Bed
- **Description**: Player used bed
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The player entity
  - `position`: [`Vector3D`][actmc.math.Vector3D] - Bed position
- **Usage**:
  ```python
  @client.event
  async def on_use_bed(entity: Entity, position: Vector3D) -> None:
      ...
  ```