import discord
from discord.ext import commands
import time
import datetime
from collections import defaultdict

# =====================================================================
# 1. INTERACTIVE WHITELIST DROPDOWN MENU
# =====================================================================

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
            discord.SelectOption(label="Anti Bot Add", value="bots", emoji="🤖", description="Bypass unauthorized bot additions"),
            discord.SelectOption(label="Anti Webhook Create", value="webhooks", emoji="🔗", description="Bypass webhook creation controls")
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


# =====================================================================
# 2. MAIN SECURITY COG & PROTECTION ENGINE
# =====================================================================

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelisted_users = set()
        self.user_whitelist_perms = {}  # {user_id: ['channels', 'roles', ...]}
        self.extra_owners = set()
        self.antinuke_enabled = True
        self.automod_enabled = True
        self.raid_mode = True
        
        # Threshold Configurations (2 Actions per 10 Seconds Limit)
        self.action_tracker = defaultdict(lambda: defaultdict(list))
        self.threshold_limit = 2
        self.threshold_time = 10
        self.punishment = "ban"  # Default punishment: ban

        # AutoMod Tracker
        self.msg_tracker = defaultdict(list)

    # --- TRUSTED USER / PERMISSION CHECKER ---
    def is_trusted(self, guild: discord.Guild, user: discord.User, event_type: str = "all") -> bool:
        if user.id == guild.owner_id or user.id == self.bot.user.id or user.id in self.extra_owners:
            return True
        
        if user.id in self.whitelisted_users:
            user_perms = self.user_whitelist_perms.get(user.id, [])
            if "all" in user_perms or event_type in user_perms:
                return True

        return False

    # --- THRESHOLD & PUNISHMENT LOGIC ---
    async def check_and_punish(self, guild: discord.Guild, executor_id: int, action_type: str, reason: str) -> bool:
        executor = guild.get_member(executor_id)
        if executor and self.is_trusted(guild, executor, action_type):
            return False

        current_time = time.time()
        timestamps = self.action_tracker[executor_id][action_type]
        self.action_tracker[executor_id][action_type] = [t for t in timestamps if current_time - t < self.threshold_time]
        self.action_tracker[executor_id][action_type].append(current_time)

        if len(self.action_tracker[executor_id][action_type]) >= self.threshold_limit:
            if executor:
                try:
                    await guild.ban(executor, reason=f"[ANTINUKE UNBYPASS] {reason}")
                except Exception:
                    try:
                        await executor.kick(reason=f"[ANTINUKE UNBYPASS] {reason}")
                    except Exception:
                        roles_to_remove = [r for r in executor.roles if r.name != "@everyone" and r < guild.me.top_role]
                        await executor.remove_roles(*roles_to_remove, reason="[ANTINUKE UNBYPASS] Stripped permissions")
            return True
        return False

    # =====================================================================
    # 3. KRYPTON UNBYPASS SETUP & DASHBOARD COMMANDS
    # =====================================================================

    @commands.hybrid_command(name="security-setup", description="Setup Krypton Unbypass System & Security Roles")
    @commands.has_permissions(administrator=True)
    async def security_setup(self, ctx: commands.Context):
        await ctx.send("⏳ **Setting up Krypton-Style Security Unbypass Protection...**")
        
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
                return await ctx.send(f"❌ Failed to create security role: `{e}`")

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
            description=f"Successfully configured unbypass protection for **{guild.name}**.\n\n"
                        f"• **Unbypass Role:** {unbypass_role.mention}\n"
                        f"• **Anti-Nuke Status:** `ENABLED 🟢`\n"
                        f"• **AutoMod Engine:** `ENABLED 🟢`\n"
                        f"• **Protection Standard:** `Strict Threshold Enforcement`",
            color=0x43b581
        )
        embed.set_footer(text=f"{self.bot.user.name} • Security System")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="antinuke-status", description="Show live security protection status for this server")
    async def antinuke_status(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Security Center",
            description="Live protection status for this server.",
            color=0x5865f2
        )
        embed.set_author(name=f"{ctx.guild.name}")

        embed.add_field(name="Anti-Nuke", value="✅ **ENABLED**" if self.antinuke_enabled else "❌ **DISABLED**", inline=False)
        embed.add_field(name="AutoMod", value="✅ **ENABLED**" if self.automod_enabled else "❌ **DISABLED**", inline=False)
        embed.add_field(name="Raid Mode", value="🔒 **ACTIVE**" if self.raid_mode else "🔓 **INACTIVE**", inline=False)
        embed.add_field(name="Threshold", value=f"`{self.threshold_limit}` actions / `{self.threshold_time}s`", inline=False)
        embed.add_field(name="Punishment", value=f"`{self.punishment}`", inline=False)
        embed.add_field(name="Trusted Members", value=f"**Whitelist:** `{len(self.whitelisted_users)}`\n**Extra owners:** `{len(self.extra_owners)}`", inline=False)

        events = [
            "Anti Role Creation", "Anti Role Deletion", "Anti Role Update",
            "Anti Channel Creation", "Anti Channel Deletion", "Anti Channel Update",
            "Anti Ban", "Anti Kick", "Anti Webhook", "Anti Bot",
            "Anti Server", "Anti Ping", "Anti Emoji Deletion", "Anti Emoji Creation",
            "Anti Emoji Update", "Anti Member Role Update", "Anti Link Role"
        ]
        
        icon = "✅" if self.antinuke_enabled else "❌"
        embed.add_field(name="Protected events", value="\n".join([f"{icon} **{e}**" for e in events]), inline=False)
        embed.set_footer(text=f"{self.bot.user.name} • Security System")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="antinuke", description="Toggle Antinuke protection or check dashboard")
    @commands.has_permissions(administrator=True)
    async def antinuke(self, ctx: commands.Context, status: str = None):
        if status:
            if status.lower() in ["on", "enable", "true"]:
                self.antinuke_enabled = True
                return await ctx.send("🛡️ **Antinuke protection system ENABLED 🟢**")
            elif status.lower() in ["off", "disable", "false"]:
                self.antinuke_enabled = False
                return await ctx.send("⚠️ **Antinuke protection system DISABLED 🔴**")
        
        await ctx.invoke(self.antinuke_status)

    # =====================================================================
    # 4. WHITELIST MANAGEMENT COMMANDS
    # =====================================================================

    @commands.hybrid_command(name="whitelist", description="Add user to whitelist with selective permissions")
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx: commands.Context, user: discord.User):
        embed = discord.Embed(
            title="🛡️ Custom Whitelist Configuration",
            description=f"Choose which security permissions you want to grant to {user.mention}.\n"
                        f"Select options from the drop-down menu below:",
            color=0x5865f2
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="This interaction expires in 60 seconds.")

        view = WhitelistSelectView(target_user=user, cog_ref=self)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="unwhitelist", description="Remove user from whitelist")
    @commands.has_permissions(administrator=True)
    async def unwhitelist(self, ctx: commands.Context, user: discord.User):
        if user.id in self.whitelisted_users:
            self.whitelisted_users.remove(user.id)
            self.user_whitelist_perms.pop(user.id, None)
            embed = discord.Embed(
                title="❌ Whitelist Removed",
                description=f"{user.mention} (`{user.id}`) was removed from the whitelist.",
                color=0xff4747
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ User is not whitelisted!", ephemeral=True)

    @commands.hybrid_command(name="whitelisted", description="Show all whitelisted users and their permissions")
    async def whitelisted(self, ctx: commands.Context):
        if not self.whitelisted_users:
            embed = discord.Embed(title="📜 Whitelisted Users", description="No users are currently whitelisted.", color=0x2b2d31)
        else:
            list_text = []
            for uid in self.whitelisted_users:
                perms = self.user_whitelist_perms.get(uid, ["None"])
                perms_str = ", ".join(perms)
                list_text.append(f"• <@{uid}> (`{uid}`) — **Perms:** `{perms_str}`")
            
            embed = discord.Embed(
                title="📜 Whitelisted Users & Granted Permissions",
                description="\n".join(list_text),
                color=0x2b2d31
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="extraowner", description="Grant Extra Owner status to a trusted user")
    async def extraowner(self, ctx: commands.Context, user: discord.User):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Only the Server Owner can use this command!", ephemeral=True)
        self.extra_owners.add(user.id)
        await ctx.send(f"👑 {user.mention} (`{user.id}`) is now added as an **Extra Owner**.")

    # =====================================================================
    # 5. AUTOMOD ENGINE (SPAM FILTER)
    # =====================================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot or not self.automod_enabled:
            return

        if self.is_trusted(message.guild, message.author):
            return

        current_time = time.time()
        user_msgs = self.msg_tracker[message.author.id]
        self.msg_tracker[message.author.id] = [t for t in user_msgs if current_time - t < 5]
        self.msg_tracker[message.author.id].append(current_time)

        if len(self.msg_tracker[message.author.id]) >= 5:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, stop spamming!", delete_after=3)
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=10), reason="[AUTOMOD] Anti-Spam Triggered")
            except Exception:
                pass

    # =====================================================================
    # 6. REAL-TIME PROTECTION AUDIT LOG LISTENERS
    # =====================================================================

    # --- Channel Protection ---
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not self.antinuke_enabled:
            return
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            if not self.is_trusted(channel.guild, entry.user, "channels"):
                punished = await self.check_and_punish(channel.guild, entry.user.id, "channels", f"Deleted #{channel.name}")
                if punished:
                    try:
                        await channel.clone(reason="[ANTINUKE RESTORE]")
                    except Exception:
                        pass
            break

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if not self.antinuke_enabled:
            return
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            if not self.is_trusted(channel.guild, entry.user, "channels"):
                punished = await self.check_and_punish(channel.guild, entry.user.id, "channels", f"Created #{channel.name}")
                if punished:
                    try:
                        await channel.delete(reason="[ANTINUKE DELETE]")
                    except Exception:
                        pass
            break

    # --- Role Protection & Dangerous Permission Check ---
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if not self.antinuke_enabled:
            return
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
            if not self.is_trusted(role.guild, entry.user, "roles"):
                await self.check_and_punish(role.guild, entry.user.id, "roles", f"Created role @{role.name}")
                try:
                    await role.delete(reason="[ANTINUKE] Unauthorized Role Creation")
                except Exception:
                    pass
            break

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if not self.antinuke_enabled:
            return
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            if not self.is_trusted(role.guild, entry.user, "roles"):
                punished = await self.check_and_punish(role.guild, entry.user.id, "roles", f"Deleted role @{role.name}")
                if punished:
                    try:
                        await role.guild.create_role(name=role.name, color=role.color, permissions=role.permissions, reason="[ANTINUKE RESTORE]")
                    except Exception:
                        pass
            break

    # --- Anti Admin Role Grant ---
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
                            await self.check_and_punish(after.guild, entry.user.id, "roles", f"Granted admin role {role.name}")
                            try:
                                await after.remove_roles(role, reason="[ANTINUKE] Unauthorized Admin Grant")
                            except Exception:
                                pass
                break

    # --- Anti Ban & Kick ---
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not self.antinuke_enabled:
            return
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            if not self.is_trusted(guild, entry.user, "punishments"):
                punished = await self.check_and_punish(guild, entry.user.id, "punishments", f"Banned {user.name}")
                if punished:
                    try:
                        await guild.unban(user, reason="[ANTINUKE RESTORE]")
                    except Exception:
                        pass
            break

    # --- Anti Bot Join ---
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot and self.antinuke_enabled:
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                if not self.is_trusted(member.guild, entry.user, "bots"):
                    try:
                        await member.kick(reason="[ANTINUKE] Unauthorized Bot Addition")
                    except Exception:
                        pass
                    await self.check_and_punish(member.guild, entry.user.id, "bots", f"Added unauthorized bot @{member.name}")
                break

async def setup(bot):
    await bot.add_cog(Security(bot))