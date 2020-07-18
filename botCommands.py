import discord
from discord.ext import tasks, commands
import functools
import asyncio

from config import TOKEN
from files import get_file, save_file
from botInterface import Payload, payload_manage
from tasks import Task, check_tasks

# needs to have access to everything that could possibly be pickled
from players import *
from regions import *
from vehicles import *

client = discord.Client()
bot = commands.Bot(command_prefix='~')


def region_string_to_int(region_string):
    """Converts a string '(x, y)' to a tuple (x, y)"""
    splitforms = region_string.split(',')
    nospaces = [x.replace(' ', '') for x in splitforms]
    noparens = [x.replace('(', '') for x in nospaces]
    noparens2 = [x.replace(')', '') for x in noparens]
    asints = [int(x) for x in noparens2]
    return (asints[0], asints[1])


def entity_display_to_id(entity_display):
    """Converts an entity's display name to its internal ID"""
    # * entity display will be in the form "Owners's Entity | "
    # * we need it to be in the form OWNERentity
    # first, we strip it into two words
    try:
        owner, entity = entity_display.split()
    except ValueError:  # unless it's already one word
        return entity_display
    # for owner, we remove the 's and uppercase it
    owner = owner[:-2].upper()
    # for entity, we just lowercase it
    entity = entity.lower()
    # then for the return we just combine the two
    return owner + entity


def error_helper(coro):
    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except KeyError as e:
            print(f'KeyError: {e}')
            ctx = args[0]
            return await ctx.send(f'```ERROR: No match found for the key {e}.```')
        except ValueError as e:
            print(f'ValueError: {e}')
            ctx = args[0]
            return await ctx.send('```ERROR: ValueError. Check your spaces and quotes!```')
        except AttributeError as e:
            print(f'AttributeError: {e}')
            ctx = args[0]
            return await ctx.send('```ERROR: Target does not possess that ability.```')
        except TypeError as e:
            print(f'TypeError: {e}')
            ctx = args[0]
            return await ctx.send(f'```{e}```')
        except commands.errors.MissingRequiredArgument as e:
            print(e)
            ctx = args[0]
            return await ctx.send(e)
    return wrapper


def get_entity_obj(entity_display, target_xy):
    """Gets a target entity object given a entity_string and a region

    entity_display -- The display name of an entity, e.g. "Breq's Halcyon" \n
    target_xy -- The "(x, y)" coordinates of the region containing the entity
    """
    # get the region
    Regions = get_file('Regions.pickle')
    target_region = Regions[region_string_to_int(target_xy)]
    # get the entity's ID
    entity_id = entity_display_to_id(entity_display)
    # get the entity object
    target_entity = target_region.content[entity_id]
    return target_entity


# * BG TASKS * #


# checks all tasks every x amount of time
async def task_check_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        # check all tasks and register the returning payloads as output
        payloads = check_tasks()
        # send the list of messages
        channel = bot.get_channel(734116611300261939)
        for p in payloads:
            output = payload_manage(p)
            await channel.send(output)
        # in seconds, determine how long between checks
        await asyncio.sleep(5)


# * COMMANDS * #


@bot.command()
async def ability_help(ctx, entity_display, target_xy, ability):
    """Sends a help display for an ability of a given entity

    entity_display -- The display name of the target, e.g. "Breq's Halcyon" \n
    target_xy -- The (x,y) coordinates of the target \n
    ability -- The ability name to display help for (shown by ~inspect)
    """
    target = get_entity_obj(entity_display, target_xy)
    ability_method = getattr(target, 'A_' + ability)
    arg_count = ability_method.__code__.co_argcount
    arguments = str(ability_method.__code__.co_varnames[1:arg_count])
    messages = [str(ability_method.__name__)[2:] + '- Arguments: ' + arguments,
                str(ability_method.__doc__)]
    print(messages)
    output = payload_manage(Payload(None, messages))
    print(output)
    await ctx.send(output)


@bot.command()
async def register_player(ctx, player_name):
    """Registers a Discord user under the given player_name.

    player_name -- The player name to register the Discord user under.
    """
    uid = ctx.message.author.id
    # make sure this is a unique player
    Players = get_file('Players.pickle')
    if uid in list(Players.keys()):
        await ctx.send('Error: you\'re already registered!')
        return
    # make sure this is a unique username
    if player_name in [p.name for p in Players.values()]:
        await ctx.send('Error: a player already has this name!')
        return
    # if both of those are math, initialize a Player object
    Player(uid, player_name)
    await ctx.send(f'Player {player_name} created with UID {uid}')


@bot.command()
@error_helper
async def scan_region(ctx, target_xy):
    """Returns the contents of the region matching the given coordinates

    target_xy -- The (x,y) coordinates of the region to scan"""
    Regions = get_file('Regions.pickle')
    # translate coords to actual region object
    target_region = Regions[region_string_to_int(target_xy)]
    result = target_region.scan()
    output = payload_manage(result)
    await ctx.send(output)


@bot.command()
@error_helper
async def inspect(ctx, entity_display_string, target_xy):
    """Provides details about a given entity

    entity_display_string -- The display name of the target entity
    target_xy -- The (x,y) coordinates of the region containing the target"""
    # get the obj we want
    target = get_entity_obj(entity_display_string, target_xy)
    # inspect it and send the result to payload manager
    output = payload_manage(target.A_inspect())
    await ctx.send(output)


@bot.command()
# @error_helper
async def use_ability(ctx, caster_entity_name, caster_xy, ability, *args):
    """Activates a given ability possessed by a given entity

    caster_entity_name -- The entity who's ability you wish to use
    caster_xy -- The (x,y) coordinates of the region containing the caster
    ability -- The name of the ability you want to use (shown by ~inspect)
    *args -- Any arguments needed for the ability
    """
    # get the entity object
    caster = get_entity_obj(caster_entity_name, caster_xy)
    # get the method linked to the ability
    ability_method = getattr(caster, 'A_' + ability)
    # call the method
    output = payload_manage(ability_method(*args))
    await ctx.send(output)


bot.loop.create_task(task_check_loop())
bot.run(TOKEN)
