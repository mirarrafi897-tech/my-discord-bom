import os
import discord
from discord.ext import commands
from cogs.advanced import TicketSetupView, ReactionRoleView
from cogs.vc_manager import VCSetupView, VCControlView

class SecurityBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Persistent Views রেজিস্টার করা হলো যাতে বোট রিস্টার্টের পরেও বাটন কাজ করে
        self.add_view(TicketSetupView())
        self.add_view(ReactionRoleView())
        self.add_view(VCSetupView())
        self.add_view(VCControlView(self))

        # Cogs লোড করা
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"[LOADED COG] {filename}")
                except Exception as e:
                    print(f"[ERROR COG] {filename}: {e}")

        # গ্লোবাল স্লাশ কমান্ড সিঙ্ক (Public Bot-এর জন্য)
        try:
            synced = await self.tree.sync()
            print(f"[GLOBAL SYNC SUCCESS] {len(synced)} slash commands synced globally!")
        except Exception as e:
            print(f"[SYNC ERROR] {e}")

    async def on_ready(self, *args, **kwargs):
        print(f"[ONLINE] Logged in as {self.user} (ID: {self.user.id})")

bot = SecurityBot()

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token.strip().strip('"').strip("'"))
else:
    print("[ERROR] DISCORD_TOKEN is missing!")