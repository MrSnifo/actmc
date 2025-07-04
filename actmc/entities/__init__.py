"""
actmc.entities

An entity management module for Minecraft entities

:copyright: (c) 2025-present Snifo
:license: MIT, see LICENSE for more details.
"""

from . import ambient
from . import animals
from . import aquatic
from . import blocks
from . import dragons
from . import entity
from . import flying
from . import golems
from . import hanging
from . import illagers
from . import misc
from . import monsters
from . import player
from . import projectiles
from . import tameable
from . import vehicles
from . import villagers

BLOCK_ENTITY_TYPES = {
    'minecraft:bed': blocks.Bed,
    'minecraft:flower_pot': blocks.FlowerPot,
    'minecraft:banner': blocks.Banner,
    'minecraft:beacon': blocks.Beacon,
    'minecraft:sign': blocks.Sign,
    'minecraft:mob_spawner': blocks.MobSpawner,
    'minecraft:skull': blocks.Skull,
    'minecraft:structure_block': blocks.StructureBlock,
    'minecraft:end_gateway': blocks.EndGateway,
    'minecraft:shulker_box': blocks.ShulkerBox
}

MOB_ENTITY_TYPES = {
    4: monsters.ElderGuardian,
    5: monsters.WitherSkeleton,
    6: monsters.Stray,
    23: monsters.Husk,
    27: monsters.ZombieVillager,
    28: animals.SkeletonHorse,
    29: animals.ZombieHorse,
    31: animals.Donkey,
    32: animals.Mule,
    34: illagers.EvocationIllager,
    35: monsters.Vex,
    36: illagers.VindicationIllager,
    37: illagers.IllusionIllager,
    50: monsters.Creeper,
    51: monsters.Skeleton,
    52: monsters.Spider,
    53: monsters.Giant,
    54: monsters.Zombie,
    55: monsters.Slime,
    56: flying.Ghast,
    57: monsters.PigZombie,
    58: monsters.Enderman,
    59: monsters.CaveSpider,
    60: monsters.Silverfish,
    61: monsters.Blaze,
    62: monsters.LavaSlime,
    63: dragons.EnderDragon,
    64: monsters.WitherBoss,
    65: ambient.Bat,
    66: monsters.Witch,
    67: monsters.Endermite,
    68: monsters.Guardian,
    69: monsters.Shulker,
    90: animals.Pig,
    91: animals.Sheep,
    92: animals.Cow,
    93: animals.Chicken,
    94: aquatic.Squid,
    95: tameable.Wolf,
    96: animals.MushroomCow,
    97: golems.Snowman,
    98: tameable.Ocelot,
    99: golems.IronGolem,
    100: animals.Horse,
    101: animals.Rabbit,
    102: animals.PolarBear,
    103: animals.Llama,
    105: tameable.Parrot,
    120: villagers.Villager,
}

OBJECT_ENTITY_TYPES = {
    1: vehicles.Boat,
    2: misc.DroppedItem,
    3: misc.AreaEffectCloud,
    10: {
        0: vehicles.MinecartRideable,
        1: vehicles.MinecartChest,
        2: vehicles.MinecartFurnace,
        3: vehicles.MinecartTNT,
        4: vehicles.MinecartSpawner,
        5: vehicles.MinecartHopper,
        6: vehicles.MinecartCommandBlock,
    },
    18: hanging.ItemFrame,
    50: misc.TNTPrimed,
    51: misc.EnderCrystal,
    60: projectiles.TippedArrow,
    61: projectiles.Snowball,
    62: projectiles.Egg,
    63: projectiles.Fireball,
    64: projectiles.SmallFireball,
    65: projectiles.Enderpearl,
    66: projectiles.WitherSkull,
    67: projectiles.ShulkerBullet,
    68: projectiles.LlamaSpit,
    69: misc.XPOrb,  # Custom
    70: misc.FallingBlock,
    71: hanging.ItemFrame,
    72: projectiles.EyeOfEnderSignal,
    73: projectiles.Potion,
    75: projectiles.ExpBottle,
    76: misc.FireworksRocket,
    77: misc.LeashKnot,
    78: misc.ArmorStand,
    79: misc.EvocationFangs,
    83: hanging.Painting,  # Custom
    90: misc.FishingHook,
    91: projectiles.SpectralArrow,
    93: projectiles.DragonFireball,
    200: misc.LightningBolt  # Custom
}