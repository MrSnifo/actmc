## Player State Events

### Join
- **Description**: Player joined game
- **Usage**:
  ```python
  @client.event
  async def on_join() -> None:
      ...
  ```

### Kicked
- **Description**: Player was kicked
- **Parameters**:
  - `reason`: [`Message`][actmc.ui.chat.Message] - Kick reason message
- **Usage**:
  ```python
  @client.event
  async def on_kicked(reason: Message) -> None:
      ...
  ```

### Respawn
- **Description**: Player respawned
- **Parameters**:
  - `dimension`: [`int`][int] - Dimension ID
  - `difficulty`: [`int`][int] - Game difficulty
  - `gamemode`: [`int`][int] - Player gamemode
  - `level_type`: [`str`][str] - World type
- **Usage**:
  ```python
  @client.event
  async def on_respawn(dimension: int, difficulty: int, gamemode: int, level_type: str) -> None:
      ...
  ```
