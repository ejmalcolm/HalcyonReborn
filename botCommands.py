import discord
from discord.ext import commands

from config import TOKEN
from files import get_file, save_file
from botInterface import Payload, payload_manage

# needs to have access to everything that could possibly be pickled
from players import *
from regions import *
from vehicles import *

client = discord.Client()
bot = commands.Bot(command_prefix='~')

# * any command that involves RETURNING something from a function should be managed as a Payload!! * #

def region_string_to_int(region_string): # converts an '(x, y)' string to a tuple (x, y)
    splitforms = region_string.split(',')
    nospaces = [x.replace(' ', '') for x in splitforms]
    noparens = [x.replace('(', '') for x in nospaces]
    noparens2 = [x.replace(')', '') for x in noparens]
    asints = [int(x) for x in noparens2]
    return (asints[0], asints[1])

def entity_display_to_id(entity_display): # converts an entity's display name to its internal ID
    # * entity display will be in the form "Owners's Entity | "
    # * we need it to be in the form OWNERentity
    # first, we strip it into two words
    owner, entity = entity_display.split()
    # for owner, we remove the 's and uppercase it
    owner = owner[:-2].upper()
    # for entity, we just lowercase it
    entity = entity.lower()
    # then for the return we just combine the two
    return owner + entity

@bot.command() # ! this is the one exception to payloads due to... weirdness. maybe rewrite later ! #
async def register_player(ctx, player_name):
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
    #if both of those are math, initialize a Player object
    Player(uid, player_name)
    await ctx.send(f'Player {player_name} created with UID {uid}')
    return

@bot.command()
async def scan_region(ctx, target_xy):
    Regions = get_file('Regions.pickle')
    target_region = Regions[region_string_to_int(target_xy)] # translate coords to actual region
    result = target_region.scan()
    output = payload_manage(result)
    await ctx.send(output)

@bot.command()
async def inspect(ctx, entity_display_string, target_xy):
    # first, we get the region python_object we want
    Regions = get_file('Regions.pickle')
    target_region = Regions[region_string_to_int(target_xy)]
    # then we get the target entity's internal ID
    target_entity_id = entity_display_to_id(entity_display_string)
    # then we get the actual object we want
    inspect_target = target_region.content[target_entity_id]
    # inspect it and send the result to payload manager
    output = payload_manage(inspect_target.inspect())
    await ctx.send(output)
     
bot.run(TOKEN)