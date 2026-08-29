import discord
from discord.ext import commands
import time
import datetime
from collections import defaultdict

# --- WHITELIST PERMISSION SELECT DROPDOWN VIEW ---
class WhitelistSelectView(discord.ui.View):
    def __init__(self, target_user: discord.User, cog_ref):
        super().__init__(timeout=60)
        self.target_user = target_user
        self.cog = cog_ref

        options = [
            discord.SelectOption(label="All Events (Full Trust)", value="all", emoji="⭐", description="Give bypass to all antinuke protection events"),
            discord.SelectOption(label="Anti Channel Create/Delete", value="channels", emoji="📁", description="Bypass channel creation and deletion"),
            discord.SelectOption(label="Anti Role Create/Delete", value="roles", emoji="🏷️", description="Bypass role management permissions"),
            discord.SelectOption(label="Anti Ban & Kick", value="punishments", emoji="🔨", description="Bypass mass ban and kick actions"),
            discord.SelectOption(label="Anti Bot Add", value="bots", emoji="🤖", description="Bypass adding bots to the server"),
            discord.SelectOption(label="Anti Webhook Create", value="webhooks", emoji="🔗", description="Bypass webhook creation")
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
        
        self.action_tracker = defaultdict(lambda: defaultdict(list))
        self.threshold_limit = 2
        self.threshold_time = 10
        self.msg_tracker = defaultdict(list)

    def is_trusted(self, guild: discord.Guild, user: discord.User, event_type: str = "all") -> bool:
        if user.id == guild.owner_id or user.id == self.bot.user.id or user.id in self.extra_owners:
            return True
        
        if user.id in self.whitelisted_users:
            user_perms = self.user_whitelist_perms.get(user.id, [])
            if "all" in user_perms or event_type in user_perms:
                return True

        return False

    async def check_and_punish(self, guild: discord.Guild, executor_id: int, action_type: str, reason: str):
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
                        await executor.kick(reason=f"[ANTINUKE] {reason}")
                    except Exception:
                        roles_to_remove = [r for r in executor.roles if r.name != "@everyone" and r < guild.me.top_role]
                        await executor.remove_roles(*roles_to_remove, reason="[ANTINUKE] Stripped roles")
            return True
        return False

    # ================= UNBYPASS SETUP COMMAND =================

    @commands.hybrid_command(name="security-setup", description="Setup Unbypass Security Role and AutoMod System")
    @commands.has_permissions(administrator=True)
    async def security_setup(self, ctx: commands.Context):
        await ctx.send("⏳ **Setting up Krypton-Style Unbypass Protection...**")
        
        guild = ctx.guild
        role_name = f"{self.bot.user.name} Unbypass System"
        
        unbypass_role = discord.utils.get(guild.roles, name=role_name)
        if not unbypass_role:
            try:
                unbypass_role = await guild.create_role(
                    name=role_name,
                    permissions=discord.Permissions.all(),
                    color=discord.Color.from_rgb(43, 45, 49),
                    reason="[SECURITY SETUP] Created Unbypass Protection Role"
                )
            except Exception as e:
                return await ctx.send(f"❌ Failed to create unbypass role: `{e}`")

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
                        f"• **AutoMod Anti-Spam:** `ENABLED 🟢`\n"
                        f"• **Protection Standard:** `Strict Unbypass Limit`",
            color=0x43b581
        )
        embed.set_footer(text=f"{self.bot.user.name} • Security System")
        await ctx.send(embed=embed)

    # ================= AUTOMOD LISTENER =================

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

    # ================= COMMANDS =================

    @commands.hybrid_command(name="whitelist", description="Add user to whitelist with specific permissions")
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx: commands.Context, user: discord.User):
        embed = discord.Embed(
            title="🛡️ Custom Whitelist Configuration",
            description=f"Choose which security permissions you want to grant to {user.mention}.\n"
                        f"Select options from the drop-down menu below:",
            color=0x5865f2
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="This action will expire in 60 seconds.")

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
                description=f"{user.mention} (`{user.id}`) is no longer in the whitelist.",
                color=0xff4747
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ User is not whitelisted!", ephemeral=True)

    # ================= REAL-TIME LISTENERS =================

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

async def setup(bot):
    await bot.add_cog(Security(bot))