import os
import asyncio
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# Initialize Flask web server for uptime monitoring
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active and running smoothly!", 200

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Bot Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Security Core is fully operational.")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="over servers | /antinuke")
    )

# Fixed: Removed 'async' from class definition
class BotMain:
    @staticmethod
    async def main():
        keep_alive()
        async with bot:
            # Load cogs
            if os.path.exists('./cogs'):
                for filename in os.listdir('./cogs'):
                    if filename.endswith('.py'):
                        cog_name = filename[:-3]
                        try:
                            await bot.load_extension(f'cogs.{cog_name}')
                            print(f"Loaded extension: {cog_name}")
                        except Exception as e:
                            print(f"Failed to load extension {cog_name}: {e}")

            # Sync application commands globally
            try:
                synced = await bot.tree.sync()
                print(f"Synced {len(synced)} slash commands globally.")
            except Exception as e:
                print(f"Command sync failed: {e}")

            token = os.getenv("DISCORD_TOKEN")
            if not token:
                print("CRITICAL ERROR: DISCORD_TOKEN environment variable is missing!")
                return
            await bot.start(token.strip().strip('"').strip("'"))

if __name__ == "__main__":
    asyncio.run(BotMain.main())