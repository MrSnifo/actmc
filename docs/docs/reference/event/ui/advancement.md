## Advancement Events

### Switch Advancement Tab

* **Description**: Advancement tab switched
* **Parameters**:

  * `identifier`: [`Optional`][typing.Optional][[`str`][str]] - Tab ID (None for root)
* **Usage**:

  ```python
  @client.event
  async def on_switch_advancement_tab(identifier: Optional[str]) -> None:
      ...
  ```

### Advancements

* **Description**: Advancements updated
* **Parameters**:

  * `data`: [`AdvancementsData`][actmc.ui.advancement.AdvancementsData] - Advancement data
* **Usage**:

  ```python
  @client.event
  async def on_advancements(data: AdvancementsData) -> None:
      ...
  ```
