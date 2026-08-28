# My Discord Bot

Commands:
- `!ping`
- `!hello`

Railway:
1. Add environment variable `TOKEN`
2. Put your Discord bot token as the value
3. Start command: `python main.py`
import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("TOKEN variable is missing!")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}! 👋")


bot.run(TOKEN)
discord.py
worker: python main.py


