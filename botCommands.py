import discord
from discord.ext import commands

from config import TOKEN
from files import get_file, save_file
from botInterface import Payload, payload_manage

from players import Player
from regions import Region

client = discord.Client()
bot = commands.Bot(command_prefix='~')

# * any command that involves RETURNING something from a function should be managed as a Payload!! * #

def region_string_to_int(region_string):
    splitforms = region_string.split(',')
    nospaces = [x.replace(' ', '') for x in splitforms]
    noparens = [x.replace('(', '') for x in nospaces]
    noparens2 = [x.replace(')', '') for x in noparens]
    asints = [int(x) for x in noparens2]
    return (asints[0], asints[1])

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

bot.run(TOKEN)