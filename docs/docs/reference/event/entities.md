## Entity Events

### Spawn Player
- **Description**: Player spawned
- **Parameters**:
  - `player`: [`Player`][actmc.entities.player.Player] - The spawned player
- **Usage**:
  ```python
  @client.event
  async def on_spawn_player(player: Player) -> None:
      ...
  ```

### Spawn Mob
- **Description**: Mob spawned
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The spawned mob
  - `head_rotation`: [`Rotation`][actmc.math.Rotation] - Initial head rotation
  - `velocity`: [`Vector3D`][actmc.math.Vector3D] - Initial velocity
- **Usage**:
  ```python
  @client.event
  async def on_spawn_mob(entity: Entity, head_rotation: Rotation, velocity: Vector3D) -> None:
      ...
  ```

### Spawn Object
- **Description**: Object spawned
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The spawned object
  - `velocity`: [`Vector3D`][actmc.math.Vector3D] - Initial velocity
- **Usage**:
  ```python
  @client.event
  async def on_spawn_object(entity: Entity, velocity: Vector3D) -> None:
      ...
  ```

### Spawn Painting
- **Description**: Painting spawned
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The painting entity
- **Usage**:
  ```python
  @client.event
  async def on_spawn_painting(entity: Entity) -> None:
      ...
  ```

### Spawn Global Entity
- **Description**: Global entity spawned (lightning)
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The global entity
- **Usage**:
  ```python
  @client.event
  async def on_spawn_global_entity(entity: Entity) -> None:
      ...
  ```

### Spawn Experience Orb
- **Description**: XP orb spawned
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The XP orb
- **Usage**:
  ```python
  @client.event
  async def on_spawn_experience_orb(entity: Entity) -> None:
      ...
  ```

### Destroy Entities
- **Description**: Entities destroyed
- **Parameters**:
  - `entities`: [`List`][typing.List][[`Entity`][actmc.entities.entity.Entity]] - List of destroyed entities
- **Usage**:
  ```python
  @client.event
  async def on_destroy_entities(entities: List[Entity]) -> None:
      ...
  ```

## Entity Movement

???+ warning

    The Y position of an entity is not always a reliable indicator of whether it's on the ground.
    Always use the `on_ground` parameter for accurate ground detection.

### Entity Move
- **Description**: Entity moved
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The moving entity
  - `delta`: [`Vector3D`][actmc.math.Vector3D] - Movement delta
  - `on_ground`: [`bool`][bool] - Whether entity is on ground
- **Usage**:
  ```python
  @client.event
  async def on_entity_move(entity: Entity, delta: Vector3D, on_ground: bool) -> None:
      ...
  ```

### Entity Move Look
- **Description**: Entity moved and rotated
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The moving entity
  - `delta`: [`Vector3D`][actmc.math.Vector3D] - Movement delta
  - `on_ground`: [`bool`][bool] - Whether entity is on ground
- **Usage**:
  ```python
  @client.event
  async def on_entity_move_look(entity: Entity, delta: Vector3D, on_ground: bool) -> None:
      ...
  ```

### Entity Look
- **Description**: Entity rotated
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The rotating entity
  - `on_ground`: [`bool`][bool] - Whether entity is on ground
- **Usage**:
  ```python
  @client.event
  async def on_entity_look(entity: Entity, on_ground: bool) -> None:
      ...
  ```

### Entity Head Look
- **Description**: Entity head rotated
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
- **Usage**:
  ```python
  @client.event
  async def on_entity_head_look(entity: Entity) -> None:
      ...
  ```

### Entity Teleport
- **Description**: Entity teleported
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The teleported entity
  - `on_ground`: [`bool`][bool] - Whether entity is on ground
- **Usage**:
  ```python
  @client.event
  async def on_entity_teleport(entity: Entity, on_ground: bool) -> None:
      ...
  ```

## Entity Properties

