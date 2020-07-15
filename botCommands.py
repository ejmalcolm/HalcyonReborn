import discord

token = 'NzMzMDUzNTkzMjU4ODE5NjY1.Xw9sVw.HTP3zs2cb-Kbs3Ma9XMHggsCuX0'

client = discord.Client()

@client.event
async def on_ready():
    print('Bot client has logged in.')

@bot.command()
async def inspect(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(token)