import discord
from discord.ext import commands
import datetime
from collections import defaultdict, deque

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Configuration & State Toggles
        self.antinuke_enabled = True
        self.automod_enabled = True
        self.antibot_enabled = True
        
        # Whitelist Storage (Set of User IDs)
        self.whitelisted_users = set()
        
        # Rate Limiting Trackers (Action tracking dictionaries for anti-nuke)
        self.ban_tracker = defaultdict(deque)
        self.kick_tracker = defaultdict(deque)
        self.channel_tracker = defaultdict(deque)

    # =====================================================================
    # 1. WHITELIST MANAGEMENT SYSTEM (Add / Remove / List)
    # =====================================================================

    @commands.hybrid_group(name="whitelist", description="Manage trusted users for anti-nuke protection")
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🛡️ Royal Security Whitelist Menu",
                description="Please use subcommands to manage your trusted administrators:\n\n"
                            "• `/whitelist add @user` - Add user to whitelist\n"
                            "• `/whitelist remove @user` - Remove user from whitelist\n"
                            "• `/whitelist list` - View all whitelisted users",
                color=0x3498db
            )
            embed.set_footer(text=f"{ctx.guild.name} • Security Core")
            await ctx.send(embed=embed)

    @whitelist.command(name="add", description="Add a trusted user to the security whitelist")
    @commands.has_permissions(administrator=True)
    async def whitelist_add(self, ctx: commands.Context, member: discord.Member):
        if member.id in self.whitelisted_users:
            embed = discord.Embed(
                title="⚠️ Already Whitelisted",
                description=f"**{member.mention}** is already present in the security whitelist.",
                color=0xf39c12
            )
            return await ctx.send(embed=embed)

        self.whitelisted_users.add(member.id)
        embed = discord.Embed(
            title="🛡️ Whitelist Updated",
            description=f"Successfully added **{member.mention}** to the security whitelist. They are now immune to anti-nuke actions.",
            color=0x2ecc71
        )
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

    @whitelist.command(name="remove", description="Remove a user from the security whitelist")
    @commands.has_permissions(administrator=True)
    async def whitelist_remove(self, ctx: commands.Context, member: discord.Member):
        if member.id not in self.whitelisted_users:
            embed = discord.Embed(
                title="⚠️ Not Found",
                description=f"**{member.mention}** is not in the security whitelist.",
                color=0xe74c3c
            )
            return await ctx.send(embed=embed)

        self.whitelisted_users.remove(member.id)
        embed = discord.Embed(
            title="🛡️ Whitelist Updated",
            description=f"Successfully removed **{member.mention}** from the security whitelist.",
            color=0xe74c3c
        )
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

    @whitelist.command(name="list", description="List all currently whitelisted users")
    @commands.has_permissions(administrator=True)
    async def whitelist_list(self, ctx: commands.Context):
        if not self.whitelisted_users:
            embed = discord.Embed(
                title="🛡️ Security Whitelist",
                description="The whitelist is currently empty.",
                color=0x95a5a6
            )
            return await ctx.send(embed=embed)

        mentions = [f"<@{uid}> (`{uid}`)" for uid in self.whitelisted_users]
        embed = discord.Embed(
            title="🛡️ Current Whitelisted Users",
            description="\n".join(mentions),
            color=0x3498db
        )
        embed.set_footer(text=f"Total Whitelisted: {len(self.whitelisted_users)}")
        await ctx.send(embed=embed)

    # =====================================================================
    # 2. SECURITY TOGGLE CONTROLS (Enable / Disable)
    # =====================================================================

    @commands.hybrid_command(name="antinuke", description="Enable or disable the anti-nuke protection system")
    @commands.has_permissions(administrator=True)
    async def antinuke(self, ctx: commands.Context, status: str):
        status = status.lower()
        if status == "enable":
            self.antinuke_enabled = True
            embed = discord.Embed(title="🟢 Anti-Nuke Status", description="Anti-nuke protection has been **ENABLED**.", color=0x2ecc71)
        elif status == "disable":
            self.antinuke_enabled = False
            embed = discord.Embed(title="🔴 Anti-Nuke Status", description="Anti-nuke protection has been **DISABLED**.", color=0xe74c3c)
        else:
            embed = discord.Embed(title="❌ Invalid Argument", description="Please use `/antinuke enable` or `/antinuke disable`.", color=0xe74c3c)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="automod", description="Enable or disable automod link and spam protection")
    @commands.has_permissions(administrator=True)
    async def automod(self, ctx: commands.Context, status: str):
        status = status.lower()
        if status == "enable":
            self.automod_enabled = True
            embed = discord.Embed(title="🟢 AutoMod Status", description="Link & spam automod has been **ENABLED**.", color=0x2ecc71)
        elif status == "disable":
            self.automod_enabled = False
            embed = discord.Embed(title="🔴 AutoMod Status", description="Link & spam automod has been **DISABLED**.", color=0xe74c3c)
        else:
            embed = discord.Embed(title="❌ Invalid Argument", description="Please use `/automod enable` or `/automod disable`.", color=0xe74c3c)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="antibot", description="Enable or disable unauthorized bot integration protection")
    @commands.has_permissions(administrator=True)
    async def antibot(self, ctx: commands.Context, status: str):
        status = status.lower()
        if status == "enable":
            self.antibot_enabled = True
            embed = discord.Embed(title="🟢 Anti-Bot Status", description="Anti-bot guard has been **ENABLED**.", color=0x2ecc71)
        elif status == "disable":
            self.antibot_enabled = False
            embed = discord.Embed(title="🔴 Anti-Bot Status", description="Anti-bot guard has been **DISABLED**.", color=0xe74c3c)
        else:
            embed = discord.Embed(title="❌ Invalid Argument", description="Please use `/antibot enable` or `/antibot disable`.", color=0xe74c3c)
        await ctx.send(embed=embed)

    # =====================================================================
    # 3. SECURITY EVENT LISTENERS (Anti-Nuke, Anti-Bot, AutoMod)
    # =====================================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if self.antibot_enabled and member.bot:
            # Check if bot was added by a whitelisted user or server owner
            guild = member.guild
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                if entry.target.id == member.id:
                    actor = entry.user
                    if actor.id != guild.owner.id and actor.id not in self.whitelisted_users:
                        try:
                            await guild.kick(member, reason="[ANTI-BOT] Unauthorized bot added by non-whitelisted user.")
                            await guild.ban(actor, reason="[ANTI-NUKER] Bypassed security by adding unauthorized bot.")
                            
                            log_channel = discord.utils.get(guild.text_channels, name="security-logs")
                            if log_channel:
                                embed = discord.Embed(
                                    title="🚨 SECURITY BREACH BLOCKED (Anti-Bot)",
                                    description=f"**Unauthorized Bot:** {member.mention}\n**Added By:** {actor.mention} (Banned)\n**Action:** Bot kicked and culprit permanently banned.",
                                    color=0xe74c3c
                                    )
                                await log_channel.send(embed=embed)
                        except Exception:
                            pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not self.antinuke_enabled:
            return
        
        guild = channel.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            actor = entry.user
            if actor.id == guild.owner.id or actor.id == self.bot.user.id or actor.id in self.whitelisted_users:
                return

            now = datetime.datetime.utcnow()
            self.channel_tracker[actor.id].append(now)
            
            # Clean up old timestamps older than 10 seconds
            while self.channel_tracker[actor.id] and (now - self.channel_tracker[actor.id][0]).total_seconds() > 10:
                self.channel_tracker[actor.id].popleft()

            # If user deletes more than 3 channels within 10 seconds -> Punish
            if len(self.channel_tracker[actor.id]) > 3:
                try:
                    await guild.ban(actor, reason="[ANTI-NUKE] Mass channel deletion detected.")
                    log_channel = discord.utils.get(guild.text_channels, name="security-logs")
                    if log_channel:
                        embed = discord.Embed(
                            title="🚨 ANTI-NUKE TRIGGERED",
                            description=f"**Culprit:** {actor.mention}\n**Violation:** Mass Channel Deletion\n**Action:** User banned instantly.",
                            color=0xe74c3c
                        )
                        await log_channel.send(embed=embed)
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild or not self.automod_enabled:
            return

        # Simple AutoMod link and invitation blocker
        content = message.content.lower()
        if "discord.gg/" in content or "https://" in content or "http://" in content:
            # Check if user has administrative or manage messages permissions
            if message.author.guild_permissions.manage_messages:
                return

            try:
                await message.delete()
                warning_msg = await message.channel.send(f"⚠️ {message.author.mention}, links and server invitations are restricted by server AutoMod!")
                await discord.utils.sleep_until(datetime.datetime.utcnow() + datetime.timedelta(seconds=5))
                await warning_msg.delete()
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(Security(bot))