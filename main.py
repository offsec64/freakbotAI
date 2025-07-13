# Import Modules
import discord
from discord.ext import commands
import requests

# Set the bot's prefix
bot = commands.Bot(command_prefix='!')


# First Command
@bot.command()
# Whatever you want the command to be, put that in for COMMAND_NAME (one word).
async def COMMAND_NAME(ctx):
  # Trigger the IFTTT applet. Put your key in YOUR_KEY.
  requests.post('https://maker.ifttt.com/trigger/fan/with/key/YOUR_KEY')
  # Put a message in the console. Replace CONSOLE OUTPUT with what you want.
  print('CONSOLE OUTPUT')
  # Send a message back to discord. Put the message you want for MESSAGE TO SEND.
  await ctx.send('MESSAGE TO SEND')


# Another Command
@bot.command()
# Whatever you want the command to be, put that in for COMMAND_NAME (one word).
async def COMMAND_NAME(ctx):
  # Trigger the IFTTT applet. Put your key in YOUR_KEY.
  requests.post('https://maker.ifttt.com/trigger/fan/with/key/YOUR_KEY')
  # Put a message in the console. Replace CONSOLE OUTPUT with what you want.
  print('CONSOLE OUTPUT')
  # Send a message back to discord. Put the message you want for MESSAGE TO SEND.
  await ctx.send('MESSAGE TO SEND')

# Put your token for YOUR_TOKEN
bot.run('YOUR_TOKEN')