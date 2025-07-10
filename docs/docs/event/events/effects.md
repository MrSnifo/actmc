## Effect Events

### Effect
- **Description**: World effect played
- **Parameters**:
  - `effect_id`: [`int`][int] - Effect ID
  - `position`: [`Vector3D`][actmc.math.Vector3D] - Effect location
  - `data`: [`int`][int] - Effect data
  - `disable_relative`: [`bool`][bool] - Disable relative volume
- **Usage**:
  ```python
  @client.event
  async def on_effect(effect_id: int, position: Vector3D, data: int, disable_relative: bool) -> None:
      ...
  ```

### Particle
- **Description**: Particle effect
- **Parameters**:
  - `id`: [`int`][int] - Particle ID
  - `long_distance`: [`bool`][bool] - Long distance rendering
  - `position`: [`Vector3D`][actmc.math.Vector3D] - Particle origin
  - `offset`: [`Vector3D`][actmc.math.Vector3D] - Particle spread
  - `data`: [`float`][float] - Particle data
  - `count`: [`int`][int] - Particle count
  - `extra`: [`List`][typing.List][[`int`][int]] - Additional particle data
- **Usage**:
  ```python
  @client.event
  async def on_particle(id: int, long_distance: bool, position: Vector3D, offset: Vector3D,
                   data: float, count: int, extra: List[int]) -> None:
      ...
  ```

## Sound Effects

### Sound Effect
- **Description**: Sound effect played
- **Parameters**:
  - `id`: [`int`][int] - Sound ID
  - `category`: [`int`][int] - Sound category
  - `position`: [`Vector3D`][actmc.math.Vector3D] - Sound location
  - `volume`: [`float`][float] - Playback volume (0.0-1.0)
  - `pitch`: [`float`][float] - Playback pitch (0.5-2.0)
- **Usage**:
  ```python
  @client.event
  async def on_sound_effect(id: int, category: int, position: Vector3D, volume: float, pitch: float) -> None:
      ...
  ```

### Named Sound Effect
- **Description**: Named sound effect played
- **Parameters**:
  - `name`: [`str`][str] - Sound name
  - `category`: [`int`][int] - Sound category
  - `position`: [`Vector3D`][actmc.math.Vector3D] - Sound location
  - `volume`: [`float`][float] - Playback volume (0.0-1.0)
  - `pitch`: [`float`][float] - Playback pitch (0.5-2.0)
- **Usage**:
  ```python
  @client.event
  async def on_named_sound_effect(name: str, category: int, position: Vector3D, volume: float, pitch: float) -> None:
      ...
  ```

## Explosions

### Explosion
- **Description**: Explosion occurred
- **Parameters**:
  - `position`: [`Vector3D`][actmc.math.Vector3D] - Explosion center
  - `radius`: [`float`][float] - Explosion radius
  - `records`: [`List`][typing.List][[`Vector3D`][actmc.math.Vector3D]] - Affected blocks
  - `motion`: [`Vector3D`][actmc.math.Vector3D] - Knockback motion
- **Usage**:
  ```python
  @client.event
  async def on_explosion(position: Vector3D, radius: float, records: List[Vector3D], 
                     motion: Vector3D) -> None:
      ...
  ```
