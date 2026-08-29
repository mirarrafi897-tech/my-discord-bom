import discord
from discord.ext import commands
import random
import asyncio

class MiniGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slots", description="Play the royal slot machine game")
    async def slots(self, ctx: commands.Context):
        emojis = ["🍒", "🍋", "🍉", "⭐", "💎", "🔔"]
        result = [random.choice(emojis) for _ in range(3)]

        embed = discord.Embed(title="🎰 Royal Slot Machine", description=f"**[ {result[0]} | {result[1]} | {result[2]} ]**", color=0xf1c40f)

        if result[0] == result[1] == result[2]:
            embed.add_field(name="Result", value="🎉 **JACKPOT! You won the grand royal prize!**", inline=False)
            embed.color = 0x2ecc71
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            embed.add_field(name="Result", value="✨ **Nice! You got a partial match!**", inline=False)
        else:
            embed.add_field(name="Result", value="❌ **Aww, better luck next time!**", inline=False)
            embed.color = 0xe74c3c

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="8ball", description="Ask the magical 8-ball a yes/no question")
    async def eight_ball(self, ctx: commands.Context, *, question: str):
        answers = [
            "Yes, absolutely.", "Without a doubt.", "Most likely.", "Yes.",
            "Ask again later.", "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "Outlook not so good.", "My sources say no."
        ]
        embed = discord.Embed(title="🎱 Magic 8-Ball", color=0x9b59b6)
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(answers), inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rps", description="Play Rock, Paper, Scissors against the bot")
    async def rps(self, ctx: commands.Context, choice: str):
        choice = choice.lower()
        valid_choices = ["rock", "paper", "scissors"]
        if choice not in valid_choices:
            return await ctx.send("❌ Please choose either `rock`, `paper`, or `scissors`!", ephemeral=True)

        bot_choice = random.choice(valid_choices)

        if choice == bot_choice:
            result = "It's a tie!"
            color = 0xf1c40f
        elif (choice == "rock" and bot_choice == "scissors") or \
             (choice == "paper" and bot_choice == "rock") or \
             (choice == "scissors" and bot_choice == "paper"):
            result = "🎉 You win!"
            color = 0x2ecc71
        else:
            result = "🤖 Bot wins!"
            color = 0xe74c3c

        embed = discord.Embed(title="✊ Rock, Paper, Scissors", color=color)
        embed.add_field(name="Your Choice", value=choice.capitalize(), inline=True)
        embed.add_field(name="Bot's Choice", value=bot_choice.capitalize(), inline=True)
        embed.add_field(name="Outcome", value=result, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rate", description="Rate something or someone randomly from 0 to 100%")
    async def rate(self, ctx: commands.Context, *, target: str):
        score = random.randint(0, 100)
        embed = discord.Embed(title="📊 Royal Rating System", description=f"I rate **{target}** as **`{score}%`**!", color=0x3498db)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="howgay", description="Fun rating command for members")
    async def howgay(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        score = random.randint(0, 100)
        embed = discord.Embed(title="🏳️‍🌈 Fun Meter", description=f"**{target.name}** is **`{score}%`** fabulous!", color=0xe91e63)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MiniGames(bot))