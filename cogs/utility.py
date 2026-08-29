import discord
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !ping এবং /ping দুটিই কাজ করবে
    @commands.hybrid_command(name="ping", description="Check the bot latency")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency is `{latency}ms`")

    # !help এবং /help দুটিই কাজ করবে
    @commands.hybrid_command(name="help", description="Show all security & moderation commands")
    async def help_command(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🛡️ Security & Moderation Dashboard",
            description=f"Hey {ctx.author.mention}, here are the available command categories:",
            color=0x2b2d31
        )
        embed.add_field(
            name="🔒 Security",
            value="`/unwhitelist` - Unwhitelist user from all security events",
            inline=False
        )
        embed.add_field(
            name="🛠️ Moderation",
            value="`/ban`, `/kick`, `/lock`, `/unlock`",
            inline=False
        )
        embed.add_field(
            name="👑 Roles",
            value="`/staff`, `/buddy`, `/qt`",
            inline=False
        )
        embed.set_footer(text=f"{ctx.guild.name} Security System")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))