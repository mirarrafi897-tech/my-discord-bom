import discord
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- INDIVIDUAL ROLE COMMANDS ---

    @commands.hybrid_command(name="giverole", description="Give a role to a member")
    @commands.has_permissions(manage_roles=True)
    async def giverole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ You cannot give a role higher than or equal to your highest role!", ephemeral=True)
        
        await member.add_roles(role)
        embed = discord.Embed(
            title="✅ Role Added",
            description=f"Added {role.mention} to {member.mention}",
            color=role.color if role.color.value != 0 else 0x43b581
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="removerole", description="Remove a role from a member")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ You cannot remove a role higher than or equal to your highest role!", ephemeral=True)
        
        await member.remove_roles(role)
        embed = discord.Embed(
            title="❌ Role Removed",
            description=f"Removed {role.mention} from {member.mention}",
            color=0xff4747
        )
        await ctx.send(embed=embed)

    # --- ROLE CREATION & MANAGEMENT ---

    @commands.hybrid_command(name="createrole", description="Create a new role with custom name and color (HEX)")
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx: commands.Context, name: str, color_hex: str = "2b2d31"):
        try:
            color = discord.Color(int(color_hex.replace("#", ""), 16))
            role = await ctx.guild.create_role(name=name, color=color, reason=f"Created by {ctx.author}")
            embed = discord.Embed(
                title="✨ Role Created",
                description=f"Successfully created role {role.mention}\n**Color:** `#{color_hex}`",
                color=color
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to create role! Error: `{e}`", ephemeral=True)

    @commands.hybrid_command(name="deleterole", description="Delete a role from server")
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx: commands.Context, role: discord.Role):
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Cannot delete this role due to hierarchy!", ephemeral=True)
        role_name = role.name
        await role.delete(reason=f"Deleted by {ctx.author}")
        embed = discord.Embed(title="🗑️ Role Deleted", description=f"Successfully deleted role `{role_name}`", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rolecolor", description="Change color of a role")
    @commands.has_permissions(manage_roles=True)
    async def rolecolor(self, ctx: commands.Context, role: discord.Role, hex_code: str):
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Hierarchy error!", ephemeral=True)
        color = discord.Color(int(hex_code.replace("#", ""), 16))
        await role.edit(color=color)
        embed = discord.Embed(title="🎨 Role Color Changed", description=f"Changed {role.mention} color to `#{hex_code}`", color=color)
        await ctx.send(embed=embed)

    # --- MASS ROLE MANAGEMENT ---

    @commands.hybrid_command(name="roleall", description="Add a role to all human members in the server")
    @commands.has_permissions(administrator=True)
    async def roleall(self, ctx: commands.Context, role: discord.Role):
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Hierarchy error!", ephemeral=True)

        await ctx.send(f"⏳ Adding {role.mention} to all humans...", ephemeral=True)
        count = 0
        for member in ctx.guild.members:
            if not member.bot and role not in member.roles:
                try:
                    await member.add_roles(role)
                    count += 1
                except Exception:
                    continue

        embed = discord.Embed(title="✨ Mass Role Completed", description=f"Gave {role.mention} to `{count}` members.", color=0x43b581)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="removeroleall", description="Remove a role from all members")
    @commands.has_permissions(administrator=True)
    async def removeroleall(self, ctx: commands.Context, role: discord.Role):
        if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Hierarchy error!", ephemeral=True)

        await ctx.send(f"⏳ Removing {role.mention} from all members...", ephemeral=True)
        count = 0
        for member in ctx.guild.members:
            if role in member.roles:
                try:
                    await member.remove_roles(role)
                    count += 1
                except Exception:
                    continue

        embed = discord.Embed(title="🧹 Mass Remove Completed", description=f"Removed {role.mention} from `{count}` members.", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rolebots", description="Add a role to all bots in server")
    @commands.has_permissions(administrator=True)
    async def rolebots(self, ctx: commands.Context, role: discord.Role):
        await ctx.send(f"⏳ Adding {role.mention} to all bots...", ephemeral=True)
        count = 0
        for member in ctx.guild.members:
            if member.bot and role not in member.roles:
                try:
                    await member.add_roles(role)
                    count += 1
                except Exception:
                    continue
        embed = discord.Embed(title="🤖 Bot Role Completed", description=f"Gave {role.mention} to `{count}` bots.", color=0x43b581)
        await ctx.send(embed=embed)

    # --- SPECIAL SHORTCUT ROLES ---

    @commands.hybrid_command(name="staff", description="Give/Remove staff role")
    @commands.has_permissions(manage_roles=True)
    async def staff(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(description=f"Removed {role.mention} staff role from {member.mention}", color=0xff4747)
        else:
            await member.add_roles(role)
            embed = discord.Embed(description=f"Gave {role.mention} staff role to {member.mention}", color=0x43b581)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="vip", description="Give/Remove VIP role")
    @commands.has_permissions(manage_roles=True)
    async def vip(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(description=f"Removed VIP {role.mention} from {member.mention}", color=0xff4747)
        else:
            await member.add_roles(role)
            embed = discord.Embed(description=f"Gave VIP {role.mention} to {member.mention}", color=0xffaa00)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="friend", description="Give/Remove Friend role")
    @commands.has_permissions(manage_roles=True)
    async def friend(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(description=f"Removed Friend role {role.mention} from {member.mention}", color=0xff4747)
        else:
            await member.add_roles(role)
            embed = discord.Embed(description=f"Gave Friend role {role.mention} to {member.mention}", color=0x43b581)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="inrole", description="Show members inside a role")
    async def inrole(self, ctx: commands.Context, role: discord.Role):
        members = [m.mention for m in role.members[:20]]
        total = len(role.members)
        embed = discord.Embed(
            title=f"👥 Members in {role.name} ({total})",
            description=", ".join(members) if members else "No members in this role.",
            color=role.color
        )
        if total > 20:
            embed.set_footer(text=f"And {total - 20} more members...")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Roles(bot))