import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency is `{latency}ms`")

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🛡️ Security & Moderation Bot",
            description=f"Hey {ctx.author.mention}, here are the available command categories:",
            color=0x2b2d31
        )
        embed.add_field(
            name="🔒 Security",
            value="`unwhitelist`, `whitelist`",
            inline=False
        )
        embed.add_field(
            name="🛠️ Moderation",
            value="`ban`, `kick`, `lock`, `unlock`",
            inline=False
        )
        embed.add_field(
            name="👑 Roles",
            value="`staff`, `buddy`, `qt`",
            inline=False
        )
        embed.set_footer(text=f"{ctx.guild.name} Security System")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))