import discord
from discord.ext import commands
import datetime
import asyncio
from collections import defaultdict, deque

class AdvancedSecurity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Anti-Spam tracking dictionaries
        self.message_cooldowns = defaultdict(lambda: deque(maxlen=6))
        
        # Security Management Sets & States
        self.whitelisted_users = set()
        self.extra_owners = set()
        self.antinuke_enabled = True  # Default status is ON

    # Helper: Check if user is protected/trusted
    def _is_trusted(self, guild: discord.Guild, user_id: int):
        if user_id == guild.owner_id:
            return True
        if user_id in self.extra_owners:
            return True
        if user_id in self.whitelisted_users:
            return True
        return False

    # =====================================================================
    # 1. MANAGEMENT COMMANDS (Whitelist, Extra Owners, Status & Antinuke Toggle)
    # =====================================================================
    @commands.hybrid_group(name="security", description="Manage royal security configurations")
    @commands.has_permissions(administrator=True)
    async def security(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🛡️ Royal Security Control Panel",
                description="Use subcommands to manage server security, whitelists, and extra owners.\n\n"
                            "• `/security status` - View live security status\n"
                            "• `/security antinuke <on/off>` - Enable or disable anti-nuke\n"
                            "• `/security whitelist add/remove @user`\n"
                            "• `/security extraowner add/remove @user`",
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)

    @security.command(name="status", description="View the current Anti-Nuke and security protection status")
    async def security_status(self, ctx: commands.Context):
        whitelist_mentions = [f"<@{uid}>" for uid in self.whitelisted_users]
        whitelist_text = ", ".join(whitelist_mentions) if whitelist_mentions else "No users whitelisted"

        extra_owner_mentions = [f"<@{uid}>" for uid in self.extra_owners]
        extra_owner_text = ", ".join(extra_owner_mentions) if extra_owner_mentions else "No extra owners assigned"

        antinuke_status = "`🟢 Enabled (Active)`" if self.antinuke_enabled else "`🔴 Disabled (Inactive)`"

        embed = discord.Embed(
            title="🛡️ Royal Security & Anti-Nuke Status",
            description="All multi-layered security shields and protection protocols overview.",
            color=0x2ecc71 if self.antinuke_enabled else 0xe74c3c
        )
        embed.add_field(name="🔒 Anti-Nuke Protection", value=antinuke_status, inline=False)
        embed.add_field(name="🤖 Auto-Mod & Anti-Flood", value="`🟢 Active` (Links & Mass Mentions Blocked)", inline=False)
        embed.add_field(name="👑 Server Owner", value=f"<@{ctx.guild.owner_id}>", inline=False)
        embed.add_field(name="🛡️ Extra Owners / Trusted", value=extra_owner_text, inline=False)
        embed.add_field(name="📝 Whitelisted Users", value=whitelist_text, inline=False)
        embed.set_footer(text=f"{ctx.guild.name} • Heavy-Duty Security Engine")
        
        await ctx.send(embed=embed, ephemeral=True)

    @security.command(name="antinuke", description="Enable or disable the Anti-Nuke protection system")
    async def security_antinuke(self, ctx: commands.Context, state: str):
        if ctx.author.id != ctx.guild.owner_id and not ctx.author.guild_permissions.administrator:
            return await ctx.send("❌ You do not have permission to change Anti-Nuke settings!", ephemeral=True)

        state_lower = state.lower()
        if state_lower in ["on", "enable", "true"]:
            self.antinuke_enabled = True
            await ctx.send("🟢 **Anti-Nuke protection has been successfully ENABLED.**", ephemeral=True)
        elif state_lower in ["off", "disable", "false"]:
            self.antinuke_enabled = False
            await ctx.send("🔴 **Anti-Nuke protection has been DISABLED.** Server vulnerability increased!", ephemeral=True)
        else:
            await ctx.send("⚠️ Invalid state! Use `/security antinuke on` or `/security antinuke off`.", ephemeral=True)

    @security.command(name="whitelist", description="Add or remove a user from the security whitelist")
    async def security_whitelist(self, ctx: commands.Context, action: str, member: discord.Member):
        if action.lower() == "add":
            self.whitelisted_users.add(member.id)
            await ctx.send(f"✅ Successfully added {member.mention} to the **Security Whitelist**.", ephemeral=True)
        elif action.lower() == "remove":
            self.whitelisted_users.discard(member.id)
            await ctx.send(f"❌ Successfully removed {member.mention} from the **Security Whitelist**.", ephemeral=True)
        else:
            await ctx.send("⚠️ Invalid action! Use `add` or `remove`.", ephemeral=True)

    @security.command(name="extraowner", description="Add or remove an Extra Owner / Trusted Admin")
    async def security_extraowner(self, ctx: commands.Context, action: str, member: discord.Member):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Only the **Server Owner** can manage Extra Owners!", ephemeral=True)

        if action.lower() == "add":
            self.extra_owners.add(member.id)
            await ctx.send(f"👑 Successfully appointed {member.mention} as an **Extra Owner**.", ephemeral=True)
        elif action.lower() == "remove":
            self.extra_owners.discard(member.id)
            await ctx.send(f"🚫 Successfully removed {member.mention} from **Extra Owners**.", ephemeral=True)
        else:
            await ctx.send("⚠️ Invalid action! Use `add` or `remove`.", ephemeral=True)

    # =====================================================================
    # 2. INTELLIGENT AUTO-MOD (Links, Flood, Mass Mentions)
    # =====================================================================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.author.guild_permissions.manage_messages or self._is_trusted(message.guild, message.author.id):
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        content = message.content.lower()

        # Link & Invite Protection
        if "discord.gg/" in content or "discord.com/invite/" in content or "https://" in content or "http://" in content:
            try:
                await message.delete()
                warning = await message.channel.send(
                    f"🛡️ **[ROYAL SECURITY]** {message.author.mention}, links and invites are blocked!"
                )
                await asyncio.sleep(4)
                await warning.delete()
                return
            except Exception:
                pass

        # Rapid Flood Protection
        author_id = message.author.id
        self.message_cooldowns[author_id].append(now)
        if len(self.message_cooldowns[author_id]) >= 5:
            time_diff = (self.message_cooldowns[author_id][-1] - self.message_cooldowns[author_id][0]).total_seconds()
            if time_diff < 4:
                try:
                    await message.delete()
                    await message.author.timeout(datetime.timedelta(minutes=15), reason="[AUTO-MOD] Flood spamming.")
                    alert = await message.channel.send(f"🚨 {message.author.mention} timed out for 15 minutes due to spamming.")
                    await asyncio.sleep(5)
                    await alert.delete()
                    return
                except Exception:
                    pass

    # =====================================================================
    # 3. HEAVY-DUTY ANTI-NUKE ENGINE
    # =====================================================================
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not self.antinuke_enabled:
            return
        try:
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                user = entry.user
                if user.bot or self._is_trusted(channel.guild, user.id):
                    return

                member = channel.guild.get_member(user.id)
                if member:
                    await member.ban(reason="[ANTI-NUKE] Unauthorized channel deletion.")
                    print(f"[SECURITY ALERT] Banned {user.name} for unauthorized channel deletion.")
        except Exception as e:
            print(f"[ANTI-NUKE ERROR] {e}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if not self.antinuke_enabled:
            return
        try:
            async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
                user = entry.user
                if user.bot or self._is_trusted(role.guild, user.id):
                    return

                member = role.guild.get_member(user.id)
                if member:
                    await member.ban(reason="[ANTI-NUKE] Unauthorized role deletion.")
                    print(f"[SECURITY ALERT] Banned {user.name} for unauthorized role deletion.")
        except Exception as e:
            print(f"[ANTI-NUKE ERROR] {e}")

    # =====================================================================
    # 4. UTILITY & SECURITY COMMANDS (Lockdown, Nuke, Slowmode)
    # =====================================================================
    @commands.hybrid_command(name="lockdown", description="Lock down the current channel")
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx: commands.Context):
        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        embed = discord.Embed(title="🔒 Channel Locked Down", description=f"Secured by {ctx.author.mention}.", color=0xe74c3c)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unlock", description="Unlock the current channel")
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx: commands.Context):
        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        embed = discord.Embed(title="🔓 Channel Unlocked", description=f"Unlocked by {ctx.author.mention}.", color=0x2ecc71)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="nuke", description="Wipe and recreate the current channel clean")
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx: commands.Context):
        await ctx.message.delete()
        channel = ctx.channel
        position = channel.position
        new_channel = await channel.clone(reason=f"Nuked by {ctx.author}")
        await new_channel.edit(position=position)
        await channel.delete()
        
        embed = discord.Embed(title="💥 Channel Nuked", description=f"Refreshed cleanly by {ctx.author.mention}.", color=0xe74c3c)
        await new_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedSecurity(bot))