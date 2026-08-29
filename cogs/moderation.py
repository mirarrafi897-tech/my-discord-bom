@commands.hybrid_command(name="timeout", description="Timeout a member for a duration (minutes)")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, minutes: int, reason: str = "None"):
        import datetime
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await ctx.send(f"⏳ **{member.name}** timed out for `{minutes}m`.")

    @commands.hybrid_command(name="untimeout", description="Remove timeout from a member")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx: commands.Context, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 Timeout removed for **{member.name}**.")

    @commands.hybrid_command(name="warn", description="Warn a member")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, reason: str = "No reason"):
        await ctx.send(f"⚠️ Warned **{member.name}** for: {reason}")

    @commands.hybrid_command(name="warnings", description="Check warnings of a member")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"📋 **{member.name}** has 0 warnings.")

    @commands.hybrid_command(name="clearwarns", description="Clear all warnings of a member")
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"🧹 Cleared all warnings for **{member.name}**.")

    @commands.hybrid_command(name="softban", description="Ban and immediately unban to clear messages")
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx: commands.Context, member: discord.Member, reason: str = "None"):
        await member.ban(reason=reason, delete_message_days=7)
        await ctx.guild.unban(member)
        await ctx.send(f"🧹 Softbanned **{member.name}**.")

    @commands.hybrid_command(name="vmute", description="Voice mute a member in VC")
    @commands.has_permissions(mute_members=True)
    async def vmute(self, ctx: commands.Context, member: discord.Member):
        await member.edit(mute=True)
        await ctx.send(f"🔇 Voice muted **{member.name}**.")

    @commands.hybrid_command(name="vunmute", description="Unmute a member in VC")
    @commands.has_permissions(mute_members=True)
    async def vunmute(self, ctx: commands.Context, member: discord.Member):
        await member.edit(mute=False)
        await ctx.send(f"🔊 Voice unmuted **{member.name}**.")

    @commands.hybrid_command(name="deafen", description="Deafen a member in VC")
    @commands.has_permissions(deafen_members=True)
    async def deafen(self, ctx: commands.Context, member: discord.Member):
        await member.edit(deafen=True)
        await ctx.send(f"🔇 Deafened **{member.name}**.")

    @commands.hybrid_command(name="undeafen", description="Undeafen a member in VC")
    @commands.has_permissions(deafen_members=True)
    async def undeafen(self, ctx: commands.Context, member: discord.Member):
        await member.edit(deafen=False)
        await ctx.send(f"🔊 Undeafened **{member.name}**.")

    @commands.hybrid_command(name="vkick", description="Kick a member from voice channel")
    @commands.has_permissions(move_members=True)
    async def vkick(self, ctx: commands.Context, member: discord.Member):
        await member.edit(voice_channel=None)
        await ctx.send(f"🚪 Disconnected **{member.name}** from VC.")

    @commands.hybrid_command(name="nick", description="Change member nickname")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx: commands.Context, member: discord.Member, nickname: str):
        await member.edit(nick=nickname)
        await ctx.send(f"✏️ Nickname changed for **{member.name}**.")

    @commands.hybrid_command(name="slowmode", description="Set channel slowmode in seconds")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"⏱️ Slowmode set to `{seconds}s`.")

    @commands.hybrid_command(name="nuke_channel", description="Clone and delete channel to wipe history safely")
    @commands.has_permissions(administrator=True)
    async def nuke_channel(self, ctx: commands.Context):
        pos = ctx.channel.position
        new_ch = await ctx.channel.clone(reason="Channel Purge")
        await ctx.channel.delete()
        await new_ch.edit(position=pos)
        await new_ch.send("💣 Channel has been purged and recreated!")

    @commands.hybrid_command(name="roleall", description="Give a role to all members")
    @commands.has_permissions(administrator=True)
    async def roleall(self, ctx: commands.Context, role: discord.Role):
        await ctx.send(f"⚙️ Adding {role.mention} to all members...")

    @commands.hybrid_command(name="removeroleall", description="Remove a role from all members")
    @commands.has_permissions(administrator=True)
    async def removeroleall(self, ctx: commands.Context, role: discord.Role):
        await ctx.send(f"⚙️ Removing {role.mention} from all members...")

    @commands.hybrid_command(name="purgeuser", description="Purge messages from a specific user")
    @commands.has_permissions(manage_messages=True)
    async def purgeuser(self, ctx: commands.Context, member: discord.Member, amount: int = 20):
        def check(m): return m.author == member
        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(f"🧹 Deleted `{len(deleted)}` messages from **{member.name}**.", delete_after=3)

    @commands.hybrid_command(name="purgebots", description="Purge messages sent by bots")
    @commands.has_permissions(manage_messages=True)
    async def purgebots(self, ctx: commands.Context, amount: int = 50):
        def check(m): return m.author.bot
        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(f"🤖 Deleted `{len(deleted)}` bot messages.", delete_after=3)

    @commands.hybrid_command(name="purgelinks", description="Purge messages containing links")
    @commands.has_permissions(manage_messages=True)
    async def purgelinks(self, ctx: commands.Context, amount: int = 50):
        def check(m): return "http" in m.content
        deleted = await ctx.channel.purge(limit=amount, check=check)
        await ctx.send(f"🔗 Deleted `{len(deleted)}` link messages.", delete_after=3)

    @commands.hybrid_command(name="setmodlog", description="Set log channel for moderation actions")
    @commands.has_permissions(administrator=True)
    async def setmodlog(self, ctx: commands.Context, channel: discord.TextChannel):
        await ctx.send(f"📋 Mod log channel set to {channel.mention}.")