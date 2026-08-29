import discord
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="staff")
    @commands.has_permissions(administrator=True)
    async def staff(self, ctx, member: discord.Member):
        staff_role_id = 1213762834991939584
        role = ctx.guild.get_role(staff_role_id)
        if role:
            await member.add_roles(role)
            await ctx.send(f"✅ Successful! Added {role.mention} to {member.mention}")
        else:
            await ctx.send("❌ Staff role not found in this server!")

    @commands.command(name="buddy")
    @commands.has_permissions(administrator=True)
    async def buddy(self, ctx, member: discord.Member):
        buddy_role_id = 1213764069291720704
        role = ctx.guild.get_role(buddy_role_id)
        if role:
            await member.add_roles(role)
            await ctx.send(f"✅ Successful! Added {role.mention} to {member.mention}")
        else:
            await ctx.send("❌ Buddy role not found in this server!")

    @commands.command(name="qt")
    @commands.has_permissions(administrator=True)
    async def qt(self, ctx, member: discord.Member):
        qt_role_id = 1213763924718125056
        role = ctx.guild.get_role(qt_role_id)
        if role:
            await member.add_roles(role)
            await ctx.send(f"✅ Successful! Added {role.mention} to {member.mention}")
        else:
            await ctx.send("❌ QT role not found in this server!")

async def setup(bot):
    await bot.add_cog(Roles(bot))