## Scoreboard Events

### Scoreboard Display

* **Description**: Scoreboard display updated
* **Parameters**:
  * `position`: [`int`][int] - Display position ID
  * `name`: [`str`][str] - Scoreboard name
* **Usage**:

  ```python
  @client.event
  async def on_scoreboard_display(position: int, name: str) -> None:
      ...
  ```

### Scoreboard Objective

* **Description**: Scoreboard objective updated
* **Parameters**:

  * `name`: [`str`][str] - Objective name
  * `mode`: [`int`][int] - Update mode (0 = create, 1 = remove, 2 = update)
* **Usage**:

  ```python
  @client.event
  async def on_scoreboard_objective(name: str, mode: int) -> None:
      ...
  ```

### Scoreboard Score Update

* **Description**: Scoreboard score updated
* **Parameters**:

  * `entity`: [`str`][str] - Score holder name
  * `objective`: [`str`][str] - Objective name
  * `action`: [`int`][int] - Update action (0 = create/update, 1 = remove)
  * `value`: [`Optional`][typing.Optional][[`int`][int]] - New score (None for remove)
* **Usage**:

  ```python
  @client.event
  async def on_scoreboard_score_update(entity: str, objective: str, action: int, value: Optional[int]) -> None:
      ...
  ```
