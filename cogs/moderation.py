import discord
from discord.ext import commands
import datetime
from collections import defaultdict

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = defaultdict(list) # {user_id: [reasons]}

    # =====================================================================
    # 1. CHANNEL LOCK & UNLOCK COMMANDS
    # =====================================================================

    @commands.hybrid_command(name="lock", description="Lock the current text channel against @everyone")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        overwrite = target_channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False

        try:
            await target_channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"Successfully locked {target_channel.mention}. Regular members can no longer send messages.",
                color=0xe74c3c
            )
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to lock channel: {e}", ephemeral=True)

    @commands.hybrid_command(name="unlock", description="Unlock the current text channel for @everyone")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        overwrite = target_channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True

        try:
            await target_channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description=f"Successfully unlocked {target_channel.mention}. Regular members can now send messages.",
                color=0x2ecc71
            )
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to unlock channel: {e}", ephemeral=True)

    # =====================================================================
    # 2. VOICE CHANNEL LOCK, UNLOCK & MUTE ALL COMMANDS
    # =====================================================================

    @commands.hybrid_command(name="lockvc", description="Lock your current voice channel")
    @commands.has_permissions(manage_channels=True)
    async def lockvc(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You must be connected to a voice channel to use this command!", ephemeral=True)

        vc = ctx.author.voice.channel
        overwrite = vc.overwrites_for(ctx.guild.default_role)
        overwrite.connect = False

        try:
            await vc.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(
                title="🔒 Voice Channel Locked",
                description=f"Successfully locked **{vc.name}**. No new members can join.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to lock voice channel: {e}", ephemeral=True)

    @commands.hybrid_command(name="unlockvc", description="Unlock your current voice channel")
    @commands.has_permissions(manage_channels=True)
    async def unlockvc(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You must be connected to a voice channel to use this command!", ephemeral=True)

        vc = ctx.author.voice.channel
        overwrite = vc.overwrites_for(ctx.guild.default_role)
        overwrite.connect = True

        try:
            await vc.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(
                title="🔓 Voice Channel Unlocked",
                description=f"Successfully unlocked **{vc.name}**. Members can now join freely.",
                color=0x2ecc71
            )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to unlock voice channel: {e}", ephemeral=True)

    @commands.hybrid_command(name="muteall", description="Server-mute all members in your voice channel")
    @commands.has_permissions(mute_members=True)
    async def muteall(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You must be in a voice channel to mute everyone!", ephemeral=True)

        vc = ctx.author.voice.channel
        count = 0
        for member in vc.members:
            if member.id != ctx.author.id and not member.bot:
                try:
                    await member.edit(mute=True, reason=f"Muteall executed by {ctx.author}")
                    count += 1
                except Exception:
                    pass

        embed = discord.Embed(
            title="🔇 Voice Channel Muted",
            description=f"Successfully server-muted **{count}** members in **{vc.name}**.",
            color=0xf39c12
        )
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="unmuteall", description="Server-unmute all members in your voice channel")
    @commands.has_permissions(mute_members=True)
    async def unmuteall(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You must be in a voice channel to unmute everyone!", ephemeral=True)

        vc = ctx.author.voice.channel
        count = 0
        for member in vc.members:
            if member.id != ctx.author.id and not member.bot:
                try:
                    await member.edit(mute=False, reason=f"Unmuteall executed by {ctx.author}")
                    count += 1
                except Exception:
                    pass

        embed = discord.Embed(
            title="🔊 Voice Channel Unmuted",
            description=f"Successfully server-unmuted **{count}** members in **{vc.name}**.",
            color=0x2ecc71
        )
        await ctx.send(embed=embed, ephemeral=True)

    # =====================================================================
    # 3. MEMBER PUNISHMENT COMMANDS (Kick, Ban, Timeout, Purge)
    # =====================================================================

    @commands.hybrid_command(name="kick", description="Kick a member from the server")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ You cannot kick this member due to role hierarchy.", ephemeral=True)

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**User:** {member.mention}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
                color=0xe67e22
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to kick member: {e}", ephemeral=True)

    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ You cannot ban this member due to role hierarchy.", ephemeral=True)

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**User:** {member.mention}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to ban member: {e}", ephemeral=True)

    @commands.hybrid_command(name="timeout", description="Timeout a member for a specified duration in minutes")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ You cannot timeout this member due to role hierarchy.", ephemeral=True)

        duration = datetime.timedelta(minutes=minutes)
        try:
            await member.timeout(duration, reason=reason)
            embed = discord.Embed(
                title="⏳ Member Timed Out",
                description=f"**User:** {member.mention}\n**Duration:** `{minutes} minutes`\n**Reason:** {reason}",
                color=0xf1c40f
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to timeout member: {e}", ephemeral=True)

    @commands.hybrid_command(name="purge", description="Bulk delete messages in a channel")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Please specify an amount greater than 0.", ephemeral=True)

        try:
            deleted = await ctx.channel.purge(limit=amount + 1) # +1 to include command invocation message
            msg = await ctx.send(f"🗑️ Successfully deleted **{len(deleted) - 1}** messages.")
            await discord.utils.sleep_until(datetime.datetime.utcnow() + datetime.timedelta(seconds=4))
            await msg.delete()
        except Exception as e:
            await ctx.send(f"❌ Failed to purge messages: {e}", ephemeral=True)

    # =====================================================================
    # 4. ADVANCED WARNING SYSTEM (Warn, Warnings, Clear, Remove)
    # =====================================================================

    @commands.hybrid_command(name="warn", description="Issue a warning to a member")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        self.warnings[member.id].append(reason)
        warn_count = len(self.warnings[member.id])

        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=f"**User:** {member.mention}\n**Reason:** {reason}\n**Total Warnings:** `{warn_count}`",
            color=0xf39c12
        )
        await ctx.send(embed=embed)

        # Auto-punishment if warnings reach 3
        if warn_count >= 3:
            try:
                await member.timeout(datetime.timedelta(hours=1), reason="[AUTO-MOD] Reached 3 cumulative warnings.")
                await ctx.send(f"🚨 {member.mention} has reached **3 warnings** and has been automatically timed out for 1 hour!")
            except Exception:
                pass

    @commands.hybrid_command(name="warnings", description="Check active warnings for a member")
    async def warnings(self, ctx: commands.Context, member: discord.Member):
        user_warns = self.warnings.get(member.id, [])
        if not user_warns:
            return await ctx.send(f"✅ {member.mention} has no active warnings.")

        reasons = "\n".join([f"`#{i+1}` {r}" for i, r in enumerate(user_warns)])
        embed = discord.Embed(
            title=f"⚠️ Warnings for {member.name}",
            description=reasons,
            color=0x3498db
        )
        embed.set_footer(text=f"Total Warnings: {len(user_warns)}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="clearwarns", description="Clear all warnings for a member")
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx: commands.Context, member: discord.Member):
        if member.id in self.warnings:
            self.warnings.pop(member.id)
            await ctx.send(f"✅ Successfully cleared all warnings for {member.mention}.")
        else:
            await ctx.send(f"❌ {member.mention} has no warnings to clear.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))