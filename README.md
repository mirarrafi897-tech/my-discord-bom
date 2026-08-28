# my-discord-bom
import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("TOKEN environment variable is missing.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}! 👋")

bot.run(TOKEN)
discord.py>=2.6,<3
__pycache__/
*.pyc
.env
# My Discord Bot

Commands:
- `!ping`
- `!hello`

Railway:
1. Add environment variable `TOKEN`
2. Put your Discord bot token as the value
3. Start command: `python main.py`
4. 
