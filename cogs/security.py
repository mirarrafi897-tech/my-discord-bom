import discord
from discord.ext import commands

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ইন-মেমোরি ডাটাবেজ (প্রয়োজনে ডাটাবেজে রূপান্তরযোগ্য)
        self.whitelist = set()
        self.extra_owners = set()
        self.antinuke_enabled = True

    # --- SECURITY CONTROLS ---

    @commands.hybrid_command(name="antinuke", description="Turn antinuke system ON or OFF")
    @commands.has_permissions(administrator=True)
    async def antinuke(self, ctx: commands.Context, status: str):
        status = status.lower()
        if status in ["on", "enable", "true"]:
            self.antinuke_enabled = True
            embed = discord.Embed(
                title="🛡️ Antinuke Protection",
                description="Antinuke system has been **ENABLED** 🟢\nYour server is now shielded from unauthorized actions.",
                color=0x43b581
            )
        elif status in ["off", "disable", "false"]:
            self.antinuke_enabled = False
            embed = discord.Embed(
                title="⚠️ Antinuke Protection",
                description="Antinuke system has been **DISABLED** 🔴\nServer protection features are currently paused.",
                color=0xff4747
            )
        else:
            embed = discord.Embed(
                description="❌ Invalid status! Use `on` or `off`.",
                color=0xff4747
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="whitelist", description="Add a user to the security whitelist")
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx: commands.Context, user: discord.User):
        self.whitelist.add(user.id)
        embed = discord.Embed(
            title="✅ User Whitelisted",
            description=f"{user.mention} (`{user.id}`) has been added to the trusted whitelist.",
            color=0x43b581
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unwhitelist", description="Remove a user from the security whitelist")
    @commands.has_permissions(administrator=True)
    async def unwhitelist(self, ctx: commands.Context, user: discord.User):
        if user.id in self.whitelist:
            self.whitelist.remove(user.id)
            embed = discord.Embed(
                title="❌ Whitelist Removed",
                description=f"{user.mention} (`{user.id}`) was removed from the whitelist.",
                color=0xff4747
            )
        else:
            embed = discord.Embed(description="❌ User is not in the whitelist!", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="whitelisted", description="View all whitelisted users")
    async def whitelisted(self, ctx: commands.Context):
        if not self.whitelist:
            embed = discord.Embed(title="📜 Whitelisted Users", description="No users are currently whitelisted.", color=0x2b2d31)
        else:
            users = [f"<@{uid}> (`{uid}`)" for uid in self.whitelist]
            embed = discord.Embed(
                title="📜 Whitelisted Users",
                description="\n".join(users),
                color=0x2b2d31
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="extraowner", description="Grant Extra Owner privileges to a trusted user")
    async def extraowner(self, ctx: commands.Context, user: discord.User):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Only the Server Owner can use this command!", ephemeral=True)
        
        self.extra_owners.add(user.id)
        embed = discord.Embed(
            title="👑 Extra Owner Granted",
            description=f"{user.mention} (`{user.id}`) is now set as an Extra Owner.",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverlockdown", description="Lock down all text channels in emergency")
    @commands.has_permissions(administrator=True)
    async def serverlockdown(self, ctx: commands.Context):
        await ctx.send("🚨 **Initiating Full Server Lockdown...**")
        count = 0
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                count += 1
            except Exception:
                continue
        
        embed = discord.Embed(
            title="🔒 Server Lockdown Complete",
            description=f"Successfully locked down `{count}` text channels.",
            color=0xff4747
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverunlock", description="Unlock all text channels after a lockdown")
    @commands.has_permissions(administrator=True)
    async def serverunlock(self, ctx: commands.Context):
        await ctx.send("🔓 **Unlocking Server Channels...**")
        count = 0
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                count += 1
            except Exception:
                continue

        embed = discord.Embed(
            title="🔓 Server Unlock Complete",
            description=f"Successfully restored message permissions in `{count}` text channels.",
            color=0x43b581
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Security(bot))