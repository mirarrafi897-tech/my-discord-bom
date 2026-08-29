import discord
from discord.ext import commands

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelist = set()
        self.extra_owners = set()
        self.antinuke_enabled = True
        self.antibot_enabled = True
        self.antilink_enabled = False
        self.blacklisted_words = set()

    # --- MAIN SECURITY CONTROLS ---

    @commands.hybrid_command(name="antinuke", description="Turn antinuke system ON or OFF")
    @commands.has_permissions(administrator=True)
    async def antinuke(self, ctx: commands.Context, status: str):
        status = status.lower()
        if status in ["on", "enable", "true"]:
            self.antinuke_enabled = True
            embed = discord.Embed(
                title="🛡️ Antinuke Protection",
                description="Antinuke system is **ENABLED** 🟢\nYour server is protected from unauthorized nuke attempts.",
                color=0x43b581
            )
        elif status in ["off", "disable", "false"]:
            self.antinuke_enabled = False
            embed = discord.Embed(
                title="⚠️ Antinuke Protection",
                description="Antinuke system is **DISABLED** 🔴",
                color=0xff4747
            )
        else:
            embed = discord.Embed(description="❌ Use `on` or `off`.", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="antibot", description="Enable or disable anti-unverified bot join protection")
    @commands.has_permissions(administrator=True)
    async def antibot(self, ctx: commands.Context, status: str):
        status = status.lower()
        if status in ["on", "enable"]:
            self.antibot_enabled = True
            embed = discord.Embed(title="🤖 Anti-Bot Protection", description="Anti-Bot is **ENABLED** 🟢\nUnauthorized bots will be auto-kicked.", color=0x43b581)
        else:
            self.antibot_enabled = False
            embed = discord.Embed(title="🤖 Anti-Bot Protection", description="Anti-Bot is **DISABLED** 🔴", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="antilink", description="Enable or disable anti-invite/link protection")
    @commands.has_permissions(administrator=True)
    async def antilink(self, ctx: commands.Context, status: str):
        status = status.lower()
        if status in ["on", "enable"]:
            self.antilink_enabled = True
            embed = discord.Embed(title="🔗 Anti-Link Protection", description="Anti-Link is **ENABLED** 🟢\nExternal invite links will be removed.", color=0x43b581)
        else:
            self.antilink_enabled = False
            embed = discord.Embed(title="🔗 Anti-Link Protection", description="Anti-Link is **DISABLED** 🔴", color=0xff4747)
        await ctx.send(embed=embed)

    # --- WHITELIST & EXTRA OWNER ---

    @commands.hybrid_command(name="whitelist", description="Add a user to trusted whitelist")
    @commands.has_permissions(administrator=True)
    async def whitelist(self, ctx: commands.Context, user: discord.User):
        self.whitelist.add(user.id)
        embed = discord.Embed(
            title="✅ User Whitelisted",
            description=f"{user.mention} (`{user.id}`) is now trusted.",
            color=0x43b581
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="unwhitelist", description="Remove a user from whitelist")
    @commands.has_permissions(administrator=True)
    async def unwhitelist(self, ctx: commands.Context, user: discord.User):
        if user.id in self.whitelist:
            self.whitelist.remove(user.id)
            embed = discord.Embed(title="❌ Whitelist Removed", description=f"Removed {user.mention} from whitelist.", color=0xff4747)
        else:
            embed = discord.Embed(description="❌ User is not in whitelist!", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="whitelisted", description="View all whitelisted users")
    async def whitelisted(self, ctx: commands.Context):
        if not self.whitelist:
            embed = discord.Embed(title="📜 Whitelisted Users", description="No users whitelisted.", color=0x2b2d31)
        else:
            users = [f"<@{uid}> (`{uid}`)" for uid in self.whitelist]
            embed = discord.Embed(title="📜 Whitelisted Users", description="\n".join(users), color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="extraowner", description="Add an Extra Owner to server bypass list")
    async def extraowner(self, ctx: commands.Context, user: discord.User):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send("❌ Only the Server Owner can use this command!", ephemeral=True)
        self.extra_owners.add(user.id)
        embed = discord.Embed(title="👑 Extra Owner Set", description=f"Granted extra owner rights to {user.mention}", color=0xffaa00)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="extraowners", description="List all extra owners")
    async def extraowners(self, ctx: commands.Context):
        if not self.extra_owners:
            embed = discord.Embed(title="👑 Extra Owners", description="No extra owners added.", color=0x2b2d31)
        else:
            users = [f"<@{uid}> (`{uid}`)" for uid in self.extra_owners]
            embed = discord.Embed(title="👑 Extra Owners", description="\n".join(users), color=0x2b2d31)
        await ctx.send(embed=embed)

    # --- BAD WORDS / BLACKLIST COMMANDS ---

    @commands.hybrid_command(name="addbadword", description="Add a forbidden word to automod filter")
    @commands.has_permissions(administrator=True)
    async def addbadword(self, ctx: commands.Context, word: str):
        self.blacklisted_words.add(word.lower())
        embed = discord.Embed(title="🚫 Word Filter Updated", description=f"Added `{word}` to bad words list.", color=0x43b581)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="removebadword", description="Remove a word from bad words list")
    @commands.has_permissions(administrator=True)
    async def removebadword(self, ctx: commands.Context, word: str):
        if word.lower() in self.blacklisted_words:
            self.blacklisted_words.remove(word.lower())
            embed = discord.Embed(title="🧹 Word Removed", description=f"Removed `{word}` from filter.", color=0x43b581)
        else:
            embed = discord.Embed(description="❌ Word not found in filter list!", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="badwords", description="Show all blacklisted words")
    @commands.has_permissions(manage_messages=True)
    async def badwords(self, ctx: commands.Context):
        if not self.blacklisted_words:
            embed = discord.Embed(title="📜 Bad Words List", description="No forbidden words set.", color=0x2b2d31)
        else:
            embed = discord.Embed(title="📜 Bad Words List", description=", ".join([f"`{w}`" for w in self.blacklisted_words]), color=0x2b2d31)
        await ctx.send(embed=embed)

    # --- LOCKDOWN CONTROLS ---

    @commands.hybrid_command(name="serverlockdown", description="Emergency lockdown all text channels")
    @commands.has_permissions(administrator=True)
    async def serverlockdown(self, ctx: commands.Context):
        await ctx.send("🚨 **Initiating Full Server Lockdown...**")
        count = 0
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                count += 1
            except Exception:
                continue
        embed = discord.Embed(title="🔒 Server Lockdown Complete", description=f"Locked `{count}` text channels.", color=0xff4747)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverunlock", description="Unlock all text channels after lockdown")
    @commands.has_permissions(administrator=True)
    async def serverunlock(self, ctx: commands.Context):
        await ctx.send("🔓 **Unlocking Channels...**")
        count = 0
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                count += 1
            except Exception:
                continue
        embed = discord.Embed(title="🔓 Server Unlocked", description=f"Restored message access in `{count}` channels.", color=0x43b581)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="securityconfig", description="View current security configurations")
    async def securityconfig(self, ctx: commands.Context):
        embed = discord.Embed(title="⚙️ Security Configuration", color=0x2b2d31)
        embed.add_field(name="Antinuke", value="`ENABLED` 🟢" if self.antinuke_enabled else "`DISABLED` 🔴", inline=True)
        embed.add_field(name="Anti-Bot", value="`ENABLED` 🟢" if self.antibot_enabled else "`DISABLED` 🔴", inline=True)
        embed.add_field(name="Anti-Link", value="`ENABLED` 🟢" if self.antilink_enabled else "`DISABLED` 🔴", inline=True)
        embed.add_field(name="Whitelisted Users", value=f"`{len(self.whitelist)}` users", inline=True)
        embed.add_field(name="Bad Words Filtered", value=f"`{len(self.blacklisted_words)}` words", inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Security(bot))