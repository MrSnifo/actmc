## GUI Events

### Window Opened

* **Description**: Window opened
* **Parameters**:

  * `window`: [`Window`][actmc.ui.gui.Window] - The opened window
* **Usage**:

  ```python
  @client.event
  async def on_window_opened(window: Window) -> None:
      ...
  ```

### Window Closed

* **Description**: Window closed
* **Parameters**:

  * `window_id`: [`int`][int] - ID of closed window
* **Usage**:

  ```python
  @client.event
  async def on_window_closed(window_id: int) -> None:
      ...
  ```

### Window Items Updated

* **Description**: Window items updated
* **Parameters**:

  * `window`: [`Window`][actmc.ui.gui.Window] - The updated window
* **Usage**:

  ```python
  @client.event
  async def on_window_items_updated(window: Window) -> None:
      ...
  ```

### Window Property Changed

* **Description**: Window property changed
* **Parameters**:

  * `window`: [`Window`][actmc.ui.gui.Window] - The window
  * `property_id`: [`int`][int] - Property ID
  * `value`: [`int`][int] - New property value
* **Usage**:

  ```python
  @client.event
  async def on_window_property_changed(window: Window, property_id: int, value: int) -> None:
      ...
  ```

## Inventory Transactions

### Transaction Confirmed

* **Description**: Window transaction confirmed
* **Note**: Client automatically confirms transactions.
* **Parameters**:

  * `window_id`: [`int`][int] - Window ID
  * `action_number`: [`int`][int] - Action number
  * `accepted`: [`bool`][bool] - Whether action was accepted
* **Usage**:

  ```python
  @client.event
  async def on_transaction_confirmed(window_id: int, action_number: int, accepted: bool) -> None:
      ...
  ```

### Craft Recipe Response

* **Description**: Crafting recipe response
* **Parameters**:

  * `window`: [`Window`][actmc.ui.gui.Window] - The crafting window
  * `recipe`: [`int`][int] - Recipe ID
* **Usage**:

  ```python
  @client.event
  async def on_craft_recipe_response(window: Window, recipe: int) -> None:
      ...
  ```

### Set Cooldown

* **Description**: Item cooldown started
* **Parameters**:

  * `item_id`: [`int`][int] - Item ID
  * `ticks`: [`int`][int] - Cooldown duration in ticks
* **Usage**:

  ```python
  @client.event
  async def on_set_cooldown(item_id: int, ticks: int) -> None:
      ...
  ```
