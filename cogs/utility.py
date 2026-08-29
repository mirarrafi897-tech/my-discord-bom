import discord
from discord.ext import commands
import random
import datetime

class UtilityAndFun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_levels = {} # {user_id: {"xp": int, "level": int}}
        self.custom_tags = {} # {tag_name: content}

    # =====================================================================
    # 1. LEVEL & XP SYSTEM (Listener & Commands)
    # =====================================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        if user_id not in self.user_levels:
            self.user_levels[user_id] = {"xp": 0, "level": 1}

        # Add random XP per message (between 15 to 25)
        xp_gain = random.randint(15, 25)
        self.user_levels[user_id]["xp"] += xp_gain

        current_xp = self.user_levels[user_id]["xp"]
        current_level = self.user_levels[user_id]["level"]
        
        # Level up threshold calculation (Level * 100 XP)
        next_level_xp = current_level * 100

        if current_xp >= next_level_xp:
            self.user_levels[user_id]["level"] += 1
            self.user_levels[user_id]["xp"] = 0 # Reset XP for next level
            
            try:
                embed = discord.Embed(
                    title="🎉 LEVEL UP!",
                    description=f"Congratulations {message.author.mention}! You have leveled up to **Level {current_level + 1}**!",
                    color=0xf1c40f
                )
                await message.channel.send(embed=embed)
            except Exception:
                pass

    @commands.hybrid_command(name="rank", description="Check your current level and XP")
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        data = self.user_levels.get(target.id, {"xp": 0, "level": 1})
        
        embed = discord.Embed(
            title=f"👑 Rank Card • {target.name}",
            description=f"**Level:** `{data['level']}`\n**Current XP:** `{data['xp']} / {data['level'] * 100}`",
            color=0x3498db
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    # =====================================================================
    # 2. CUSTOM TAGS SYSTEM (Bidirectional: Add, Show, Remove)
    # =====================================================================

    @commands.hybrid_command(name="tag", description="Create, view or delete custom server tags")
    async def tag(self, ctx: commands.Context, action: str, name: str, *, content: str = None):
        action = action.lower()
        name = name.lower()

        if action == "add":
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("❌ You do not have permission to create tags!", ephemeral=True)
            if not content:
                return await ctx.send("❌ Please provide content for the tag!", ephemeral=True)
            
            self.custom_tags[name] = content
            await ctx.send(f"✅ Tag **`{name}`** has been successfully created!")

        elif action in ["get", "show"]:
            if name in self.custom_tags:
                await ctx.send(self.custom_tags[name])
            else:
                await ctx.send(f"❌ No tag found with the name `{name}`!", ephemeral=True)

        elif action in ["remove", "delete"]:
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("❌ You do not have permission to delete tags!", ephemeral=True)
            if name in self.custom_tags:
                del self.custom_tags[name]
                await ctx.send(f"🗑️ Tag **`{name}`** has been successfully deleted.")
            else:
                await ctx.send(f"❌ Tag `{name}` does not exist.", ephemeral=True)
        else:
            await ctx.send("❌ Invalid action! Use `tag add`, `tag show`, or `tag remove`.", ephemeral=True)

    # =====================================================================
    # 3. FUN COMMANDS (Truth, Dare, Ship, Coinflip, Roll)
    # =====================================================================

    @commands.hybrid_command(name="truth", description="Get a random truth question")
    async def truth(self, ctx: commands.Context):
        questions = [
            "What is your most embarrassing moment?",
            "What is a secret you’ve never told anyone?",
            "If you could switch lives with someone for a day, who would it be?",
            "What is your biggest pet peeve?",
            "What was your most awkward date?"
        ]
        embed = discord.Embed(title="🤔 Truth Question", description=random.choice(questions), color=0x9b59b6)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="dare", description="Get a random dare challenge")
    async def dare(self, ctx: commands.Context):
        dares = [
            "Send the last photo in your camera roll.",
            "Speak in an accent for the next 10 minutes in voice chat.",
            "Type your entire keyboard layout using only your nose.",
            "Compliment the person above you in the chat.",
            "Change your nickname to something funny chosen by the chat."
        ]
        embed = discord.Embed(title="🔥 Dare Challenge", description=random.choice(dares), color=0xe74c3c)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ship", description="Calculate love compatibility between two users")
    async def ship(self, ctx: commands.Context, member1: discord.Member, member2: discord.Member = None):
        target = member2 or ctx.author
        score = random.randint(0, 100)
        
        # Emoji bar based on score
        hearts = "❤️" * (score // 10) + "🖤" * (10 - (score // 10))
        
        embed = discord.Embed(
            title="💖 Love Calculator",
            description=f"**{member1.mention}** ❤️ **{target.mention}**\n\nCompatibility Score: **`{score}%`**\n{hearts}",
            color=0xe91e63
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="coinflip", description="Flip a coin (Heads or Tails)")
    async def coinflip(self, ctx: commands.Context):
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"The coin landed on: **{result}**!", color=0xf1c40f)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="roll", description="Roll a dice between 1 and 6")
    async def roll(self, ctx: commands.Context):
        result = random.randint(1, 6)
        embed = discord.Embed(title="🎲 Dice Roll", description=f"You rolled a: **{result}**!", color=0x2ecc71)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilityAndFun(bot))