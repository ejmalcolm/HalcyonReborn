import discord
from discord.ext import commands
from config import TOKEN
from players import Player
from files import get_file, save_file
from botInterface import Payload

client = discord.Client()
bot = commands.Bot(command_prefix='~')

# * all commands should be primarily managed through the Player object's methods * #

def payload_manage(pload): # used for any function that 
    return pload.messages[0]

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

bot.run(TOKEN)