import discord
from discord.ext import commands
import datetime
import re
from collections import defaultdict

# --- WHITELIST PERMISSION SELECT DROPDOWN VIEW (FOR USER) ---
class UserWhitelistSelectView(discord.ui.View):
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


# --- WHITELIST PERMISSION SELECT DROPDOWN VIEW (FOR ROLE) ---
class RoleWhitelistSelectView(discord.ui.View):
    def __init__(self, target_role: discord.Role, cog_ref):
        super().__init__(timeout=60)
        self.target_role = target_role
        self.cog = cog_ref

        options = [
            discord.SelectOption(label="All Events (Full Bypass)", value="all", emoji="⭐", description="Bypass all antinuke protection triggers"),
            discord.SelectOption(label="Anti Channel Create/Delete", value="channels", emoji="📁", description="Bypass channel creation & deletion limits"),
            discord.SelectOption(label="Anti Role Create/Delete", value="roles", emoji="🏷️", description="Bypass role creation, deletion & permissions"),
            discord.SelectOption(label="Anti Ban & Kick", value="punishments", emoji="🔨", description="Bypass mass ban and kick thresholds"),
            discord.SelectOption(label="Anti Bot Add", value="bots", emoji="🤖", description="Bypass unauthorized bot additions")
        ]

        select = discord.ui.Select(
            placeholder=f"Select whitelist permissions for @{target_role.name}...",
            min_values=1,
            max_values=len(options),
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        selected_perms = interaction.data["values"]
        
        if "all" in selected_perms:
            self.cog.role_whitelist_perms[self.target_role.id] = ["all"]
            perms_text = "⭐ **Full Whitelist (All Events Bypass)**"
        else:
            self.cog.role_whitelist_perms[self.target_role.id] = selected_perms
            perms_text = "\n".join([f"✅ **{p.title()} Protection Bypass**" for p in selected_perms])

        self.cog.whitelisted_roles.add(self.target_role.id)

        embed = discord.Embed(
            title="✅ Role Whitelisted Successfully",
            description=f"**Role:** {self.target_role.mention} (`{self.target_role.id}`)\n\n"
                        f"**Granted Specific Permissions:**\n{perms_text}",
            color=0x43b581
        )
        embed.set_footer(text=f"Whitelisted by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Users Whitelist Data
        self.whitelisted_users = set()
        self.user_whitelist_perms = {}
        
        # Roles Whitelist Data
        self.whitelisted_roles = set()
        self.role_whitelist_perms = {}

        self.extra_owners = set()
        self.antinuke_enabled = True
        self.automod_enabled = True
        self.raid_mode = True
        
        self.spam_tracker = defaultdict(list)
        self.url_pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|discord\.gg/\w+")

    # --- TRUSTED CHECK (USER & ROLE WISE) ---
    def is_trusted(self, guild: discord.Guild, user: discord.User, event_type: str = "all") -> bool:
        if user.id == guild.owner_id or user.id == self.bot.user.id or user.id in self.extra_owners:
            return True
        
        # Check User Whitelist
        if user.id in self.whitelisted_users:
            u_perms = self.user_whitelist_perms.get(user.id, [])
            if "all" in u_perms or event_type in u_perms:
                return True

        # Check Role Whitelist (If user has a whitelisted role)
        member = guild.get_member(user.id)
        if member:
            for role in member.roles:
                if role.id in self.whitelisted_roles:
                    r_perms = self.role_whitelist_perms.get(role.id, [])
                    if "all" in r_perms or event_type in r_perms:
                        return True

        return False

    # --- INSTANT PUNISHMENT ---
    async def instant_punish(self, guild: discord.Guild, executor_id: int, action_type: str, reason: str) -> bool:
        executor = guild.get_member(executor_id)
        if not executor or self.is_trusted(guild, executor, action_type):
            return False

        try:
            await guild.ban(executor, reason=f"[ANTINUKE INSTANT ACTION] {reason}")
        except Exception:
            try:
                await executor.kick(reason=f"[ANTINUKE INSTANT ACTION] {reason}")
            except Exception:
                roles_to_remove = [r for r in executor.roles if r.name != "@everyone" and r < guild.me.top_role]
                await executor.remove_roles(*roles_to_remove, reason="[ANTINUKE] Stripped dangerous permissions")
        return True

    # ================= SECURITY SETUP =================

    @commands.hybrid_command(name="security-setup", description="Turn ON/OFF Security Setup and Unbypass System")
    @commands.has_permissions(administrator=True)
    async def security_setup(self, ctx: commands.Context, action: str = "on"):
        guild = ctx.guild
        role_name = f"{self.bot.user.name} Unbypass System"
        unbypass_role = discord.utils.get(guild.roles, name=role_name)

        if action.lower() in ["off", "disable", "stop"]:
            self.antinuke_enabled = False
            self.automod_enabled = False
            
            if unbypass_role:
                try:
                    await unbypass_role.delete(reason="[SECURITY SETUP OFF] System disabled")
                except Exception:
                    pass

            embed = discord.Embed(
                title="⚠️ Security Setup Disabled",
                description=f"Antinuke & AutoMod protections have been **DISABLED** for **{guild.name}**.",
                color=0xff4747
            )
            return await ctx.send(embed=embed)

        await ctx.send("⏳ **Setting up Krypton Unbypass Protection...**")
        
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
                        f"• **Anti-Nuke Status:** `ENABLED 🟢`\n"
                        f"• **AutoMod (Link & Spam):** `ENABLED 🟢`",
            color=0x43b581
        )
        embed.set_footer(text=f"{self.bot.user.name} • Security System")
        await ctx.send(embed=embed)

    # ================= WHITELIST USER COMMANDS =================

    @commands.hybrid_command(name="whitelist-user", description="Add a user to whitelist with selective permissions")
    @commands.has_permissions(administrator=True)
    async def whitelist_user(self, ctx: commands.Context, user: discord.User):
        embed = discord.Embed(
            title="🛡️ Custom User Whitelist Configuration",
            description=f"Choose permissions to grant to {user.mention}:",
            color=0x5865f2
        )
        view = UserWhitelistSelectView(target_user=user, cog_ref=self)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="unwhitelist-user", description="Remove a user from whitelist")
    @commands.has_permissions(administrator=True)
    async def unwhitelist_user(self, ctx: commands.Context, user: discord.User):
        if user.id in self.whitelisted_users:
            self.whitelisted_users.remove(user.id)
            self.user_whitelist_perms.pop(user.id, None)
            embed = discord.Embed(
                title="❌ User Whitelist Removed",
                description=f"{user.mention} (`{user.id}`) was removed from the whitelist.",
                color=0xff4747
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ User is not in the whitelist!", ephemeral=True)

    # ================= WHITELIST ROLE COMMANDS =================

    @commands.hybrid_command(name="whitelist-role", description="Add a role to whitelist with selective permissions")
    @commands.has_permissions(administrator=True)
    async def whitelist_role(self, ctx: commands.Context, role: discord.Role):
        embed = discord.Embed(
            title="🛡️ Custom Role Whitelist Configuration",
            description=f"Choose permissions to grant to role {role.mention}:",
            color=0x5865f2
        )
        view = RoleWhitelistSelectView(target_role=role, cog_ref=self)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="unwhitelist-role", description="Remove a role from whitelist")
    @commands.has_permissions(administrator=True)
    async def unwhitelist_role(self, ctx: commands.Context, role: discord.Role):
        if role.id in self.whitelisted_roles:
            self.whitelisted_roles.remove(role.id)
            self.role_whitelist_perms.pop(role.id, None)
            embed = discord.Embed(
                title="❌ Role Whitelist Removed",
                description=f"{role.mention} (`{role.id}`) was removed from the role whitelist.",
                color=0xff4747
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Role is not in the whitelist!", ephemeral=True)

    # ================= WHITELISTED LIST COMMAND =================

    @commands.hybrid_command(name="whitelisted", description="Show all whitelisted users and roles")
    async def whitelisted(self, ctx: commands.Context):
        embed = discord.Embed(title="📜 Whitelisted Users & Roles", color=0x2b2d31)
        
        # Whitelisted Users
        if self.whitelisted_users:
            u_list = []
            for uid in self.whitelisted_users:
                perms = self.user_whitelist_perms.get(uid, ["None"])
                u_list.append(f"• <@{uid}> — `{', '.join(perms)}`")
            embed.add_field(name="👥 Whitelisted Users", value="\n".join(u_list), inline=False)
        else:
            embed.add_field(name="👥 Whitelisted Users", value="None", inline=False)

        # Whitelisted Roles
        if self.whitelisted_roles:
            r_list = []
            for rid in self.whitelisted_roles:
                perms = self.role_whitelist_perms.get(rid, ["None"])
                r_list.append(f"• <@&{rid}> — `{', '.join(perms)}`")
            embed.add_field(name="🏷️ Whitelisted Roles", value="\n".join(r_list), inline=False)
        else:
            embed.add_field(name="🏷️ Whitelisted Roles", value="None", inline=False)

        await ctx.send(embed=embed)

    # ================= EXTRA OWNER MANAGEMENT =================

    @commands.hybrid_command(name="extraowner", description="Add or Remove an Extra Owner")
    async def extraowner(self, ctx: commands.Context, option: str, user: discord.User):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Only the **Server Owner** can manage Extra Owners!", ephemeral=True)

        if option.lower() in ["add", "set"]:
            self.extra_owners.add(user.id)
            await ctx.send(f"👑 {user.mention} (`{user.id}`) is now added as an **Extra Owner**.")
        elif option.lower() in ["remove", "del"]:
            if user.id in self.extra_owners:
                self.extra_owners.remove(user.id)
                await ctx.send(f"❌ {user.mention} (`{user.id}`) was removed from Extra Owners.")
            else:
                await ctx.send("❌ User is not an Extra Owner!", ephemeral=True)

    # ================= AUTOMOD & LISTENERS =================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot or not self.automod_enabled:
            return

        if self.is_trusted(message.guild, message.author):
            return

        # 1. Anti-Link
        if self.url_pattern.search(message.content):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, links are not allowed here!", delete_after=4)
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=10), reason="[AUTOMOD] Posted Link")
                return
            except Exception:
                pass

        # 2. Anti-Spam
        now = datetime.datetime.utcnow().timestamp()
        user_id = message.author.id
        self.spam_tracker[user_id] = [t for t in self.spam_tracker[user_id] if now - t < 3]
        self.spam_tracker[user_id].append(now)

        if len(self.spam_tracker[user_id]) >= 4:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, stop spamming!", delete_after=4)
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=10), reason="[AUTOMOD] Anti-Spam Triggered")
                self.spam_tracker[user_id].clear()
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if not self.antinuke_enabled:
            return
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            if not self.is_trusted(channel.guild, entry.user, "channels"):
                punished = await self.instant_punish(channel.guild, entry.user.id, "channels", f"Created #{channel.name}")
                if punished:
                    try:
                        await channel.delete(reason="[ANTINUKE RESTORE]")
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
                        await channel.clone(reason="[ANTINUKE RESTORE]")
                    except Exception:
                        pass
            break

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if not self.antinuke_enabled:
            return
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
            if not self.is_trusted(role.guild, entry.user, "roles"):
                punished = await self.instant_punish(role.guild, entry.user.id, "roles", f"Created role @{role.name}")
                if punished:
                    try:
                        await role.delete(reason="[ANTINUKE RESTORE]")
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
                        await role.guild.create_role(name=role.name, color=role.color, permissions=role.permissions, reason="[ANTINUKE RESTORE]")
                    except Exception:
                        pass
            break

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
                                await after.remove_roles(role, reason="[ANTINUKE RESTORE]")
                            except Exception:
                                pass
                break

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not self.antinuke_enabled:
            return
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            if not self.is_trusted(guild, entry.user, "punishments"):
                punished = await self.instant_punish(guild, entry.user.id, "punishments", f"Banned {user.name}")
                if punished:
                    try:
                        await guild.unban(user, reason="[ANTINUKE RESTORE]")
                    except Exception:
                        pass
            break

async def setup(bot):
    await bot.add_cog(Security(bot))