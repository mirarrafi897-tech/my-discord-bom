@commands.hybrid_command(name="botinfo", description="Show bot technical specifications")
    async def botinfo(self, ctx: commands.Context):
        embed = discord.Embed(title="🤖 Bot System Info", color=0x2b2d31)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Shards", value=str(self.bot.shard_count), inline=True)
        embed.add_field(name="Library", value="discord.py v2.x", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="banner", description="Get user banner image")
    async def banner(self, ctx: commands.Context, user: discord.User = None):
        user = user or ctx.author
        u = await self.bot.fetch_user(user.id)
        if u.banner:
            await ctx.send(u.banner.url)
        else:
            await ctx.send("❌ User has no banner.")

    @commands.hybrid_command(name="servericon", description="Get server icon")
    async def servericon(self, ctx: commands.Context):
        if ctx.guild.icon:
            await ctx.send(ctx.guild.icon.url)
        else:
            await ctx.send("❌ Server has no icon.")

    @commands.hybrid_command(name="serverbanner", description="Get server banner")
    async def serverbanner(self, ctx: commands.Context):
        if ctx.guild.banner:
            await ctx.send(ctx.guild.banner.url)
        else:
            await ctx.send("❌ Server has no banner.")

    @commands.hybrid_command(name="emojis", description="List all server emojis")
    async def emojis(self, ctx: commands.Context):
        emojis = " ".join([str(e) for e in ctx.guild.emojis[:30]]) or "No custom emojis."
        await ctx.send(f"😃 **Server Emojis:**\n{emojis}")

    @commands.hybrid_command(name="roles", description="List all server roles")
    async def roles(self, ctx: commands.Context):
        roles_list = ", ".join([r.name for r in ctx.guild.roles[:20]])
        await ctx.send(f"📜 **Roles ({len(ctx.guild.roles)}):** {roles_list}")

    @commands.hybrid_command(name="boosters", description="List server boosters")
    async def boosters(self, ctx: commands.Context):
        boosters = ", ".join([m.name for m in ctx.guild.premium_subscribers]) or "No boosters yet."
        await ctx.send(f"🚀 **Boosters:** {boosters}")

    @commands.hybrid_command(name="vcdeafenall", description="Deafen all members in your VC")
    @commands.has_permissions(deafen_members=True)
    async def vcdeafenall(self, ctx: commands.Context):
        if ctx.author.voice:
            for m in ctx.author.voice.channel.members:
                await m.edit(deafen=True)
            await ctx.send("🔇 Deafened all in VC.")

    @commands.hybrid_command(name="vcundeafenall", description="Undeafen all members in VC")
    @commands.has_permissions(deafen_members=True)
    async def vcundeafenall(self, ctx: commands.Context):
        if ctx.author.voice:
            for m in ctx.author.voice.channel.members:
                await m.edit(deafen=False)
            await ctx.send("🔊 Undeafened all in VC.")

    @commands.hybrid_command(name="vcmuteall", description="Mute all members in your VC")
    @commands.has_permissions(mute_members=True)
    async def vcmuteall(self, ctx: commands.Context):
        if ctx.author.voice:
            for m in ctx.author.voice.channel.members:
                await m.edit(mute=True)
            await ctx.send("🔇 Muted all in VC.")

    @commands.hybrid_command(name="vcunmuteall", description="Unmute all members in VC")
    @commands.has_permissions(mute_members=True)
    async def vcunmuteall(self, ctx: commands.Context):
        if ctx.author.voice:
            for m in ctx.author.voice.channel.members:
                await m.edit(mute=False)
            await ctx.send("🔊 Unmuted all in VC.")

    @commands.hybrid_command(name="vcmove", description="Move VC members to another VC")
    @commands.has_permissions(move_members=True)
    async def vcmove(self, ctx: commands.Context, channel: discord.VoiceChannel):
        if ctx.author.voice:
            for m in ctx.author.voice.channel.members:
                await m.edit(voice_channel=channel)
            await ctx.send(f"🚚 Moved members to `{channel.name}`.")

    @commands.hybrid_command(name="embed", description="Create a custom embed message")
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx: commands.Context, title: str, description: str):
        emb = discord.Embed(title=title, description=description, color=0x2b2d31)
        await ctx.send(embed=emb)

    @commands.hybrid_command(name="say", description="Make bot repeat a message")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: commands.Context, *, message: str):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.hybrid_command(name="poll", description="Create a quick yes/no poll")
    async def poll(self, ctx: commands.Context, question: str):
        emb = discord.Embed(title="📊 Poll", description=question, color=0x2b2d31)
        msg = await ctx.send(embed=emb)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.hybrid_command(name="membercount", description="Show server member count breakdown")
    async def membercount(self, ctx: commands.Context):
        total = ctx.guild.member_count
        bots = sum(1 for m in ctx.guild.members if m.bot)
        humans = total - bots
        await ctx.send(f"👥 **Total:** {total} | 🧑 **Humans:** {humans} | 🤖 **Bots:** {bots}")

    @commands.hybrid_command(name="firstmsg", description="Get link to the first message in channel")
    async def firstmsg(self, ctx: commands.Context):
        msg = [m async for m in ctx.channel.history(limit=1, oldest_first=True)][0]
        await ctx.send(f"🔗 **First Message:** {msg.jump_url}")

    @commands.hybrid_command(name="uptime", description="Check bot status uptime")
    async def uptime(self, ctx: commands.Context):
        await ctx.send("⏱️ Bot has been online and operating smoothly.")

    @commands.hybrid_command(name="invite", description="Get bot invite link")
    async def invite(self, ctx: commands.Context):
        await ctx.send(f"🔗 **Invite Me:** https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands")

    @commands.hybrid_command(name="support", description="Get security support link")
    async def support(self, ctx: commands.Context):
        await ctx.send("🛡️ **Support Server:** https://discord.gg/your-support-server")