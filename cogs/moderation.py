import discord
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- BAN & KICK COMMANDS ---

    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ You cannot ban this user due to role hierarchy!", ephemeral=True)
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"**User:** {member.mention} (`{member.id}`)\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
            color=0xff4747
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unban", description="Unban a user by ID")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: str, *, reason: str = "No reason provided"):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await ctx.guild.unban(user, reason=reason)
            embed = discord.Embed(
                title="🔓 Member Unbanned",
                description=f"**User:** {user.name} (`{user.id}`)\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
                color=0x43b581
            )
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("❌ User not found or not banned!", ephemeral=True)

    @commands.hybrid_command(name="kick", description="Kick a member from the server")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ You cannot kick this user due to role hierarchy!", ephemeral=True)
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Member Kicked",
            description=f"**User:** {member.mention} (`{member.id}`)\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="softban", description="Ban and immediately unban to clear recent messages")
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Softban (Clear messages)"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Hierarchy error!", ephemeral=True)
        await member.ban(reason=reason, delete_message_days=1)
        await ctx.guild.unban(member, reason="Softban unban")
        embed = discord.Embed(
            title="🧹 Member Softbanned",
            description=f"**User:** {member.mention}\n**Reason:** {reason}",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

    # --- TIMEOUT / MUTE ---

    @commands.hybrid_command(name="timeout", description="Timeout/Mute a member (minutes)")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Cannot timeout this user!", ephemeral=True)
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title="⏱️ Member Timed Out",
            description=f"**User:** {member.mention}\n**Duration:** `{minutes}m`\n**Reason:** {reason}",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="untimeout", description="Remove timeout from a member")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx: commands.Context, member: discord.Member):
        await member.timeout(None)
        embed = discord.Embed(
            title="🔊 Timeout Removed",
            description=f"**User:** {member.mention} can now talk.",
            color=0x43b581
        )
        await ctx.send(embed=embed)

    # --- CHANNEL MANAGEMENT ---

    @commands.hybrid_command(name="purge", description="Bulk delete messages from channel")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int = 10):
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            description=f"🧹 Deleted `{len(deleted)-1}` messages.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed, delete_after=5)

    @commands.hybrid_command(name="lock", description="Lock current channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(title="🔒 Channel Locked", description="Members cannot send messages here.", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unlock", description="Unlock current channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(title="🔓 Channel Unlocked", description="Channel is open for messaging.", color=0x43b581)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="hide", description="Hide current channel from @everyone")
    @commands.has_permissions(manage_channels=True)
    async def hide(self, ctx: commands.Context):
        await ctx.channel.set_permissions(ctx.guild.default_role, read_messages=False)
        embed = discord.Embed(title="👁️‍🗨️ Channel Hidden", color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unhide", description="Make channel visible again")
    @commands.has_permissions(manage_channels=True)
    async def unhide(self, ctx: commands.Context):
        await ctx.channel.set_permissions(ctx.guild.default_role, read_messages=True)
        embed = discord.Embed(title="👁️ Channel Unhidden", color=0x43b581)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="slowmode", description="Set channel slowmode in seconds")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        embed = discord.Embed(
            description=f"⏱️ Slowmode set to `{seconds}` seconds.",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="setnick", description="Change a member's nickname")
    @commands.has_permissions(manage_nicknames=True)
    async def setnick(self, ctx: commands.Context, member: discord.Member, *, nick: str = None):
        await member.edit(nick=nick)
        embed = discord.Embed(
            description=f"📝 Nickname for {member.mention} changed to `{nick or 'Reset'}`",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="warn", description="Issue an official warning to a member")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=f"**User:** {member.mention}\n**Warned By:** {ctx.author.mention}\n**Reason:** {reason}",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))