import os
import asyncio
import discord
from discord.ext import commands

class SecurityBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"[LOADED COG] {filename}")
                except Exception as e:
                    print(f"[ERROR LOADING COG] {filename}: {e}")
        
        try:
            synced = await self.tree.sync()
            print(f"[SYNCED] Successfully synced {len(synced)} slash command(s).")
        except Exception as e:
            print(f"[ERROR SYNCING] {e}")

    async def on_ready(self):
        print(f"[ONLINE] Logged in as {self.user} (ID: {self.user.id})")

bot = SecurityBot()

token = os.getenv("DISCORD_TOKEN")
if token:
    token = token.strip().strip('"').strip("'")
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("[CRITICAL ERROR] Invalid Discord Bot Token provided!")
    except Exception as e:
        print(f"[CRITICAL ERROR] Failed to run bot: {e}")
else:
    print("[ERROR] DISCORD_TOKEN environment variable is missing!")