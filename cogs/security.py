import discord
from discord.ext import commands

SECURITY_EVENTS = [
    "Anti Role Creation", "Anti Role Deletion", "Anti Role Update",
    "Anti Channel Creation", "Anti Channel Deletion", "Anti Channel Update",
    "Anti Ban", "Anti Kick", "Anti Webhook", "Anti Bot",
    "Anti Server", "Anti Ping", "Anti Emoji Deletion", "Anti Emoji Creation",
    "Anti Emoji Update", "Anti Member Role Update", "Anti Link Role"
]

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="unwhitelist")
    @commands.has_permissions(administrator=True)
    async def unwhitelist(ctx, self, user: discord.User):
        embed = discord.Embed(
            description=f"**{user.name}** is now unwhitelisted from all events:\n",
            color=0x2b2d31
        )
        
        events_formatted = "\n".join([f"✅ **{event}**" for event in SECURITY_EVENTS])
        embed.description += f"\n{events_formatted}"
        
        footer_text = f"{ctx.guild.name} | {ctx.message.created_at.strftime('%m/%d/%Y %I:%M %p')}"
        embed.set_footer(text=footer_text)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Security(bot))