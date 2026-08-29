import discord
from discord.ext import commands
import time

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.hybrid_command(name="ping", description="Check bot's latency and WS status")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**WebSocket Latency:** `{latency}ms`\n**API Status:** `Operational 🟢`",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bothelp", description="Show main security and bot dashboard")
    async def bothelp(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🛡️ Bot Command Center",
            description="All commands are available via Slash (`/`) and Prefix (`!`).",
            color=0x2b2d31
        )
        embed.add_field(name="🔒 Security", value="`antinuke`, `whitelist`, `unwhitelist`, `whitelisted`, `extraowner`, `serverlockdown`, `serverunlock`, `anti-bot`, `anti-spam`, `anti-link`", inline=False)
        embed.add_field(name="🛠️ Moderation", value="`ban`, `unban`, `kick`, `timeout`, `untimeout`, `purge`, `lock`, `unlock`, `hide`, `unhide`, `slowmode`, `setnick`, `warn`, `warns`, `clearwarns`, `nuke`, `pin`, `unpin`", inline=False)
        embed.add_field(name="👑 Roles", value="`giverole`, `removerole`, `staff`, `vip`, `friend`, `roleall`, `removeroleall`, `inrole`, `rolecolor`, `rolecreate`, `roledelete`", inline=False)
        embed.add_field(name="⚙️ Utility", value="`ping`, `serverinfo`, `userinfo`, `avatar`, `banner`, `servericon`, `serverbanner`, `channelinfo`, `invites`, `emojilist`, `poll`, `membercount`, `say`, `roleinfo`, `uptime`", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", description="Display detailed server information")
    async def serverinfo(self, ctx: commands.Context):
        g = ctx.guild
        embed = discord.Embed(title=f"📊 {g.name} Information", color=0x2b2d31)
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="👑 Owner", value=f"{g.owner.mention} (`{g.owner.id}`)", inline=False)
        embed.add_field(name="👥 Members", value=f"`{g.member_count}` Total", inline=True)
        embed.add_field(name="💬 Channels", value=f"`{len(g.channels)}` Total", inline=True)
        embed.add_field(name="🎭 Roles", value=f"`{len(g.roles)}` Roles", inline=True)
        embed.add_field(name="🚀 Boost Level", value=f"Level `{g.premium_tier}` (`{g.premium_subscription_count}` Boosts)", inline=True)
        embed.add_field(name="📅 Created On", value=g.created_at.strftime("%B %d, %Y"), inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="userinfo", description="Get full profile details of a member")
    async def userinfo(self, ctx: commands.Context, member: discord.Member = None):
        m = member or ctx.author
        embed = discord.Embed(title=f"👤 Profile: {m.name}", color=m.color)
        embed.set_thumbnail(url=m.display_avatar.url)
        embed.add_field(name="🆔 User ID", value=f"`{m.id}`", inline=True)
        embed.add_field(name="🏷️ Nickname", value=m.nick or "None", inline=True)
        embed.add_field(name="🤖 Bot?", value="Yes" if m.bot else "No", inline=True)
        embed.add_field(name="📥 Joined Server", value=m.joined_at.strftime("%Y-%m-%d") if m.joined_at else "Unknown", inline=True)
        embed.add_field(name="🎉 Joined Discord", value=m.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="⭐ Top Role", value=m.top_role.mention, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="avatar", description="Get high-res user avatar")
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        u = user or ctx.author
        embed = discord.Embed(title=f"🖼️ {u.name}'s Avatar", color=0x2b2d31)
        embed.set_image(url=u.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="banner", description="Get user banner")
    async def banner(self, ctx: commands.Context, user: discord.User = None):
        u = await self.bot.fetch_user(user.id if user else ctx.author.id)
        if not u.banner:
            return await ctx.send("❌ This user has no custom banner!", ephemeral=True)
        embed = discord.Embed(title=f"🖼️ {u.name}'s Banner", color=0x2b2d31)
        embed.set_image(url=u.banner.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="servericon", description="Get current server icon")
    async def servericon(self, ctx: commands.Context):
        if not ctx.guild.icon:
            return await ctx.send("❌ Server has no icon!")
        embed = discord.Embed(title=f"🖼️ {ctx.guild.name} Icon", color=0x2b2d31)
        embed.set_image(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverbanner", description="Get current server banner")
    async def serverbanner(self, ctx: commands.Context):
        if not ctx.guild.banner:
            return await ctx.send("❌ Server has no banner image!", ephemeral=True)
        embed = discord.Embed(title=f"🖼️ {ctx.guild.name} Banner", color=0x2b2d31)
        embed.set_image(url=ctx.guild.banner.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="channelinfo", description="Get details of a channel")
    async def channelinfo(self, ctx: commands.Context, channel: discord.TextChannel = None):
        ch = channel or ctx.channel
        embed = discord.Embed(title=f"📺 Channel: #{ch.name}", color=0x2b2d31)
        embed.add_field(name="ID", value=f"`{ch.id}`", inline=True)
        embed.add_field(name="Category", value=ch.category.name if ch.category else "None", inline=True)
        embed.add_field(name="Topic", value=ch.topic or "No topic set", inline=False)
        embed.add_field(name="Created At", value=ch.created_at.strftime("%Y-%m-%d"), inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="membercount", description="Show human vs bot counts")
    async def membercount(self, ctx: commands.Context):
        total = ctx.guild.member_count
        bots = sum(1 for m in ctx.guild.members if m.bot)
        humans = total - bots
        embed = discord.Embed(title="👥 Member Count Breakdown", color=0x2b2d31)
        embed.add_field(name="Total", value=f"`{total}`", inline=True)
        embed.add_field(name="Humans", value=f"`{humans}`", inline=True)
        embed.add_field(name="Bots", value=f"`{bots}`", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="poll", description="Create an interactive poll")
    async def poll(self, ctx: commands.Context, question: str):
        embed = discord.Embed(title="📊 Community Poll", description=question, color=0x2b2d31)
        embed.set_footer(text=f"Poll created by {ctx.author.name}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.hybrid_command(name="uptime", description="Check how long the bot has been online")
    async def uptime(self, ctx: commands.Context):
        delta = int(time.time() - self.start_time)
        hours, remainder = divmod(delta, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed = discord.Embed(
            title="⏰ Bot Uptime",
            description=f"`{days}d {hours}h {minutes}m {seconds}s`",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="say", description="Send a clean embed message via bot")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: commands.Context, *, message: str):
        embed = discord.Embed(description=message, color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="roleinfo", description="Get info about a specific role")
    async def roleinfo(self, ctx: commands.Context, role: discord.Role):
        embed = discord.Embed(title=f"🎭 Role Info: {role.name}", color=role.color)
        embed.add_field(name="ID", value=f"`{role.id}`", inline=True)
        embed.add_field(name="Members", value=f"`{len(role.members)}`", inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
        embed.add_field(name="Created At", value=role.created_at.strftime("%Y-%m-%d"), inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="emojilist", description="List all custom emojis in server")
    async def emojilist(self, ctx: commands.Context):
        emojis = [str(e) for e in ctx.guild.emojis[:30]]
        if not emojis:
            return await ctx.send("❌ No custom emojis found in this server!")
        embed = discord.Embed(
            title=f"😀 Server Emojis ({len(ctx.guild.emojis)})",
            description=" ".join(emojis),
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))