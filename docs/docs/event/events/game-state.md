## Game State Events

### Game State Change
- **Description**: Game state changed
- **Parameters**:
  - `reason`: [`int`][int] - Change reason ID
  - `value`: [`float`][float] - New value
- **Usage**:
  ```python
  @client.event
  async def on_game_state_change(reason: int, value: float) -> None:
      ...
  ```

### Statistics
- **Description**: Statistics updated
- **Parameters**:
  - `stats`: [`List`][typing.List][[`Tuple`][typing.Tuple][[`str`][str], [`int`][int]]] - List of (statistic, value) pairs
- **Usage**:
  ```python
  @client.event
  async def on_statistics(stats: List[Tuple[str, int]]) -> None:
      ...
  ```