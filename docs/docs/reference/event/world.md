## World Events

### Chunk Load

* **Description**: Chunk loaded
* **Parameters**:

  * `chunk`: [`Chunk`][actmc.chunk.Chunk] - The loaded chunk data
* **Usage**:

  ```python
  @client.event
  async def on_chunk_load(chunk: Chunk) -> None:
      ...
  ```

### Chunk Unload

* **Description**: Chunk unloaded
* **Parameters**:

  * `position`: [`Vector2D`][actmc.math.Vector2D] - Chunk coordinates
* **Usage**:

  ```python
  @client.event
  async def on_chunk_unload(position: Vector2D) -> None:
      ...
  ```

## World State

### Time Update

* **Description**: World time changed
* **Parameters**:

  * `world_age`: [`int`][int] - Total world age in ticks
  * `time_of_day`: [`int`][int] - Current time of day
* **Usage**:

  ```python
  @client.event
  async def on_time_update(world_age: int, time_of_day: int) -> None:
      ...
  ```

### Spawn Position

* **Description**: World spawn point set
* **Parameters**:

  * `position`: [`Vector3D`][actmc.math.Vector3D] - New spawn coordinates
* **Usage**:

  ```python
  @client.event
  async def on_spawn_position(position: Vector3D) -> None:
      ...
  ```

## Block Changes

### Block Change

* **Description**: Single block changed
* **Parameters**:

  * `block`: [`Block`][actmc.chunk.Block] - The updated block
* **Usage**:

  ```python
  @client.event
  async def on_block_change(block: Block) -> None:
      ...
  ```

### Multi Block Change

* **Description**: Multiple blocks changed
* **Parameters**:

  * `blocks`: [`List`][typing.List][[`Block`][actmc.chunk.Block]] - List of changed blocks
* **Usage**:

  ```python
  @client.event
  async def on_multi_block_change(blocks: List[Block]) -> None:
      ...
  ```

## Block Interactions

### Block Action

* **Description**: Block event (like note block)
* **Parameters**:

  * `position`: [`Vector3D`][actmc.math.Vector3D] - Block location
  * `action_id`: [`int`][int] - Action type ID
  * `action_param`: [`int`][int] - Action parameter
  * `block_type`: [`int`][int] - Block type ID
* **Usage**:

  ```python
  @client.event
  async def on_block_action(position: Vector3D, action_id: int, action_param: int, block_type: int) -> None:
      ...
  ```

### Block Break Animation

* **Description**: Block breaking animation
* **Parameters**:

  * `entity`: [`Entity`][actmc.entities.entity.Entity] - Breaking entity
  * `position`: [`Vector3D`][actmc.math.Vector3D] - Block position
  * `stage`: [`int`][int] - Break progress (0-9)
* **Usage**:

  ```python
  @client.event
  async def on_block_break_animation(entity: Entity, position: Vector3D, stage: int) -> None:
      ...
  ```

### Block Entity Update

* **Description**: Block entity updated
* **Parameters**:

  * `position`: [`Vector3D`][actmc.math.Vector3D] - Block position
  * `entity`: [`BaseEntity`][actmc.entities.entity.BaseEntity] - Block entity data
* **Usage**:

  ```python
  @client.event
  async def on_block_entity_update(position: Vector3D, entity: BaseEntity) -> None:
      ...
  ```