## World Border Events

### World Border Set Size

* **Description**: World border size set
* **Parameters**:

  * `diameter`:[`float`]\[float] - New diameter
* **Usage**:

  ```python
  @client.event
  async def on_world_border_set_size(diameter: float) -> None:
      ...
  ```

### World Border Lerp Size

* **Description**: World border size changing
* **Parameters**:

  * `old`:[`float`]\[float] - Old diameter
  * `new`:[`float`]\[float] - Target diameter
  * `speed`:[`int`]\[int] - Speed of change (ticks)
* **Usage**:

  ```python
  @client.event
  async def on_world_border_lerp_size(old: float, new: float, speed: int) -> None:
      ...
  ```

### World Border Set Center

* **Description**: World border center set
* **Parameters**:

  * `center`:[`Vector3D`]\[actmc.math.Vector3D] - New center position
* **Usage**:

  ```python
  @client.event
  async def on_world_border_set_center(center: Vector3D) -> None:
      ...
  ```

### World Border Initialize

* **Description**: World border initialized
* **Parameters**:

  * `border`:[`WorldBorder`]\[actmc.ui.border.WorldBorder] - Border data
* **Usage**:

  ```python
  @client.event
  async def on_world_border_initialize(border: WorldBorder) -> None:
      ...
  ```

### World Border Set Warning Time

* **Description**: World border warning time set
* **Parameters**:

  * `seconds`:[`int`]\[int] - Warning time in seconds
* **Usage**:

  ```python
  @client.event
  async def on_world_border_set_warning_time(seconds: int) -> None:
      ...
  ```

### World Border Set Warning Blocks

* **Description**: World border warning distance set
* **Parameters**:

  * `blocks`:[`int`]\[int] - Warning distance in blocks
* **Usage**:

  ```python
  @client.event
  async def on_world_border_set_warning_blocks(blocks: int) -> None:
      ...
  ```
