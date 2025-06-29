from . import entity
from . import block
from . import player
from . import misc
from . import bosses
from . import projectiles
from . import animals
from . import vehicles
from . import monsters


BLOCK_ENTITY_TYPES = {
    'minecraft:bed': block.Bed,
    'minecraft:flower_pot': block.FlowerPot,
    'minecraft:banner': block.Banner,
    'minecraft:beacon': block.Beacon,
    'minecraft:sign': block.Sign,
    'minecraft:mob_spawner': block.MobSpawner,
    'minecraft:skull': block.Skull,
    'minecraft:structure_block': block.StructureBlock,
    'minecraft:end_gateway': block.EndGateway,
    'minecraft:shulker_box': block.ShulkerBox
}

ENTITY_TYPES = {
    # Generic / Misc
    1: misc.Item,
    # 2: misc.XPOrb,
    3: misc.AreaEffectCloud,
    # 8: misc.LeashKnot,
    # 9: misc.Painting,
    18: misc.ItemFrame,
    # 20: block.PrimedTNT,
    21: block.FallingBlock,
    # 30: misc.ArmorStand,
    200: misc.EnderCrystal,

    # Projectiles
    # 7: projectiles.ThrownEgg,
    10: projectiles.Arrow,
    11: projectiles.Snowball,
    12: projectiles.Fireball,
    # 13: projectiles.SmallFireball,
    # 14: projectiles.ThrownEnderpearl,
    # 15: projectiles.EyeOfEnderSignal,
    # 16: projectiles.ThrownPotion,
    # 17: projectiles.ThrownExpBottle,
    # 19: projectiles.WitherSkull,
    # 22: projectiles.FireworksRocketEntity,
    # 24: projectiles.SpectralArrow,
    # 25: projectiles.ShulkerBullet,
    # 26: projectiles.DragonFireball,
    104: projectiles.LlamaSpit,

    # Animals
    90: animals.Pig,
    91: animals.Sheep,
    # 92: animals.Cow,
    # 93: animals.Chicken,
    94: animals.Squid,
    95: animals.Wolf,
    # 96: animals.Mooshroom,
    # 97: animals.Snowman,
    98: animals.Ocelot,
    # 99: animals.IronGolem,
    100: animals.Horse,
    101: animals.Rabbit,
    102: animals.PolarBear,
    103: animals.Llama,
    105: animals.Parrot,

    # Monsters
    4: monsters.ElderGuardian,
    5: monsters.WitherSkeleton,
    6: monsters.Stray,
    23: monsters.Husk,
    27: monsters.ZombieVillager,
    34: monsters.EvocationIllager,
    35: monsters.Vex,
    36: monsters.VindicationIllager,
    37: monsters.IllusionIllager,
    50: monsters.Creeper,
    51: monsters.Skeleton,
    52: monsters.Spider,
    # 53: monsters.Giant,
    54: monsters.Zombie,
    55: monsters.Slime,
    # 56: monsters.Ghast,
    # 57: monsters.ZombiePigman,
    58: monsters.Enderman,
    # 59: monsters.CaveSpider,
    60: monsters.Silverfish,
    61: monsters.Blaze,
    # 62: monsters.MagmaCube,
    65: animals.Bat,
    66: monsters.Witch,
    67: monsters.Endermite,
    68: monsters.Guardian,
    69: monsters.Shulker,
    120: monsters.Villager,
    33: monsters.EvocationFangs,

    # Bosses
    63: bosses.EnderDragon,
    64: bosses.Wither,

    # Vehicles
    40: vehicles.MinecartCommandBlock,
    41: vehicles.Boat,
    42: vehicles.MinecartRideable,
    43: vehicles.MinecartChest,
    44: vehicles.MinecartFurnace,
    45: vehicles.MinecartTNT,
    46: vehicles.MinecartHopper,
    47: vehicles.MinecartSpawner,
}
