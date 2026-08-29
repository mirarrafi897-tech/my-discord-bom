import discord
from discord.ext import commands
import time
from collections import defaultdict

# --- WHITELIST PERMISSION SELECT DROPDOWN VIEW ---
class WhitelistSelectView(discord.ui.View):
    def __init__(self, target_user: discord.User, cog_ref):
        super().__init__(timeout=60)
        self.target_user = target_user
        self.cog = cog_ref

        # ড্রপডাউন মেনু তৈরি
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
        # নির্বাচিত পারমিশনগুলো প্রসেস করা
        selected_perms = interaction.data["values"]
        
        # বট ডেটাতে সেভ করা
        if "all" in selected_perms:
            self.cog.user_whitelist_perms[self.target_user.id] = ["all"]
            perms_text = "⭐ **Full Whitelist (All Events Bypass)**"
        else:
            self.cog.user_whitelist_perms[self.target_user.id] = selected_perms
            perms_text = "\n".join([f"✅ **{p.title()} Protection Bypass**" for p in selected_perms])

        self.cog.whitelisted_users.add(self.target_user.id)

        # সুন্দর কনফার্মেশন ইমবেড
        embed = discord.Embed(
            title="✅ User Whitelisted Successfully",
            description=f"**User:** {self.target_user.mention} (`{self.target_user.id}`)\n\n"
                        f"**Granted Specific Permissions:**\n{perms_text}",
            color=0x43b581
        )
        embed.set_thumbnail(url=self.target_user.display_avatar.url)
        embed.set_footer(text=f"Whitelisted by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

        # ভিউটি বন্ধ করে ড্রপডাউন সরিয়ে নেওয়া
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelisted_users = set()
        self.user_whitelist_perms = {}  # {user_id: ['channels', 'roles', ...]}
        self.extra_owners = set()
        self.antinuke_enabled = True
        self.automod_enabled = True
        self.raid_mode = True
        
        self.action_tracker = defaultdict(lambda: defaultdict(list))
        self.threshold_limit = 2
        self.threshold_time = 10

    # --- PERMISSION PER-EVENT CHECK ---
    def is_trusted(self, guild: discord.Guild, user: discord.User, event_type: str = "all") -> bool:
        if user.id == guild.owner_id or user.id == self.bot.user.id or user.id in self.extra_owners:
            return True
        
        if user.id in self.whitelisted_users:
            user_perms = self.user_whitelist_perms.get(user.id, [])
            if "all" in user_perms or event_type in user_perms:
                return True

        return False

    # --- PUNISHMENT SYSTEM ---
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
                    await guild.ban(executor, reason=f"[ANTINUKE] {reason}")
                except Exception:
                    try:
                        await executor.kick(reason=f"[ANTINUKE] {reason}")
                    except Exception:
                        pass
            return True
        return False

    # ================= WHITELIST COMMAND WITH INTERACTIVE EMBED =================

    @commands.hybrid_command(name="whitelist", description="Add user to whitelist with specific event permissions")
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

    # ================= REAL-TIME ANTINUKE EVENT LISTENERS =================

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

async def setup(bot):
    await bot.add_cog(Security(bot))
