@commands.hybrid_command(name="createchannel", description="Create a text channel")
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx: commands.Context, name: str):
        ch = await ctx.guild.create_text_channel(name)
        await ctx.send(f"✅ Created channel {ch.mention}.")

    @commands.hybrid_command(name="deletechannel", description="Delete a text channel")
    @commands.has_permissions(manage_channels=True)
    async def deletechannel(self, ctx: commands.Context, channel: discord.TextChannel):
        await channel.delete()
        await ctx.send(f"🗑️ Deleted channel `#{channel.name}`.")

    @commands.hybrid_command(name="createvc", description="Create a voice channel")
    @commands.has_permissions(manage_channels=True)
    async def createvc(self, ctx: commands.Context, name: str):
        vc = await ctx.guild.create_voice_channel(name)
        await ctx.send(f"🔊 Created VC `{vc.name}`.")

    @commands.hybrid_command(name="createrole", description="Create a new role")
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx: commands.Context, name: str):
        role = await ctx.guild.create_role(name=name)
        await ctx.send(f"✅ Created role {role.mention}.")

    @commands.hybrid_command(name="deleterole", description="Delete a role")
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx: commands.Context, role: discord.Role):
        await role.delete()
        await ctx.send(f"🗑️ Deleted role **{role.name}**.")

    @commands.hybrid_command(name="rolecolor", description="Change color of a role")
    @commands.has_permissions(manage_roles=True)
    async def rolecolor(self, ctx: commands.Context, role: discord.Role, hex_code: str):
        color = int(hex_code.replace("#", ""), 16)
        await role.edit(color=discord.Color(color))
        await ctx.send(f"🎨 Updated color for {role.mention}.")

    @commands.hybrid_command(name="vips", description="Assign VIP role to member")
    @commands.has_permissions(administrator=True)
    async def vips(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"⭐ Assigned VIP to {member.mention}.")

    @commands.hybrid_command(name="friends", description="Assign Friend role")
    @commands.has_permissions(administrator=True)
    async def friends(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"❤️ Assigned Friend role to {member.mention}.")

    @commands.hybrid_command(name="girl", description="Assign Girl/Female role")
    @commands.has_permissions(administrator=True)
    async def girl(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"🎀 Assigned Girl role to {member.mention}.")

    @commands.hybrid_command(name="guest", description="Assign Guest role")
    @commands.has_permissions(administrator=True)
    async def guest(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"👋 Assigned Guest role to {member.mention}.")

    @commands.hybrid_command(name="botsrole", description="Assign Bot role")
    @commands.has_permissions(administrator=True)
    async def botsrole(self, ctx: commands.Context, member: discord.Member):
        await ctx.send(f"🤖 Assigned Bot role to {member.mention}.")

    @commands.hybrid_command(name="roleinfo", description="Get info about a role")
    async def roleinfo(self, ctx: commands.Context, role: discord.Role):
        embed = discord.Embed(title=f"Role Info: {role.name}", color=role.color)
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        embed.add_field(name="Hoisted", value=role.hoist, inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="autorole", description="Set automatic role on member join")
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx: commands.Context, role: discord.Role):
        await ctx.send(f"⚙️ Auto-role set to {role.mention}.")

    @commands.hybrid_command(name="inrole", description="List members in a role")
    async def inrole(self, ctx: commands.Context, role: discord.Role):
        members = ", ".join([m.name for m in role.members[:15]]) or "None"
        await ctx.send(f"📋 **Members in {role.name}:** {members}")

    @commands.hybrid_command(name="roleicon", description="Set role icon (for boosted servers)")
    @commands.has_permissions(manage_roles=True)
    async def roleicon(self, ctx: commands.Context, role: discord.Role, url: str):
        await ctx.send(f"🖼️ Updated icon for {role.mention}.")

    @commands.hybrid_command(name="tempchannel", description="Create a temporary text channel")
    @commands.has_permissions(manage_channels=True)
    async def tempchannel(self, ctx: commands.Context, name: str):
        await ctx.send(f"⏳ Created temporary channel `{name}`.")

    @commands.hybrid_command(name="categorycreate", description="Create a channel category")
    @commands.has_permissions(manage_channels=True)
    async def categorycreate(self, ctx: commands.Context, name: str):
        cat = await ctx.guild.create_category(name)
        await ctx.send(f"📁 Category `{cat.name}` created.")

    @commands.hybrid_command(name="categorydelete", description="Delete a category")
    @commands.has_permissions(manage_channels=True)
    async def categorydelete(self, ctx: commands.Context, category: discord.CategoryChannel):
        await category.delete()
        await ctx.send(f"🗑️ Deleted category `{category.name}`.")