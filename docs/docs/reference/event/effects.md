## Effect Events

### Effect
- **Description**: World effect played  
- **Parameters**:  
  - `effect_id`: [`int`] - [Effect ID](#effect-ids)
  - `position`: [`Vector3D`] - Effect location  
  - `data`: [`int`] - Effect data (varies by effect type)  
  - `disable_relative`: [`bool`] - Disable relative volume (used for wither spawn and ender-dragon death)  
- **Usage**:  
  ```python
  @client.event
  async def on_effect(effect_id: int, position: Vector3D, data: int, disable_relative: bool) -> None:
      ...
  ```

#### Effect IDs

##### Sound Effects (1000-1037)
| ID   | Name                          | Data                              |
|------|-------------------------------|-----------------------------------|
| 1000 | Dispenser dispenses           |                                   |
| 1001 | Dispenser fails to dispense   |                                   |
| 1002 | Dispenser shoots              |                                   |
| 1003 | Ender eye launched            |                                   |
| 1004 | Firework shot                 |                                   |
| 1005 | Iron door opened              |                                   |
| 1006 | Wooden door opened            |                                   |
| 1007 | Wooden trapdoor opened        |                                   |
| 1008 | Fence gate opened             |                                   |
| 1009 | Fire extinguished             |                                   |
| 1010 | Play record                   | Record ID (special case)          |
| 1011 | Iron door closed              |                                   |
| 1012 | Wooden door closed            |                                   |
| 1013 | Wooden trapdoor closed        |                                   |
| 1014 | Fence gate closed             |                                   |
| 1015 | Ghast warns                   |                                   |
| 1016 | Ghast shoots                  |                                   |
| 1017 | Enderdragon shoots            |                                   |
| 1018 | Blaze shoots                  |                                   |
| 1019 | Zombie attacks wood door      |                                   |
| 1020 | Zombie attacks iron door      |                                   |
| 1021 | Zombie breaks wood door       |                                   |
| 1022 | Wither breaks block           |                                   |
| 1023 | Wither spawned                |                                   |
| 1024 | Wither shoots                 |                                   |
| 1025 | Bat takes off                 |                                   |
| 1026 | Zombie infects                |                                   |
| 1027 | Zombie villager converted     |                                   |
| 1028 | Ender dragon death            |                                   |
| 1029 | Anvil destroyed               |                                   |
| 1030 | Anvil used                    |                                   |
| 1031 | Anvil landed                  |                                   |
| 1032 | Portal travel                 |                                   |
| 1033 | Chorus flower grown           |                                   |
| 1034 | Chorus flower died            |                                   |
| 1035 | Brewing stand brewed          |                                   |
| 1036 | Iron trapdoor opened          |                                   |
| 1037 | Iron trapdoor closed          |                                   |

##### Particle Effects (2000-2007)
| ID   | Name                                      | Data                                              |
|------|-------------------------------------------|---------------------------------------------------|
| 2000 | Spawns 10 smoke particles                 | [Direction](#smoke-directions-for-effect-id-2000) |
| 2001 | Block break + block break sound           | Block ID                                          |
| 2002 | Splash potion + glass break sound         | Potion ID                                         |
| 2003 | Eye of Ender entity break animation       |                                                   |
| 2004 | Mob spawn particle effect: smoke + flames |                                                   |
| 2005 | Bonemeal particles                        | Particle count (0 = 15 particles)                 |
| 2006 | Dragon breath                             |                                                   |
| 2007 | Instant splash potion                     | Potion ID                                         |

##### Special Effects (3000-3001)
| ID   | Name               | Data |
|------|--------------------|------|
| 3000 | End gateway spawn  |      |
| 3001 | Enderdragon growl  |      |

#### Smoke Directions (for Effect ID 2000)
| Direction ID | Direction   |
|--------------|-------------|
| 0            | South-East  |
| 1            | South       |
| 2            | South-West  |
| 3            | East        |
| 4            | Up or middle|
| 5            | West        |
| 6            | North-East  |
| 7            | North       |
| 8            | North-West  |

#### Particle IDs

| Particle Name              | ID | Extra Data Length |
|----------------------------|----|-------------------|
| explode                    | 0  | 0                 |
| largeexplode               | 1  | 0                 |
| hugeexplosion              | 2  | 0                 |
| fireworksSpark             | 3  | 0                 |
| bubble                     | 4  | 0                 |
| splash                     | 5  | 0                 |
| wake                       | 6  | 0                 |
| suspended                  | 7  | 0                 |
| depthsuspend               | 8  | 0                 |
| crit                       | 9  | 0                 |
| magicCrit                  | 10 | 0                 |
| smoke                      | 11 | 0                 |
| largesmoke                 | 12 | 0                 |
| spell                      | 13 | 0                 |
| instantSpell               | 14 | 0                 |
| mobSpell                   | 15 | 0                 |
| mobSpellAmbient            | 16 | 0                 |
| witchMagic                 | 17 | 0                 |
| dripWater                  | 18 | 0                 |
| dripLava                   | 19 | 0                 |
| angryVillager              | 20 | 0                 |
| happyVillager              | 21 | 0                 |
| townaura                   | 22 | 0                 |
| note                       | 23 | 0                 |
| portal                     | 24 | 0                 |
| enchantmenttable           | 25 | 0                 |
| flame                      | 26 | 0                 |
| lava                       | 27 | 0                 |
| footstep                   | 28 | 0                 |
| cloud                      | 29 | 0                 |
| reddust                    | 30 | 0                 |
| snowballpoof               | 31 | 0                 |
| snowshovel                 | 32 | 0                 |
| slime                      | 33 | 0                 |
| heart                      | 34 | 0                 |
| barrier                    | 35 | 0                 |
| iconcrack_(id)_(data)      | 36 | 2                 |
| blockcrack_(id+(data<<12)) | 37 | 1                 |
| blockdust_(id)             | 38 | 1                 |
| droplet                    | 39 | 0                 |
| take                       | 40 | 0                 |
| mobappearance              | 41 | 0                 |
| dragonbreath               | 42 | 0                 |
| endrod                     | 43 | 0                 |
| damageindicator            | 44 | 0                 |
| sweepattack                | 45 | 0                 |
| fallingdust                | 46 | 1                 |
| totem                      | 47 | 0                 |
| spit                       | 48 | 0                 |


#### Special Particle Types

- **iconcrack**: Item break particles. Extra data contains item ID and damage value.
- **blockcrack**: Block break particles. Extra data contains block ID with damage shifted left by 12 bits.
- **blockdust**: Block dust particles. Extra data contains block ID.
- **fallingdust**: Falling dust particles. Extra data contains block ID.

## Sound Effects

### Sound Effect
- **Description**: Sound effect played
- **Parameters**:
  - `sound_id`: [`int`][int] - Sound ID
  - `category`: [`int`][int] - Sound category
  - `position`: [`Vector3D`][actmc.math.Vector3D] - Sound location
  - `volume`: [`float`][float] - Playback volume (0.0-1.0)
  - `pitch`: [`float`][float] - Playback pitch (0.5-2.0)
- **Usage**:
  ```python
  @client.event
  async def on_sound_effect(sound_id: int, category: int, position: Vector3D, volume: float, pitch: float) -> None:
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