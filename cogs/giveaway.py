import discord
from discord.ext import commands
import asyncio
import datetime

class GiveawayAndPolls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="gstart", description="Start a giveaway in the channel")
    @commands.has_permissions(manage_guild=True)
    async def gstart(self, ctx: commands.Context, minutes: int, *, prize: str):
        embed = discord.Embed(
            title="🎉 ROYAL GIVEAWAY 🎉",
            description=f"**Prize:** `{prize}`\n\n"
                        f"React with 🎉 to enter!\n"
                        f"**Duration:** `{minutes} minutes`\n"
                        f"**Hosted by:** {ctx.author.mention}",
            color=0xf1c40f
        )
        embed.timestamp = datetime.datetime.utcnow()
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        # Delete the command invocation message to keep channel clean
        try:
            await ctx.message.delete()
        except Exception:
            pass

        await asyncio.sleep(minutes * 60)

        # Fetch message again to check reactions
        new_msg = await ctx.channel.fetch_message(msg.id)
        users = []
        for reaction in new_msg.reactions:
            if reaction.emoji == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        users.append(user)

        if users:
            winner = random.choice(users)
            win_embed = discord.Embed(
                title="🏆 GIVEAWAY ENDED!",
                description=f"Congratulations {winner.mention}! You won **`{prize}`**!",
                color=0x2ecc71
            )
            await ctx.send(embed=win_embed)
        else:
            await ctx.send(f"❌ Giveaway for **{prize}** ended, but no valid entries were found.")

    @commands.hybrid_command(name="poll", description="Create a quick interactive voting poll")
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx: commands.Context, *, question: str):
        embed = discord.Embed(
            title="📊 Server Community Poll",
            description=question,
            color=0x3498db
        )
        embed.set_footer(text=f"Poll created by {ctx.author.name}")
        embed.timestamp = datetime.datetime.utcnow()

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        
        try:
            await ctx.message.delete()
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(GiveawayAndPolls(bot))