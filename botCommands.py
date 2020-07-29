import discord
from discord.ext import tasks, commands
import functools
import asyncio
from inspect import getfullargspec
import traceback

from config import TOKEN
from files import get_file, save_file
from botInterface import Payload, payload_manage, region_string_to_int, entity_display_to_id
from tasks import Task, check_tasks, manual_complete_all_tasks

# needs to have access to everything that could possibly be pickled
from players import *
from regions import *
from vehicles import *
from buildings import *
from actors import *

client = discord.Client()
bot = commands.Bot(command_prefix='~', case_insensitive=True)


def error_helper(coro):
    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except KeyError as e:
            print(f'KeyError: {e}')
            ctx = args[0]
            return await ctx.send(f'```ERROR: No match found for the key {e}.\nLikely, the wrong name was entered.\nCheck spaces and quotes.```')
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
    return wrapper


def get_entity_obj(entity_display, target_xy=None, target_celestial=None, target_territory=None,):
    """Gets a target entity object given a entity_string and a region

    entity_display -- The display name of an entity, e.g. "Breq's Halcyon" \n
    target_xy -- The "(x, y)" coordinates of the region containing the entity
    OR
    target_celestial -- The celestial the entity is on
    target_territory -- The territory that the entity is in
    """
    if target_xy:
        # if it's in a region
        # get the region
        Regions = get_file('Regions.pickle')
        target_region = Regions[region_string_to_int(target_xy)]
        # get the entity's ID
        entity_id = entity_display_to_id(entity_display)
        # get the entity object
        target_entity = target_region.content[entity_id]
        return target_entity
    if target_territory:
        # if it's in the territory
        Territories = get_file('Territories.pickle')
        TID = target_celestial.upper() + target_territory.lower()
        target_territory = Territories[TID]
        # get the entity's ID
        entity_id = entity_display_to_id(entity_display)
        # get the entity object
        target_entity = target_territory.content[entity_id]
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
        await asyncio.sleep(300)


@bot.event
async def on_command_error(ctx, error):
    '''Manages error messages'''
    # This prevents any commands with local handlers being handled here in on_command_error.
    if hasattr(ctx.command, 'on_error'):
        return
    if isinstance(error, commands.errors.CommandInvokeError):
        err_string = str(error)
        if 'KeyError' in err_string:
            missing_ID = err_string.split()[-1]
            messages = [f'A lookup failed when looking under the ID {missing_ID}.',
                        'You may have mistyped the entity name, or are searching in the wrong region/territory.'
                        'Try ~scanning the region or territory to make sure the entity is in it.']
            output = payload_manage(Payload(None, messages))
            await ctx.send(output)
        traceback.print_exception(type(error), error, error.__traceback__)
        return
    if isinstance(error, commands.errors.MissingRequiredArgument):
        command = ctx.command
        signature = command.signature.replace('<', '"').replace('>', '"')
        messages = [f'Improper usage or missing arguments for {command}.',
                    f'{command.name} {signature}']
        output = payload_manage(Payload(None, messages))
        await ctx.send(output)
        return
    if isinstance(error, commands.errors.CommandNotFound):
        attempt = ctx.message.content[1:]
        all_commands = bot.all_commands
        possible_commands = [c for c in all_commands if attempt in c]
        messages = [f'The command "{attempt}" does not exist']
        if possible_commands:
            messages.append(f'Did you mean: {possible_commands}?')
        else:
            messages.append(f'No commands contain "{attempt}".')
        output = payload_manage(Payload(None, messages))
        await ctx.send(output)
        return
    if isinstance(error, KeyError):
        messages = f'No result was found when looking up {error}'
        output = payload_manage(Payload(None, messages))
        await ctx.send(output)
        return
    print('Ignoring exception in command {}:'.format(ctx.command))
    traceback.print_exception(type(error), error, error.__traceback__)


# * COMMANDS * #


@bot.command()
async def ability_help(ctx, entity_display, target_xy, ability):
    """Sends a help display for an ability of a given entity

    EXAMPLE: ~ability_help "Evan's Halcyon" (0,0) move_region

    entity_display -- The display name of the target, e.g. "Breq's Halcyon" \n
    target_xy -- The (x,y) coordinates of the target \n
    ability -- The ability name to display help for (shown by ~inspect)
    """
    target = get_entity_obj(entity_display, target_xy=target_xy)
    ability_method = getattr(target, 'A_' + ability)
    arg_count = ability_method.__code__.co_argcount
    arguments = str(ability_method.__code__.co_varnames[1:arg_count])
    messages = [str(ability_method.__name__)[2:] + '- Arguments: ' + arguments,
                str(ability_method.__doc__)]
    output = payload_manage(Payload(None, messages))
    await ctx.send(output)


