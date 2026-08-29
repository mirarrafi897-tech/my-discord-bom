import discord
from discord.ext import commands
import random
import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageOps
from collections import defaultdict

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Level System DB (In-Memory Data Store)
        self.user_xp = defaultdict(int)
        self.user_level = defaultdict(int)
        
        # Truth or Dare Data List
        self.truths = [
            "আপনার জীবনে সবচেয়ে লজ্জাজনক ঘটনা কী?",
            "কাউকে কি গোপনভাবে পছন্দ করেন? নাম বলুন!",
            "আপনার জীবনের সবচেয়ে বড় মিথ্যা কথাটি কী ছিল?",
            "আপনার অ্যাকাউন্টে কত টাকা আছে?",
            "ডিসকর্ডে আপনার কার ওপর ক্রাশ আছে?"
        ]
        self.dares = [
            "সার্ভারের যে কাউকে ডেকে একটি রোমান্টিক ডায়ালগ বলুন!",
            "পরবর্তী ৫ মিনিট সব মেসেজ শুধু ইমোজি দিয়ে লিখুন।",
            "আপনার ফোনের শেষ স্ক্রিনশটটি চ্যাটে শেয়ার করুন।",
            "১০ সেকেন্ডের একটি ভয়েস মেসেজ পাঠিয়ে গান গাওয়ান!",
            "অ্যাডমিনকে গিয়ে বলুন 'আই লাভ ইউ'।"
        ]

    # =====================================================================
    # 1. AUTOMATIC EVENTS: LEVEL SYSTEM, WELCOME, LEAVE & BOOST LOGIC
    # =====================================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Simple XP System Engine
        uid = message.author.id
        self.user_xp[uid] += random.randint(10, 20)
        current_xp = self.user_xp[uid]
        current_lvl = self.user_level[uid]
        next_lvl_xp = (current_lvl + 1) * 100

        if current_xp >= next_lvl_xp:
            self.user_level[uid] += 1
            embed = discord.Embed(
                title="🎉 LEVEL UP!",
                description=f"অভিনন্দন {message.author.mention}! আপনি **Level {self.user_level[uid]}** এ পৌঁছেছেন! 🚀",
                color=0xf1c40f
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            await message.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = discord.utils.get(member.guild.text_channels, name="welcome") or member.guild.system_channel
        if channel:
            embed = discord.Embed(
                title=f"👋 Welcome to {member.guild.name}!",
                description=f"হ্যালো {member.mention}, আমাদের সার্ভারে আপনাকে স্বাগতম! 💖\n"
                            f"সর্বমোট মেম্বার: **{member.guild.member_count}**",
                color=0x2ecc71
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"User ID: {member.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = discord.utils.get(member.guild.text_channels, name="goodbye") or member.guild.system_channel
        if channel:
            embed = discord.Embed(
                title="👋 Goodbye!",
                description=f"**{member.name}** সার্ভার ছেড়ে চলে গেছেন। 😢",
                color=0xe74c3c
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

    # =====================================================================
    # 2. FUN & GAME COMMANDS (TRUTH/DARE, SHIP, IMAGE HUG)
    # =====================================================================

    @commands.hybrid_command(name="truth", description="Truth question for truth or dare game")
    async def truth(self, ctx: commands.Context):
        question = random.choice(self.truths)
        embed = discord.Embed(title="❓ Truth Question", description=f"{ctx.author.mention}, {question}", color=0x3498db)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="dare", description="Dare task for truth or dare game")
    async def dare(self, ctx: commands.Context):
        task = random.choice(self.dares)
        embed = discord.Embed(title="🔥 Dare Challenge", description=f"{ctx.author.mention}, {task}", color=0xe67e22)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ship", description="Check love match percentage between two users")
    async def ship(self, ctx: commands.Context, user1: discord.Member, user2: discord.Member = None):
        if not user2:
            user2 = ctx.author

        percentage = random.randint(0, 100)
        status = "💔 বিচ্ছেদ নিশ্চিত!" if percentage < 30 else "💖 মোটামুটি জমেবে!" if percentage < 70 else "💍 সোজা বিয়ের পিঁড়িতে!"

        embed = discord.Embed(title="❤️ Love Match Calculator", color=0xe91e63)
        embed.add_field(name="Lovers", value=f"{user1.mention} + {user2.mention}", inline=False)
        embed.add_field(name="Match Score", value=f"**{percentage}%** \n`[{'█' * (percentage // 10)}{'░' * (10 - percentage // 10)}]`", inline=False)
        embed.add_field(name="Verdict", value=status, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="hug", description="Hug a user with generated custom card")
    async def hug(self, ctx: commands.Context, member: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get(ctx.author.display_avatar.url) as resp1, session.get(member.display_avatar.url) as resp2:
                img1_data = await resp1.read()
                img2_data = await resp2.read()

        base = Image.new("RGBA", (500, 200), (44, 47, 51, 255))
        u1_img = Image.open(io.BytesIO(img1_data)).resize((120, 120))
        u2_img = Image.open(io.BytesIO(img2_data)).resize((120, 120))

        base.paste(u1_img, (40, 40))
        base.paste(u2_img, (340, 40))

        draw = ImageDraw.Draw(base)
        draw.text((220, 80), "🤗 HUG 🤗", fill=(255, 255, 255))

        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename="hug.png")
        embed = discord.Embed(
            title="🤗 Warm Hug!",
            description=f"**{ctx.author.name}** nicely hugged **{member.name}**!",
            color=0x9b59b6
        )
        embed.set_image(url="attachment://hug.png")
        await ctx.send(embed=file, embed=embed)

    @commands.hybrid_command(name="rank", description="Check your current level and XP")
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        lvl = self.user_level[member.id]
        xp = self.user_xp[member.id]

        embed = discord.Embed(title=f"📊 Rank Card - {member.name}", color=0x1abc9c)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Level", value=f"**{lvl}**", inline=True)
        embed.add_field(name="XP Points", value=f"**{xp}** / {(lvl + 1) * 100}", inline=True)
        await ctx.send(embed=embed)

    # =====================================================================
    # 3. ADVANCED MODERATION & CHANNEL/VC MANAGEMENT
    # =====================================================================

    @commands.hybrid_command(name="lock", description="Lock current text channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(title="🔒 Channel Locked", description="এই টেক্সট চ্যানেলটি মেম্বারদের মেসেজ দেওয়ার জন্য লক করা হয়েছে।", color=0xe74c3c)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unlock", description="Unlock current text channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(title="🔓 Channel Unlocked", description="টেক্সট চ্যানেলটি পুনরায় আনলক করা হয়েছে।", color=0x2ecc71)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="lockvc", description="Lock your current VC to prevent anyone joining")
    @commands.has_permissions(manage_channels=True)
    async def lockvc(self, ctx: commands.Context):
        if not ctx.author.voice:
            return await ctx.send("❌ আপনি কোনো ভয়েস চ্যানেলে জয়েন নেই!")
        
        vc = ctx.author.voice.channel
        await vc.set_permissions(ctx.guild.default_role, connect=False)
        await ctx.send(f"🔒 **{vc.name}** জয়েন করার জন্য লক করা হয়েছে।")

    @commands.hybrid_command(name="unlockvc", description="Unlock your current VC")
    @commands.has_permissions(manage_channels=True)
    async def unlockvc(self, ctx: commands.Context):
        if not ctx.author.voice:
            return await ctx.send("❌ আপনি কোনো ভয়েস চ্যানেলে জয়েন নেই!")

        vc = ctx.author.voice.channel
        await vc.set_permissions(ctx.guild.default_role, connect=True)
        await ctx.send(f"🔓 **{vc.name}** আনলক করা হয়েছে।")

    @commands.hybrid_command(name="muteall", description="Server Mute all members in your current VC")
    @commands.has_permissions(mute_members=True)
    async def muteall(self, ctx: commands.Context):
        if not ctx.author.voice:
            return await ctx.send("❌ আপনি কোনো ভয়েস চ্যানেলে জয়েন নেই!")

        vc = ctx.author.voice.channel
        for member in vc.members:
            if member != ctx.author and not member.bot:
                try:
                    await member.edit(mute=True)
                except Exception:
                    pass

        await ctx.send(f"🔇 **{vc.name}** চ্যানেলের সবাইকেServer Mute করা হয়েছে।")

    @commands.hybrid_command(name="unmuteall", description="Server Unmute all members in your current VC")
    @commands.has_permissions(mute_members=True)
    async def unmuteall(self, ctx: commands.Context):
        if not ctx.author.voice:
            return await ctx.send("❌ আপনি কোনো ভয়েস চ্যানেলে জয়েন নেই!")

        vc = ctx.author.voice.channel
        for member in vc.members:
            if not member.bot:
                try:
                    await member.edit(mute=False)
                except Exception:
                    pass

        await ctx.send(f"🔊 **{vc.name}** চ্যানেলের সবার Mute তুলে নেওয়া হয়েছে।")

async def setup(bot):
    await bot.add_cog(Utility(bot))