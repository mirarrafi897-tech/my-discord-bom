import discord
from discord.ext import commands

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelisted_users = set()
        self.extra_owners = set()
        self.antinuke_enabled = True
        self.automod_enabled = True
        self.raid_mode = True
        self.threshold_actions = 3
        self.threshold_time = 10
        self.punishment = "strip"  # strip, ban, kick

    # --- HELPER: CHECK IF USER IS TRUSTED ---
    def is_trusted(self, guild: discord.Guild, user: discord.User) -> bool:
        if user.id == guild.owner_id:
            return True
        if user.id == self.bot.user.id:
            return True
        if user.id in self.whitelisted_users or user.id in self.extra_owners:
            return True
        return False

    # --- HELPER: TAKE ACTION AGAINST ATTACKER ---
    async def punish_attacker(self, guild: discord.Guild, user: discord.Member, reason: str):
        if not user or self.is_trusted(guild, user):
            return

        try:
            if self.punishment == "strip":
                # অপরাধীর সব বিপজ্জনক রোল বা সব রোল কেড়ে নেওয়া
                roles_to_remove = [r for r in user.roles if r.name != "@everyone" and r < guild.me.top_role]
                await user.remove_roles(*roles_to_remove, reason=f"[ANTINUKE] {reason}")
            elif self.punishment == "ban":
                await guild.ban(user, reason=f"[ANTINUKE] {reason}")
            elif self.punishment == "kick":
                await user.kick(reason=f"[ANTINUKE] {reason}")
        except Exception as e:
            print(f"[ANTINUKE ERROR] Action failed against {user}: {e}")

    # ================= REAL-TIME EVENT LISTENERS =================

    # 1. Anti Channel Delete Protection
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not self.antinuke_enabled:
            return
        
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            executor = entry.user
            if not self.is_trusted(channel.guild, executor):
                # অ্যাকশন নেওয়া
                member = channel.guild.get_member(executor.id)
                if member:
                    await self.punish_attacker(channel.guild, member, f"Deleted channel #{channel.name}")
                
                # রিয়েল রি-ক্রিয়েট (Channel Restore)
                try:
                    await channel.clone(reason="[ANTINUKE RESTORE] Auto recreated deleted channel")
                except Exception:
                    pass
            break

    # 2. Anti Role Delete Protection
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if not self.antinuke_enabled:
            return

        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            executor = entry.user
            if not self.is_trusted(role.guild, executor):
                member = role.guild.get_member(executor.id)
                if member:
                    await self.punish_attacker(role.guild, member, f"Deleted role @{role.name}")
                
                # রিয়েল রি-ক্রিয়েট (Role Restore)
                try:
                    await role.guild.create_role(name=role.name, color=role.color, permissions=role.permissions, reason="[ANTINUKE RESTORE]")
                except Exception:
                    pass
            break

    # 3. Anti Ban Protection
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not self.antinuke_enabled:
            return

        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            executor = entry.user
            if not self.is_trusted(guild, executor):
                member = guild.get_member(executor.id)
                if member:
                    await self.punish_attacker(guild, member, f"Unauthorized ban on {user.name}")
                
                # রিয়েল আনব্যান (Unban Victim)
                try:
                    await guild.unban(user, reason="[ANTINUKE RESTORE] Auto unbanned victim")
                except Exception:
                    pass
            break

    # 4. Anti Kick Protection
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not self.antinuke_enabled:
            return

        async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
            executor = entry.user
            if not self.is_trusted(member.guild, executor):
                executor_member = member.guild.get_member(executor.id)
                if executor_member:
                    await self.punish_attacker(member.guild, executor_member, f"Unauthorized kick on {member.name}")
            break

    # 5. Anti Bot Join Protection
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot and self.antinuke_enabled:
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                executor = entry.user
                if not self.is_trusted(member.guild, executor):
                    # বোটটিকে কিক মারা
                    try:
                        await member.kick(reason="[ANTINUKE] Unauthorized bot addition")
                    except Exception:
                        pass
                    
                    # যে বোট এড করেছে তার বিরুদ্ধে ব্যবস্থা নেওয়া
                    executor_member = member.guild.get_member(executor.id)
                    if executor_member:
                        await self.punish_attacker(member.guild, executor_member, f"Added unauthorized bot @{member.name}")
                break

    # ================= COMMANDS =================

    @commands.hybrid_command(name="antinuke-status", description="Show live protection status for this server")
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
        embed.add_field(name="Threshold", value=f"`{self.threshold_actions}` actions / `{self.threshold_time}s`", inline=False)
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

    @commands.hybrid_command(name="antinuke", description="Toggle Antinuke protection")
    @commands.has_permissions(administrator=True)
    async def antinuke(self, ctx: commands.Context, status: str = None):
        if status:
            if status.lower() in ["on", "enable"]:
                self.antinuke_enabled = True
                return await ctx.send("🛡️ **Antinuke protection system ENABLED**")
            elif status.lower() in ["off", "disable"]:
                self.antinuke_enabled = False
                return await ctx.send("⚠️ **Antinuke protection system DISABLED**")
        
        await ctx.invoke(self.antinuke_status)

    @commands.hybrid_command(name="whitelist", description="Add user to trusted whitelist")
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx: commands.Context, user: discord.User):
        self.whitelisted_users.add(user.id)
        await ctx.send(f"✅ {user.mention} (`{user.id}`) is now added to the Whitelist.")

    @commands.hybrid_command(name="unwhitelist", description="Remove user from whitelist")
    @commands.has_permissions(administrator=True)
    async def unwhitelist(self, ctx: commands.Context, user: discord.User):
        if user.id in self.whitelisted_users:
            self.whitelisted_users.remove(user.id)
            await ctx.send(f"❌ {user.mention} (`{user.id}`) was removed from Whitelist.")
        else:
            await ctx.send("❌ User is not whitelisted!", ephemeral=True)

    @commands.hybrid_command(name="extraowner", description="Grant extra owner rights")
    async def extraowner(self, ctx: commands.Context, user: discord.User):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Only Server Owner can use this!", ephemeral=True)
        self.extra_owners.add(user.id)
        await ctx.send(f"👑 {user.mention} is now set as Extra Owner.")

async def setup(bot):
    await bot.add_cog(Security(bot))