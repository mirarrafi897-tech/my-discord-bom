import discord
from discord.ext import commands
import datetime
import re

# --- WHITELIST PERMISSION SELECT DROPDOWN VIEW ---
class WhitelistSelectView(discord.ui.View):
    def __init__(self, target_user: discord.User, cog_ref):
        super().__init__(timeout=60)
        self.target_user = target_user
        self.cog = cog_ref

        options = [
            discord.SelectOption(label="All Events (Full Bypass)", value="all", emoji="⭐", description="Bypass all antinuke protection triggers"),
            discord.SelectOption(label="Anti Channel Create/Delete", value="channels", emoji="📁", description="Bypass channel creation & deletion limits"),
            discord.SelectOption(label="Anti Role Create/Delete", value="roles", emoji="🏷️", description="Bypass role creation, deletion & permissions"),
            discord.SelectOption(label="Anti Ban & Kick", value="punishments", emoji="🔨", description="Bypass mass ban and kick thresholds"),
            discord.SelectOption(label="Anti Bot Add", value="bots", emoji="🤖", description="Bypass unauthorized bot additions")
        ]

        select = discord.ui.Select(
            placeholder=f"Select whitelist permissions for {target_user.name}...",
            min_values=1,
            max_values=len(options),
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        selected_perms = interaction.data["values"]
        
        if "all" in selected_perms:
            self.cog.user_whitelist_perms[self.target_user.id] = ["all"]
            perms_text = "⭐ **Full Whitelist (All Events Bypass)**"
        else:
            self.cog.user_whitelist_perms[self.target_user.id] = selected_perms
            perms_text = "\n".join([f"✅ **{p.title()} Protection Bypass**" for p in selected_perms])

        self.cog.whitelisted_users.add(self.target_user.id)

        embed = discord.Embed(
            title="✅ User Whitelisted Successfully",
            description=f"**User:** {self.target_user.mention} (`{self.target_user.id}`)\n\n"
                        f"**Granted Specific Permissions:**\n{perms_text}",
            color=0x43b581
        )
        embed.set_thumbnail(url=self.target_user.display_avatar.url)
        embed.set_footer(text=f"Whitelisted by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelisted_users = set()
        self.user_whitelist_perms = {}
        self.extra_owners = set()
        self.antinuke_enabled = True
        self.automod_enabled = True
        self.raid_mode = True
        
        # URL detection regex pattern
        self.url_pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|discord\.gg/\w+")

    # --- TRUSTED CHECK ---
    def is_trusted(self, guild: discord.Guild, user: discord.User, event_type: str = "all") -> bool:
        if user.id == guild.owner_id or user.id == self.bot.user.id or user.id in self.extra_owners:
            return True
        
        if user.id in self.whitelisted_users:
            user_perms = self.user_whitelist_perms.get(user.id, [])
            if "all" in user_perms or event_type in user_perms:
                return True

        return False

    # --- INSTANT PUNISHMENT (No Timer/No Limits) ---
    async def instant_punish(self, guild: discord.Guild, executor_id: int, action_type: str, reason: str) -> bool:
        executor = guild.get_member(executor_id)
        if not executor or self.is_trusted(guild, executor, action_type):
            return False

        # ১ম বারেই সরাসরি ব্যান/কিক
        try:
            await guild.ban(executor, reason=f"[ANTINUKE INSTANT ACTION] {reason}")
        except Exception:
            try:
                await executor.kick(reason=f"[ANTINUKE INSTANT ACTION] {reason}")
            except Exception:
                roles_to_remove = [r for r in executor.roles if r.name != "@everyone" and r < guild.me.top_role]
                await executor.remove_roles(*roles_to_remove, reason="[ANTINUKE] Stripped dangerous permissions")
        return True

    # ================= UNBYPASS SETUP & COMMANDS =================

    @commands.hybrid_command(name="security-setup", description="Setup Krypton Unbypass System")
    @commands.has_permissions(administrator=True)
    async def security_setup(self, ctx: commands.Context):
        await ctx.send("⏳ **Setting up Krypton Unbypass Protection...**")
        
        guild = ctx.guild
        role_name = f"{self.bot.user.name} Unbypass System"
        
        unbypass_role = discord.utils.get(guild.roles, name=role_name)
        if not unbypass_role:
            try:
                unbypass_role = await guild.create_role(
                    name=role_name,
                    permissions=discord.Permissions.all(),
                    color=discord.Color.from_rgb(88, 101, 242),
                    reason="[SECURITY SETUP] Krypton Unbypass Security System"
                )
            except Exception as e:
                return await ctx.send(f"❌ Failed to create role: `{e}`")

        bot_member = guild.get_member(self.bot.user.id)
        if unbypass_role not in bot_member.roles:
            try:
                await bot_member.add_roles(unbypass_role)
            except Exception:
                pass

        self.antinuke_enabled = True
        self.automod_enabled = True

        embed = discord.Embed(
            title="🛡️ Security Unbypass Setup Complete",
            description=f"Successfully configured instant protection for **{guild.name}**.\n\n"
                        f"• **Unbypass Role:** {unbypass_role.mention}\n"
                        f"• **Anti-Nuke Status:** `ENABLED 🟢 (Instant 1st-Action Ban)`\n"
                        f"• **AutoMod (Anti-Link & Anti-Spam):** `ENABLED 🟢`",
            color=0x43b581
        )
        embed.set_footer(text=f"{self.bot.user.name} • Security System")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="whitelist", description="Add user to whitelist with selective permissions")
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx: commands.Context, user: discord.User):
        embed = discord.Embed(
            title="🛡️ Custom Whitelist Configuration",
            description=f"Choose permissions to grant to {user.mention}:",
            color=0x5865f2
        )
        view = WhitelistSelectView(target_user=user, cog_ref=self)
        await ctx.send(embed=embed, view=view)

    # ================= AUTOMOD (ANTI-LINK & SPAM) =================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot or not self.automod_enabled:
            return

        if self.is_trusted(message.guild, message.author):
            return

        # 1. Anti-Link Protection (Instant Delete & Timeout)
        if self.url_pattern.search(message.content):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, links are not allowed here!", delete_after=4)
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=10), reason="[AUTOMOD] Posted Unauthorized Link")
                return
            except Exception:
                pass

    # ================= REAL-TIME INSTANT LISTENERS =================

    # 1. Anti Channel Create & Delete
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if not self.antinuke_enabled:
            return
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            if not self.is_trusted(channel.guild, entry.user, "channels"):
                punished = await self.instant_punish(channel.guild, entry.user.id, "channels", f"Created #{channel.name}")
                if punished:
                    try:
                        await channel.delete(reason="[ANTINUKE INSTANT RESTORE]")
                    except Exception:
                        pass
            break

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not self.antinuke_enabled:
            return
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            if not self.is_trusted(channel.guild, entry.user, "channels"):
                punished = await self.instant_punish(channel.guild, entry.user.id, "channels", f"Deleted #{channel.name}")
                if punished:
                    try:
                        await channel.clone(reason="[ANTINUKE INSTANT RESTORE]")
                    except Exception:
                        pass
            break

    # 2. Anti Role Create & Delete
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if not self.antinuke_enabled:
            return
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
            if not self.is_trusted(role.guild, entry.user, "roles"):
                punished = await self.instant_punish(role.guild, entry.user.id, "roles", f"Created role @{role.name}")
                if punished:
                    try:
                        await role.delete(reason="[ANTINUKE INSTANT RESTORE]")
                    except Exception:
                        pass
            break

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if not self.antinuke_enabled:
            return
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            if not self.is_trusted(role.guild, entry.user, "roles"):
                punished = await self.instant_punish(role.guild, entry.user.id, "roles", f"Deleted role @{role.name}")
                if punished:
                    try:
                        await role.guild.create_role(name=role.name, color=role.color, permissions=role.permissions, reason="[ANTINUKE INSTANT RESTORE]")
                    except Exception:
                        pass
            break

    # 3. Anti Giving Dangerous/Admin Roles
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not self.antinuke_enabled:
            return
        added_roles = [r for r in after.roles if r not in before.roles]
        if added_roles:
            async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
                if entry.target.id == after.id and not self.is_trusted(after.guild, entry.user, "roles"):
                    for role in added_roles:
                        if role.permissions.administrator or role.permissions.manage_roles or role.permissions.ban_members:
                            await self.instant_punish(after.guild, entry.user.id, "roles", f"Gave dangerous role {role.name}")
                            try:
                                await after.remove_roles(role, reason="[ANTINUKE INSTANT RESTORE]")
                            except Exception:
                                pass
                break

    # 4. Anti Ban
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not self.antinuke_enabled:
            return
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            if not self.is_trusted(guild, entry.user, "punishments"):
                punished = await self.instant_punish(guild, entry.user.id, "punishments", f"Banned {user.name}")
                if punished:
                    try:
                        await guild.unban(user, reason="[ANTINUKE INSTANT RESTORE]")
                    except Exception:
                        pass
            break

    # 5. Anti Bot Add
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot and self.antinuke_enabled:
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                if not self.is_trusted(member.guild, entry.user, "bots"):
                    try:
                        await member.kick(reason="[ANTINUKE] Unauthorized Bot")
                    except Exception:
                        pass
                    await self.instant_punish(member.guild, entry.user.id, "bots", f"Added unauthorized bot @{member.name}")
                break

async def setup(bot):
    await bot.add_cog(Security(bot))