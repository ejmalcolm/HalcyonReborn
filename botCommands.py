import discord
from discord.ext import commands
from config import TOKEN

client = discord.Client()
bot = commands.Bot(command_prefix='~')

@client.event
async def on_ready():
    print('Bot client has logged in.')

# * all commands should be primarily managed through the Player object's methods * #

@bot.command()
async def display_region(ctx, region_xy):
    uid = ctx.message.author.id
    ctx.send(uid)

bot.run(TOKEN)