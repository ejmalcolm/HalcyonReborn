import discord
from discord.ext import commands
from config import TOKEN

client = discord.Client()
bot = commands.Bot(command_prefix='~')

# * all commands should be primarily managed through the Player object's methods * #

@bot.command()
async def inspect_region(ctx, region_xy):
    uid = ctx.message.author.id
    await ctx.send(str(uid) + str(region_xy))

bot.run(TOKEN)