### Entity Velocity
- **Description**: Entity velocity changed
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
  - `velocity`: [`Vector3D`][actmc.math.Vector3D] - New velocity
- **Usage**:
  ```python
  @client.event
  async def on_entity_velocity(entity: Entity, velocity: Vector3D) -> None:
      ...
  ```

### Entity Metadata
- **Description**: Entity metadata updated
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
  - `metadata`: `Dict` - Updated metadata
- **Usage**:
  ```python
  @client.event
  async def on_entity_metadata(entity: Entity, metadata: Dict) -> None:
      ...
  ```

### Entity Leash
- **Description**: Entity leashed
- **Parameters**:
  - `entity_id`: [`int`][int] - Leashed entity ID
  - `holder_id`: [`int`][int] - Holder entity ID
- **Usage**:
  ```python
  @client.event
  async def on_entity_leash(entity_id: int, holder_id: int) -> None:
      ...
  ```

### Entity Equipment
- **Description**: Entity equipment changed
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
  - `slot`: [`Slot`][actmc.ui.gui.Slot] - Equipment slot data
- **Usage**:
  ```python
  @client.event
  async def on_entity_equipment(entity: Entity, slot: Slot) -> None:
      ...
  ```

### Entity Status
- **Description**: Entity status changed
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
  - `status`: [`int`][int] - Status code
- **Usage**:
  ```python
  @client.event
  async def on_entity_status(entity: Entity, status: int) -> None:
      ...
  ```

### Entity Keep Alive
- **Description**: Entity keep-alive
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
- **Usage**:
  ```python
  @client.event
  async def on_entity_keep_alive(entity: Entity) -> None:
      ...
  ```

### Entity Propertiese
- **Description**: Entity properties updated
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
  - `properties`: `Dict` - Updated properties
- **Usage**:
  ```python
  @client.event
  async def on_entity_properties(entity: Entity, properties: Dict) -> None:
      ...
  ```

## Entity Effects

### Entity Animation
- **Description**: Entity animation played
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
  - `animation_id`: [`int`][int] - Animation ID
- **Usage**:
  ```python
  @client.event
  async def on_entity_animation(entity: Entity, animation_id: int) -> None:
      ...
  ```

### Entity Effect
- **Description**: Entity effect applied
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
  - `effect_id`: [`int`][int] - Effect ID
  - `amplifier`: [`int`][int] - Effect strength
  - `duration`: [`int`][int] - Effect duration (ticks)
  - `is_ambient`: [`bool`][bool] - If effect is ambient
  - `show_particles`: [`bool`][bool] - If particles should show
- **Usage**:
  ```python
  @client.event
  async def on_entity_effect(entity: Entity, effect_id: int, amplifier: int, 
                        duration: int, is_ambient: bool, show_particles: bool) -> None:
      ...
  ```

### Remove Entity Effect
- **Description**: Entity effect removed
- **Parameters**:
  - `entity`: [`Entity`][actmc.entities.entity.Entity] - The entity
  - `effect_id`: [`int`][int] - Effect ID being removed
- **Usage**:
  ```python
  @client.event
  async def on_remove_entity_effect(entity: Entity, effect_id: int) -> None:
      ...
  ```

## Entity Interactions



### Collect Item

???+ Warning

    This event does not synchronously update the entity's inventory state. 
    Inventory access within this event handler may reflect stale data. For accurate inventory 
    tracking, use [on_window_items_updated](ui/gui.md#window-items-updated) instead.

- **Description**: Item collected by entity
- **Parameters**:
  - `collected`: [`Entity`][actmc.entities.entity.Entity] - The collected item
  - `count`: [`int`][int] - Number collected
  - `collector`: [`Entity`][actmc.entities.entity.Entity] - The collecting entity
- **Usage**:
  ```python
  @client.event
  async def on_collect_item(collected: Entity, count: int, collector: Entity) -> None:
      ...
  ```
