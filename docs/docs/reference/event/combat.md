## Combat Events

### Enter Combat
- **Description**: Entered combat
- **Usage**:
  ```python
  @client.event
  async def on_enter_combat() -> None:
      ...
  ```

### End Combat
- **Description**: Combat ended
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - Opponent entity
  - `duration`: [`int`][int] - Combat duration (ticks)
- **Usage**:
  ```python
  @client.event
  async def on_end_combat(entity: Entity, duration: int) -> None:
      ...
  ```
