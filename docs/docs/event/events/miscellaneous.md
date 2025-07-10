## Miscellaneous Events

### Plugin Message
- **Description**: Plugin message received
- **Parameters**:
  - `channel`: [`str`][str] - Message channel
  - `data`: `bytes` - Raw message data
- **Usage**:
  ```python
  @client.event
  async def on_plugin_message(channel: str, data: bytes) -> None:
      ...
  ```

## Map Data

### Map
- **Description**: Map data received
- **Parameters**:
  - `damage`: [`int`][int] - Map damage value
  - `scale`: [`int`][int] - Map scale
  - `tracking`: [`bool`][bool] - Tracking position
  - `icons`: [`List`][typing.List][Dict] - Map icons
  - `columns`: [`int`][int] - Map columns
  - `rows`: [`Optional`][typing.Optional][[`int`][int]] - Map rows
  - `offset`: [`Optional`][typing.Optional][[`Vector2D`][actmc.math.Vector2D]] - Map offset
  - `data`: [`Optional`][typing.Optional][[`List`][typing.List][[`int`][int]]] - Map color data
- **Usage**:
  ```python
  @client.event
  async def on_map(damage: int, scale: int, tracking: bool, icons: List[Dict],
               columns: int, rows: Optional[int], offset: Optional[Vector2D], 
               data: Optional[List[int]]) -> None:
      ...
  ```

## Vehicle Events

### Vehicle Move
- **Description**: Vehicle moved
- **Parameters**:
  - `position`: [`Vector3D`][actmc.math.Vector3D] - New position
  - `rotation`: [`Rotation`][actmc.math.Rotation] - New rotation
- **Usage**:
  ```python
  @client.event
  async def on_vehicle_move(position: Vector3D, rotation: Rotation) -> None:
      ...
  ```

### Open Sign Editor
- **Description**: Sign editor opened
- **Parameters**:
  - `position`: [`Vector3D`][actmc.math.Vector3D] - Sign position
- **Usage**:
  ```python
  @client.event
  async def on_open_sign_editor(position: Vector3D) -> None:
      ...
  ```

## Resource Management

### Resource Pack Send
- **Description**: Resource pack requested
- **Parameters**:
  - `url`: [`str`][str] - Resource pack URL
  - `hash`: [`str`][str] - SHA-1 hash of pack
- **Usage**:
  ```python
  @client.event
  async def on_resource_pack_send(url: str, hash: str) -> None:
      ...
  ```

### Unlock Recipes
- **Description**: Recipes unlocked
- **Parameters**:
  - `action`: [`int`][int] - Action type (0=init, 1=add, 2=remove)
  - `book_open`: [`bool`][bool] - Crafting book open
  - `filtering`: [`bool`][bool] - Filtering active
  - `recipes1`: [`List`][typing.List][[`int`][int]] - First recipe list
  - `recipes2`: [`Optional`][typing.Optional][[`List`][typing.List][[`int`][int]]] - Second recipe list (for remove action)
- **Usage**:
  ```python
  @client.event
  async def on_unlock_recipes(action: int, book_open: bool, filtering: bool,
                         recipes1: List[int], recipes2: Optional[List[int]]) -> None:
      ...
  ```

## UI Interactions

### Camera
- **Description**: Camera focused on entity
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity to focus on
- **Usage**:
  ```python
  @client.event
  async def on_camera(entity: Entity) -> None:
      ...
  ```

### Tab Complete
- **Description**: Tab completion results
- **Parameters**:
  - `matches`: [`List`][typing.List][[`str`][str]] - Possible completions
- **Usage**:
  ```python
  @client.event
  async def on_tab_complete(matches: List[str]) -> None:
      ...
  ```