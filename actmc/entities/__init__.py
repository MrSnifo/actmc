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

MOB_ENTITY_TYPES = {
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
    63: bosses.EnderDragon,
    64: bosses.Wither,
}


OBJECT_ENTITY_TYPES = {
    1: vehicles.Boat,
    10: {0: vehicles.Minecart, 1: vehicles.MinecartChest, 2: vehicles.MinecartFurnace,
         3: vehicles.MinecartTNT, 4: vehicles.MinecartSpawner, 5: vehicles.MinecartHopper,
         6: vehicles.MinecartCommandBlock},
    50: block.TNTPrimed,
    51: misc.EnderCrystal,
    # 2: misc.ItemStack,
    3: misc.AreaEffectCloud,
    70: block.FallingBlock,
    71: misc.ItemFrame,
    # 72: objects.EyeOfEnder,
    # 73: objects.ThrownPotion,
    # 75: objects.ThrownExpBottle,
    # 76: objects.FireworkRocket,
    # 77: objects.LeashKnot,
    # 78: objects.ArmorStand,
    60: projectiles.TippedArrow,  # also covers regular arrow
    61: projectiles.Snowball,
    62: projectiles.Egg,
    # 63: projectiles.GhastFireball,
    # 64: projectiles.BlazeFireCharge,
    # 65: projectiles.ThrownEnderpearl,
    66: projectiles.WitherSkull,
    # 67: projectiles.ShulkerBullet,
    68: projectiles.LlamaSpit,
    # 90: projectiles.FishingHook,
    # 91: projectiles.SpectralArrow,
    # 93: projectiles.DragonFireball,
    # 79: objects.EvocationFangs,
}


