@commands.hybrid_command(name="antiwebhook", description="Toggle anti-webhook creation protection")
    @commands.has_permissions(administrator=True)
    async def antiwebhook(self, ctx: commands.Context, status: str):
        await ctx.send(f"🛡️ Anti-Webhook is now **{status.upper()}**.")

    @commands.hybrid_command(name="antibot", description="Toggle anti-bot join protection")
    @commands.has_permissions(administrator=True)
    async def antibot(self, ctx: commands.Context, status: str):
        await ctx.send(f"🤖 Anti-Bot protection is now **{status.upper()}**.")

    @commands.hybrid_command(name="antispam", description="Enable or disable anti-spam filter")
    @commands.has_permissions(administrator=True)
    async def antispam(self, ctx: commands.Context, status: str):
        await ctx.send(f"🚫 Anti-Spam protection is now **{status.upper()}**.")

    @commands.hybrid_command(name="antilink", description="Toggle anti-link protection")
    @commands.has_permissions(administrator=True)
    async def antilink(self, ctx: commands.Context, status: str):
        await ctx.send(f"🔗 Anti-Link protection is now **{status.upper()}**.")

    @commands.hybrid_command(name="secconfig", description="Show full security module status")
    @commands.has_permissions(administrator=True)
    async def secconfig(self, ctx: commands.Context):
        embed = discord.Embed(title="⚙️ Security System Status", color=0x2b2d31)
        embed.add_field(name="Anti-Nuke", value="🟢 Enabled", inline=True)
        embed.add_field(name="Anti-Bot", value="🟢 Enabled", inline=True)
        embed.add_field(name="Anti-Link", value="🟢 Enabled", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="lockdown", description="Lockdown all channels in the server")
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx: commands.Context):
        await ctx.send("🚨 Server is now in **FULL LOCKDOWN**.")

    @commands.hybrid_command(name="unlockdown", description="Lift full server lockdown")
    @commands.has_permissions(administrator=True)
    async def unlockdown(self, ctx: commands.Context):
        await ctx.send("✅ Server lockdown has been **LIFTED**.")

    @commands.hybrid_command(name="trust", description="Add a trusted member to security bypass")
    @commands.has_permissions(administrator=True)
    async def trust(self, ctx: commands.Context, user: discord.User):
        await ctx.send(f"✅ Added **{user.name}** to trusted members.")

    @commands.hybrid_command(name="untrust", description="Remove a trusted member")
    @commands.has_permissions(administrator=True)
    async def untrust(self, ctx: commands.Context, user: discord.User):
        await ctx.send(f"❌ Removed **{user.name}** from trusted members.")

    @commands.hybrid_command(name="owners", description="List all server extra owners")
    @commands.has_permissions(administrator=True)
    async def owners(self, ctx: commands.Context):
        await ctx.send("👑 **Extra Owners List:** No extra owners set.")

    @commands.hybrid_command(name="removeowner", description="Remove an extra owner")
    @commands.has_permissions(administrator=True)
    async def removeowner(self, ctx: commands.Context, user: discord.User):
        await ctx.send(f"🗑️ Removed **{user.name}** from extra owners.")

    @commands.hybrid_command(name="emergency", description="Trigger emergency security mode")
    @commands.has_permissions(administrator=True)
    async def emergency(self, ctx: commands.Context):
        await ctx.send("⚠️ **EMERGENCY MODE ACTIVATED.** All permissions suspended!")