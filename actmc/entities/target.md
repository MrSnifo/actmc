# Corrected Minecraft Entity Structure

```
entities/
├── __init__.py
├── base.py
│   ├── BaseEntity(Generic[T])
│   ├── Entity(BaseEntity[int])
│   ├── Projectile(Entity)
│   ├── Hanging(Entity)
│   ├── Living(Entity)
│   ├── Insentient(Living)
│   ├── Ambient(Insentient)
│   ├── WaterMob(Insentient)
│   ├── Creature(Insentient)
│   ├── Flying(Insentient)
│   ├── Ageable(Creature)
│   ├── Animal(Ageable)
│   ├── AbstractHorse(Animal)
│   ├── ChestedHorse(AbstractHorse)
│   ├── TameableAnimal(Animal)
│   ├── Golem(Creature)
│   ├── Monster(Creature)
│   ├── AbstractSkeleton(Monster)
│   ├── AbstractIllager(Monster)
│   └── SpellcasterIllager(AbstractIllager)
│
├── animals.py
│   ├── Pig(Animal)
│   ├── Sheep(Animal)
│   ├── Cow(Animal)
│   ├── Chicken(Animal)
│   ├── Rabbit(Animal)
│   ├── PolarBear(Animal)
│   ├── MushroomCow(Animal)  # Mooshroom
│   ├── Horse(AbstractHorse)
│   ├── ZombieHorse(AbstractHorse)
│   ├── SkeletonHorse(AbstractHorse)
│   ├── Donkey(ChestedHorse)
│   ├── Llama(ChestedHorse)
│   └── Mule(ChestedHorse)
│
├── tameable.py
│   ├── Wolf(TameableAnimal)
│   ├── Ocelot(TameableAnimal)
│   └── Parrot(TameableAnimal)
│
├── water_mobs.py
│   └── Squid(WaterMob)
│
├── monsters.py
│   ├── Creeper(Monster)
│   ├── Spider(Monster)
│   ├── CaveSpider(Spider)  # Inherits from Spider, not Monster directly
│   ├── Zombie(Monster)
│   ├── ZombieVillager(Zombie)
│   ├── PigZombie(Monster)  # ZombifiedPiglin
│   ├── Husk(Zombie)
│   ├── Giant(Monster)
│   ├── Slime(Monster)
│   ├── LavaSlime(Slime)  # MagmaCube
│   ├── Blaze(Monster)
│   ├── Enderman(Monster)
│   ├── Endermite(Monster)
│   ├── Silverfish(Monster)
│   ├── Witch(Monster)
│   ├── Guardian(Monster)
│   ├── ElderGuardian(Guardian)
│   ├── Shulker(Monster)
│   ├── WitherBoss(Monster)  # Wither
│   └── Vex(Monster)
│
├── skeletons.py
│   ├── Skeleton(AbstractSkeleton)
│   ├── WitherSkeleton(AbstractSkeleton)
│   └── Stray(AbstractSkeleton)
│
├── illagers.py
│   ├── VindicationIllager(AbstractIllager)  # Vindicator
│   ├── EvocationIllager(SpellcasterIllager)  # Evoker
│   └── IllusionIllager(SpellcasterIllager)  # Illusioner
│
├── golems.py
│   ├── IronGolem(Golem)  # VillagerGolem
│   └── Snowman(Golem)  # SnowGolem
│
├── flying.py
│   └── Ghast(Flying)
│
├── ambient.py
│   └── Bat(Ambient)
│
├── villagers.py
│   └── Villager(Ageable)
│
├── dragons.py
│   └── EnderDragon(Insentient)
│
├── projectiles.py
│   ├── Arrow(Projectile)  # Base class
│   ├── TippedArrow(Arrow)
│   ├── SpectralArrow(Arrow)
│   ├── Snowball(Projectile)
│   ├── Egg(Projectile)  # ThrownEgg
│   ├── Potion(Projectile)  # ThrownPotion
│   ├── ThrownExpBottle(Projectile)
│   ├── ThrownEnderpearl(Projectile)
│   ├── EyeOfEnderSignal(Projectile)
│   ├── Fireball(Projectile)
│   ├── SmallFireball(Fireball)
│   ├── DragonFireball(Projectile)
│   ├── WitherSkull(Fireball)
│   ├── ShulkerBullet(Projectile)
│   └── LlamaSpit(Projectile)
│
├── hanging.py
│   ├── ItemFrame(Hanging)
│   └── Painting(Hanging)
│
├── vehicles.py
│   ├── Boat(Entity)
│   ├── Minecart(Entity)  # Base class
│   ├── MinecartRideable(Minecart)
│   ├── MinecartContainer(Minecart)  # Base for storage minecarts
│   ├── MinecartChest(MinecartContainer)
│   ├── MinecartHopper(MinecartContainer)
│   ├── MinecartFurnace(Minecart)
│   ├── MinecartTNT(Minecart)
│   ├── MinecartSpawner(Minecart)
│   └── MinecartCommandBlock(Minecart)
│
├── misc.py
│   ├── Item(Entity)
│   ├── XPOrb(Entity)
│   ├── AreaEffectCloud(Entity)
│   ├── ArmorStand(Living)  # Extends Living, not Entity
│   ├── FallingBlock(Entity)  # FallingSand
│   ├── FireworksRocket(Entity)  # Fireworks
│   ├── TNTPrimed(Entity)
│   ├── LeashKnot(Entity)
│   ├── EvocationFangs(Entity)
│   ├── FishingHook(Entity)  # FishingBobber
│   └── EnderCrystal(Entity)
```

## Key Corrections Made:

### 1. **Added Missing Base Classes**
- `Projectile(Entity)` - base for all projectiles
- `Hanging(Entity)` - base for hanging entities
- `WaterMob(Insentient)` - base for water creatures
- `Ambient(Insentient)` - base for ambient creatures
- `Flying(Insentient)` - base for flying creatures
- `AbstractHorse(Animal)` - base for all horses
- `ChestedHorse(AbstractHorse)` - base for horses with chests

### 2. **Corrected Inheritance Chains**
- `Squid(WaterMob)` not `Animal`
- `ArmorStand(Living)` not `Entity`
- `EnderDragon(Insentient)` not `Entity`
- `CaveSpider(Spider)` not `Monster` directly

### 3. **Better Organization**
- Separated tameable animals into their own file
- Created specific files for specialized groups (skeletons, dragons, etc.)
- Grouped related entities more logically

### 4. **Added Missing Entities**
- `Arrow(Projectile)` as base class for arrows
- `Minecart(Entity)` as base class for minecarts
- `MinecartContainer(Minecart)` for storage minecarts
- `TNTPrimed(Entity)` for activated TNT

### 5. **Corrected Entity Names**
- Used proper internal names where they differ from display names
- Added comments for alternative names

This structure now properly reflects the inheritance hierarchy from the Minecraft protocol documentation and your base.py implementation.