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
        # cogs ফোল্ডারের ফাইলগুলো অটো-লোড করবে
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"[LOADED COG] {filename}")
        
        # স্লাশ কমান্ড ডিসকর্ডে সিঙ্ক করার জন্য
        try:
            synced = await self.tree.sync()
            print(f"[SYNCED] Successfully synced {len(synced)} slash command(s).")
        except Exception as e:
            print(f"[ERROR] Failed to sync slash commands: {e}")

    async def on_ready(self):
        print(f"[ONLINE] Logged in as {self.user} (ID: {self.user.id})")
        print(f"[SHARDS] Active Shard Count: {self.shard_count}")

bot = SecurityBot()

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("[ERROR] DISCORD_TOKEN is missing!")