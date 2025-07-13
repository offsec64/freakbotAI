import discord
from discord.ext import commands
import requests

bot = commands.Bot(command_prefix='!')


@bot.command()
async def COMMAND_NAME(ctx):
  await ctx.send('MESSAGE TO SEND')


@bot.command()
async def COMMAND_NAME(ctx):
  await ctx.send('MESSAGE TO SEND')

bot.run('YOUR_TOKEN')