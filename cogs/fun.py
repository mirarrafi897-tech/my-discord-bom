import discord
from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="roll", description="Roll a dice (1-100)")
    async def roll(self, ctx: commands.Context):
        num = random.randint(1, 100)
        await ctx.send(f"🎲 You rolled: `{num}`")

    @commands.hybrid_command(name="coinflip", description="Flip a coin (Heads/Tails)")
    async def coinflip(self, ctx: commands.Context):
        res = random.choice(["Heads 🪙", "Tails 🪙"])
        await ctx.send(f"🪙 Result: **{res}**")

    @commands.hybrid_command(name="8ball", description="Ask magic 8ball a question")
    async def eightball(self, ctx: commands.Context, question: str):
        answers = ["Yes, absolutely!", "No way.", "Ask again later.", "Without a doubt!", "My sources say no."]
        embed = discord.Embed(title="🎱 Magic 8Ball", color=0x2b2d31)
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(answers), inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="slap", description="Slap a user playfully")
    async def slap(self, ctx: commands.Context, member: discord.Member):
        embed = discord.Embed(description=f"🖐️ {ctx.author.mention} slapped {member.mention}!", color=0xffaa00)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="hug", description="Give a hug to a member")
    async def hug(self, ctx: commands.Context, member: discord.Member):
        embed = discord.Embed(description=f"🤗 {ctx.author.mention} gave a warm hug to {member.mention}!", color=0x43b581)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rate", description="Rate anything out of 10")
    async def rate(self, ctx: commands.Context, thing: str):
        rating = random.randint(0, 10)
        await ctx.send(f"⭐ I rate **{thing}** a `{rating}/10`")

async def setup(bot):
    await bot.add_cog(Fun(bot))