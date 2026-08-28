import os
import asyncio
import signal
import sys
import discord
from discord.ext import commands

# 1. Go কোডের মতো অটোমেটিক শার্ডিং সেটআপ (Bot/AutoShardedBot)
# এটি ডিসকর্ড এপিআই থেকে সার্ভার সংখ্যা অনুযায়ী শার্ড সংখ্যা নিজে হিসাব করবে
class SummrsPremiumBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # ব্যাকগ্রাউন্ড টাস্ক বা এপিআই কানেকশন
        print("[INFO] Bot is initializing shard sessions...")

    async def on_ready(self):
        print(f"[SUCCESS] Logged in as {self.user} (ID: {self.user.id})")
        print(f"[INFO] Active Shard Count: {self.shard_count}")
        print(f"[INFO] Connected to {len(self.guilds)} guilds across all shards.")

bot = SummrsPremiumBot()

# 2. কোড বন্ধ হওয়ার সংকেত (Graceful Shutdown) হ্যান্ডেল করা
def handle_exit_signals():
    print("\n[INFO] Stopping bot gracefully...")
    asyncio.create_task(bot.close())

# 3. মূল এক্সিকিউশন
if __name__ == "__main__":
    # Railway Environment Variable থেকে টোকেন গ্রহণ (Go কোডের ম্যানুয়াল Scan-এর বিকল্প)
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        print("[ERROR] DISCORD_TOKEN is missing in Railway Variables!")
        sys.exit(1)

    try:
        # বট রান করা
        bot.run(token)
    except discord.errors.LoginFailure:
        print("[ERROR] Invalid Token Provided!")
    except Exception as e:
        print(f"[CRITICAL ERROR]: {e}")