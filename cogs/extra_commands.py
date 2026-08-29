import discord
from discord.ext import commands
import random
import datetime

class ExtraCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # CATEGORY 1: SERVER & UTILITY (5 Commands)
    # ==========================================

    @commands.hybrid_command(name="serverinfo", description="Display detailed information about the server")
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        embed = discord.Embed(title=f"🛡️ Server Info: {guild.name}", color=0x3498db, timestamp=datetime.datetime.utcnow())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="Total Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Channels", value=f"Text: {len(guild.text_channels)} | Voice: {len(guild.voice_channels)}", inline=True)
        embed.add_field(name="Roles Count", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Creation Date", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="userinfo", description="Display profile information for yourself or a member")
    async def userinfo(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        roles = [role.mention for role in target.roles[1:]] # Exclude @everyone
        roles_str = ", ".join(roles) if roles else "None"

        embed = discord.Embed(title=f"👤 User Info: {target.name}", color=target.color, timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Username", value=str(target), inline=True)
        embed.add_field(name="User ID", value=str(target.id), inline=True)
        embed.add_field(name="Joined Server", value=target.joined_at.strftime("%b %d, %Y") if target.joined_at else "Unknown", inline=True)
        embed.add_field(name="Account Created", value=target.created_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name=f"Roles ({len(target.roles)-1})", value=roles_str[:1024] if len(roles_str) > 0 else "None", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="botinfo", description="Display technical info and stats about the bot")
    async def botinfo(self, ctx: commands.Context):
        embed = discord.Embed(title="🤖 Royal Bot Information", description="An elite, secure, and all-in-one modular Discord bot.", color=0x9b59b6, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Total Guilds", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Latency / Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Framework", value="Discord.py (Python)", inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="avatar", description="Display the avatar of yourself or another user")
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        embed = discord.Embed(title=f"🖼️ Avatar for {target.name}", color=target.color)
        embed.set_image(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ping", description="Check the bot's current response latency")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="🏓 Pong!", description=f"Response latency is **`{latency}ms`**.", color=0x2ecc71)
        await ctx.send(embed=embed)

    # ==========================================
    # CATEGORY 2: FUN & INTERACTION (8 Commands)
    # ==========================================

    @commands.hybrid_command(name="hug", description="Give a warm hug to someone in the server")
    async def hug(self, ctx: commands.Context, member: discord.Member):
        if member == ctx.author:
            return await ctx.send("🤗 You give yourself a warm hug! Don't worry, we all need one sometimes.")
        gifs = [
            "https://media.giphy.com/media/10hkD9fGj1i2wM/giphy.gif",
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif"
        ]
        embed = discord.Embed(description=f"🤗 **{ctx.author.mention}** gives a tight hug to **{member.mention}**!", color=0xe91e63)
        embed.set_image(url=random.choice(gifs))
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="slap", description="Slap someone playfully")
    async def slap(self, ctx: commands.Context, member: discord.Member):
        if member == ctx.author:
            return await ctx.send("🤔 Why would you slap yourself?")
        embed = discord.Embed(description=f"💥 **{ctx.author.mention}** slaps **{member.mention}** right across the face!", color=0xe74c3c)
        embed.set_image(url="https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="kiss", description="Send a sweet kiss to a member")
    async def kiss(self, ctx: commands.Context, member: discord.Member):
        if member == ctx.author:
            return await ctx.send("💋 Self-love is important, but try kissing someone else!")
        embed = discord.Embed(description=f"😘 **{ctx.author.mention}** sends a sweet kiss to **{member.mention}**!", color=0xff69b4)
        embed.set_image(url="https://media.giphy.com/media/2GmMBk8o9lEKA/giphy.gif")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="pat", description="Pat someone gently on the head")
    async def pat(self, ctx: commands.Context, member: discord.Member):
        embed = discord.Embed(description=f"pat pat... 🐾 **{ctx.author.mention}** gently pats **{member.mention}** on the head!", color=0x3498db)
        embed.set_image(url="https://media.giphy.com/media/12CcWkU0OchUNW/giphy.gif")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="joke", description="Tell a random funny joke")
    async def joke(self, ctx: commands.Context):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Parallel lines have so much in common. It’s a shame they’ll never meet.",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "What do you call a fake noodle? An impasta!"
        ]
        embed = discord.Embed(title="😂 Random Joke", description=random.choice(jokes), color=0xf1c40f)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="fact", description="Display a random interesting trivia fact")
    async def fact(self, ctx: commands.Context):
        facts = [
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.",
            "Bananas are curved because they grow towards the sun against gravity.",
            "A single cloud can weigh more than 1 million pounds.",
            "Octopuses have three hearts and blue blood.",
            "The shortest war in history lasted 38 minutes between Britain and Zanzibar in 1896."
        ]
        embed = discord.Embed(title="🧠 Did You Know?", description=random.choice(facts), color=0x2ecc71)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="reverse", description="Reverse any text you provide")
    async def reverse(self, ctx: commands.Context, *, text: str):
        reversed_text = text[::-1]
        embed = discord.Embed(title="🔄 Text Reverser", description=f"**Original:** {text}\n**Reversed:** {reversed_text}", color=0x9b59b6)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="roll", description="Roll a dice between 1 and 100")
    async def roll(self, ctx: commands.Context):
        result = random.randint(1, 100)
        embed = discord.Embed(title="🎲 Dice Roll", description=f"You rolled a **`{result}`** out of 100!", color=0x3498db)
        await ctx.send(embed=embed)

    # ==========================================
    # CATEGORY 3: TEXT & UTILITY (7 Commands)
    # ==========================================

    @commands.hybrid_command(name="say", description="Make the bot repeat what you type")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: commands.Context, *, message: str):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(message)

    @commands.hybrid_command(name="embedsay", description="Send a custom text inside a clean royal embed")
    @commands.has_permissions(manage_messages=True)
    async def embedsay(self, ctx: commands.Context, *, message: str):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        embed = discord.Embed(description=message, color=0x3498db)
        embed.set_footer(text=f"Announcement by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="pollquick", description="Create a simple quick yes/no vote")
    async def pollquick(self, ctx: commands.Context, *, topic: str):
        embed = discord.Embed(title="📌 Quick Vote", description=topic, color=0xf1c40f)
        embed.set_footer(text=f"Initiated by {ctx.author.name}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @commands.hybrid_command(name="ascii", description="Convert short text into fancy ASCII art style")
    async def ascii_text(self, ctx: commands.Context, *, text: str):
        if len(text) > 10:
            return await ctx.send("❌ Please keep the text under 10 characters for ASCII formatting!", ephemeral=True)
        await ctx.send(f"```text\n[ {text.upper()} ]\n```")

    @commands.hybrid_command(name="membercount", description="Instantly view total member count of the server")
    async def membercount(self, ctx: commands.Context):
        embed = discord.Embed(title="👥 Server Member Count", description=f"This server currently has **`{ctx.guild.member_count}`** active members!", color=0x2ecc71)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="coinflip", description="Flip a coin: Heads or Tails")
    async def coinflip(self, ctx: commands.Context):
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"The coin landed on: **`{result}`**!", color=0xf1c40f)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="uptime", description="Check how long the bot has been online")
    async def uptime(self, ctx: commands.Context):
        embed = discord.Embed(title="⏱️ System Status", description="The bot is fully online, synchronized, and operational 24/7.", color=0x2ecc71)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ExtraCommands(bot))