@bot.command()
async def register_player(ctx, player_name):
    """Registers a Discord user under the given player_name.

    EXAMPLE: ~register_player Evan

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


@bot.command(usage='"target_xy" OR ~scan "celestial_name" "territory_name"')
async def scan(ctx, *args):
    """Returns the contents of the given region or territory.

    You must have vision of the target.
    Vision is typically granted by possessing a unit in that area.

    EXAMPLE: ~scan (0,0)
    OR
    EXAMPLE: ~scan Earth North

    target_xy -- The (x,y) coordinates of the region to scan
    OR
    celestial_name -- The name of the celestial the target is on
    territory_name -- The label of the territory the target is in"""
    if len(args) == 1:
        # if the caster is in a region
        target_xy = args[0]
        storage_file = 'Regions.pickle'
        Regions = get_file(storage_file)
        # translate coords to actual region object
        target = Regions[region_string_to_int(target_xy)]
    elif len(args) == 2:
        # if the caster is in a territory
        celestial_name = args[0]
        territory_name = args[1]
        territory_label = celestial_name.upper() + territory_name.lower()
        storage_file = 'Territories.pickle'
        Territories = get_file(storage_file)
        target = Territories[territory_label]
    else:
        await ctx.send('```Error: Improper number of arguments.\n ~scan "target_xy" OR ~scan "celestial_name" "territory_name"')
        return
    # check if the user has vision of the target
    uid = ctx.message.author.id
    if not target.check_vision(uid):
        await ctx.send(f'```You do not have vision of {target}.```')
        return
    # if they do, scan it
    result = target.scan()
    output = payload_manage(result)
    await ctx.send(output)


@bot.command(usage='"entity_name" "target_xy" OR ~inspect "entity_name" "celestial_name" "territory_name"')
async def inspect(ctx, *args):
    """Provides details about a given entity

    EXAMPLE: ~inspect "Evan's Halcyon" 0,0
    OR
    EXAMPLE: ~inspect "Evan's Halcyon" Earth North

    entity_name -- The display name of the target entity
    target_xy -- The (x,y) coordinates of the region containing the target
    OR
    celestial_name -- The name of the celestial the entity is on
    territory_name -- The name of the territory the entity is in"""
    if len(args) == 2:
        # if region
        entity_name = args[0]
        target_xy = args[1]
        # get the obj we want
        target = get_entity_obj(entity_name, target_xy=target_xy)
    elif len(args) == 3:
        # if territory
        entity_name = args[0]
        celestial_name = args[1]
        territory_name = args[2]
        target = get_entity_obj(entity_name, target_celestial=celestial_name, target_territory=territory_name)
    else:
        await ctx.send('```Error: Improper number of arguments.\n ~scan "target_xy" OR ~scan "celestial_name" "territory_name"')
        return
    # inspect it and send the result to payload manager
    output = payload_manage(target.inspect())
    await ctx.send(output)


@bot.command(usage='"caster_name" "caster_xy" OR ~use_ability "caster_name" "celestial_name" "territory_name"')
async def use_ability(ctx, *args):
    """Uses an ability of a given entity in a given region.

    Activates a user interface that displays all of the caster's abilities in an interactive format.
    You can use ~inspect_entity to a view an entity's abilities.
    You can use ~ability_help to view what an ability does.


    EXAMPLE: use_ability "Evan's Halcyon" 0,0
    OR
    EXAMPLE: use_ability "Evan's Halcyon" Earth North

    caster_entity_name -- The entity whose ability you wish to use

    caster_xy -- The (x,y) coordinates of the region containing the caster
    OR
    celestial_name -- The name of the celestial the caster is on
    territory_name -- The name of the territory the caster is in
    """
    if len(args) == 2:
        # if the caster is in a region
        caster_name = args[0]
        caster_xy = args[1]
        # get the obj we want
        caster = get_entity_obj(caster_name, target_xy=caster_xy)
    elif len(args) == 3:
        # if the caster is in a territory
        caster_name = args[0]
        caster_celestial = args[1]
        caster_territory = args[2]
        caster = get_entity_obj(caster_name, target_territory=caster_territory, target_celestial=caster_celestial)
    else:
        await ctx.send('```Error: Improper number of arguments.\n ~use_ability "caster_name" "caster_xy" OR ~use_ability "caster_name" "territory_name" "celestial_name"```')
        return
    # get the names of the abilities
    ability_dict = {i: caster.abilities[i] for i in range(0, len(caster.abilities))}
    text = f'```Abilities: {ability_dict}.\nSelect the ability number you wish to cast.```'
    abilitygui = await ctx.send(text)
    emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    for emo in emojis[:len(caster.abilities)]:
        # send as many emojis as there are abilities
        await abilitygui.add_reaction(emo)

    def check(reaction, user):
        # check that message being reacted to is abilitygui
        # check that the reactor is not the bot itself
        return abilitygui.id == reaction.message.id and not user == abilitygui.author

    try:
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=120)
    except asyncio.TimeoutError:
        await ctx.send('```AbilityGUI has timed out. Re-type the command to re-activate.```')
        return

    # translate the reaction into the string of the method
    ability = ability_dict[emojis.index(reaction.emoji)]
    # get the method linked to the ability
    ability_method = getattr(caster, 'A_' + ability)
    # get the arguments to ask
    requested_args = getfullargspec(ability_method).args[1:]
    # IF there are args
    if requested_args:
        # ask for the args and wait for response
        readable_args = [a.replace('_', ' ') for a in requested_args]
        if len(readable_args) == 1:
            request_str = f'Please enter the {readable_args[0]}'
        else:
            request_str = f'Please enter the {readable_args[0]}'
            # second argument to the pentultimate argument
            for i in range(len(readable_args[1:-1])):
                request_str += f', the {readable_args[i]}'
            # add last argument
            request_str += f' and the {readable_args[-1]}'
        await ctx.send(f'```{request_str}.\nDo NOT use a tilde (~).\nSeparate each argument with spaces and use "quotes".```')

        def check(message):
            return message.author == ctx.message.author

        try:
            msg = await bot.wait_for('message', check=check, timeout=120)
        except asyncio.TimeoutError:
            await ctx.send('```AbilityGUI has timed out. Re-type the command to re-activate.```')
            return
        arg_string1 = msg.content
        # first, split off the tilde from the name
        arg_string2 = arg_string1.replace('~', '')
        # then, split on spaces
        args = arg_string2.split()
        # then we call the method
        output = payload_manage(ability_method(*args))
        await ctx.send(output)
        return
    # IF there are no args, we just call it
    output = payload_manage(ability_method())
    await ctx.send(output)
    return


@bot.command()
async def z_use_ability(ctx, caster_entity_name, caster_xy, ability, *args):
    """A more difficult but faster method of using abilities. Consider use_ability.

    EXAMPLE: z_use_ability "Evan's Halcyon" 0,0 move_region 1,0

    caster_entity_name -- The entity whose ability you wish to use
    caster_xy -- The (x,y) coordinates of the region containing the caster
    ability -- The name of the ability you want to use (shown by ~inspect_entity)
    *args -- Any arguments needed for the ability
    """
    # get the entity object
    caster = get_entity_obj(caster_entity_name, target_xy=caster_xy)
    # get the method linked to the ability
    ability_method = getattr(caster, 'A_' + ability)
    # call the method
    output = payload_manage(ability_method(*args))
    await ctx.send(output)


@bot.command()
async def inspect_territory(ctx, planet, territory):
    """Inspects a given territory of a planet

    EXAMPLE: ~inspect_territory "North" "Earth"

    territory -- The name of the territory
    planet -- The name of the planet"""
    Territories = get_file('Territories.pickle')
    # get the territory ID
    TID = planet.upper() + territory.lower()
    territory_obj = Territories[TID]
    pload = territory_obj.inspect()
    output = payload_manage(pload)
    await ctx.send(output)


@bot.command()
async def manual_complete(ctx):
    """Automatically completes all tasks"""
    payloads = manual_complete_all_tasks()
    channel = bot.get_channel(734116611300261939)
    for p in payloads:
        output = payload_manage(p)
        await channel.send(output)


bot.loop.create_task(task_check_loop())
bot.run(TOKEN)
