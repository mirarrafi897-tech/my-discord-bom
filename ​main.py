import os
import discord
from discord.ext import commands
from cogs.advanced import TicketSetupView, ReactionRoleView
from cogs.vc_manager import VCSetupView, VCControlView

class RoyalSecurityBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Register persistent UI views globally to prevent interaction timeouts after restart
        self.add_view(TicketSetupView())
        self.add_view(ReactionRoleView())
        self.add_view(VCSetupView())
        self.add_view(VCControlView(self))

        # Dynamically load all cogs from the /cogs directory
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f'cogs.{cog_name}')
                    print(f"[ROYAL COG LOADED] Successfully initialized: {cog_name.upper()}")
                except Exception as e:
                    print(f"[ERROR COG LOADED] Failed to initialize {cog_name}: {e}")

        # Sync global application/slash commands
        try:
            synced = await self.tree.sync()
            print(f"[ROYAL SYNC SUCCESS] Total {len(synced)} commands synchronized globally.")
        except Exception as e:
            print(f"[SYNC ERROR] {e}")

    async def on_ready(self):
        print(f"==================================================")
        print(f"[ONLINE] Logged in as: {self.user.name} (ID: {self.user.id})")
        print(f"[STATUS] Royal All-in-One Engine is fully operational.")
        print(f"==================================================")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="over Royal Servers | /help"
            ),
            status=discord.Status.online
        )

bot = RoyalSecurityBot()

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token.strip().strip('"').strip("'"))
else:
    print("[CRITICAL ERROR] DISCORD_TOKEN environment variable is missing!")