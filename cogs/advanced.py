import discord
from discord.ext import commands
import asyncio
import datetime
import random
from collections import defaultdict

# =====================================================================
# 1. TICKET SYSTEM DROPDOWN & BUTTON VIEWS
# =====================================================================

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏳ Ticket will be deleted in 5 seconds...")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason="[TICKET CLOSED]")
        except Exception:
            pass

class TicketSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.success, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Support Tickets")
        if not category:
            category = await guild.create_category("Support Tickets")

        # Check if user already has a ticket
        existing_channel = discord.utils.get(category.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_channel:
            return await interaction.response.send_message(f"❌ আপনার ইতোমধ্যে একটি টিকেট খোলা আছে: {existing_channel.mention}", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites,
            reason="[TICKET SYSTEM] Support Ticket Created"
        )

        embed = discord.Embed(
            title=f"🎫 Support Ticket - {interaction.user.name}",
            description="স্টাফদের জন্য অপেক্ষা করুন। তারা শীঘ্রই আপনার সমস্যার সমাধান করবে।\nটিনকেট বন্ধ করতে নিচের বাটনে ক্লিক করুন।",
            color=0x3498db
        )
        await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketCloseView())
        await interaction.response.send_message(f"✅ আপনার টিকেট সফলভাবে তৈরি হয়েছে: {ticket_channel.mention}", ephemeral=True)


# =====================================================================
# 2. REACTION ROLE BUTTON VIEW
# =====================================================================

class ReactionRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔔 Notify Role", style=discord.ButtonStyle.primary, custom_id="role_notify")
    async def notify_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Notification")
        if not role:
            role = await interaction.guild.create_role(name="Notification", color=discord.Color.blue())
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("❌ Notification রোলটি আপনার কাছ থেকে সরিয়ে নেওয়া হয়েছে।", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ আপনাকে Notification রোলটি দেওয়া হয়েছে!", ephemeral=True)

    @discord.ui.button(label="🎮 Gamer Role", style=discord.ButtonStyle.success, custom_id="role_gamer")
    async def gamer_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Gamer")
        if not role:
            role = await interaction.guild.create_role(name="Gamer", color=discord.Color.green())
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("❌ Gamer রোলটি আপনার কাছ থেকে সরিয়ে নেওয়া হয়েছে।", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ আপনাকে Gamer রোলটি দেওয়া হয়েছে!", ephemeral=True)


# =====================================================================
# 3. MAIN ADVANCED COG (WARNINGS, LOGS, GIVEAWAY, TAGS, ETC.)
# =====================================================================

class AdvancedFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = defaultdict(list)  # {user_id: [reasons]}
        self.custom_tags = {}            # {tag_name: content}

    # =====================================================================
    # A. ADVANCED WARNING & STRIKE SYSTEM
    # =====================================================================

    @commands.hybrid_command(name="warn", description="Warn a user for rule violation")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        self.warnings[member.id].append(reason)
        warn_count = len(self.warnings[member.id])

        embed = discord.Embed(
            title="⚠️ User Warned",
            description=f"**User:** {member.mention}\n**Reason:** {reason}\n**Total Warnings:** `{warn_count}`",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)

        # Auto Actions if warnings reach threshold (e.g. 3 warnings = Mute/Timeout)
        if warn_count >= 3:
            try:
                await member.timeout(discord.utils.utcnow() + datetime.timedelta(hours=1), reason="[AUTO-MOD] Reached 3 warnings")
                await ctx.send(f"🚨 {member.mention} has reached **3 warnings** and has been auto-timeout for 1 hour!")
            except Exception:
                pass

    @commands.hybrid_command(name="warnings", description="Check warnings of a user")
    async def warnings_list(self, ctx: commands.Context, member: discord.Member):
        user_warns = self.warnings.get(member.id, [])
        if not user_warns:
            return await ctx.send(f"✅ {member.mention} এর কোনো ওয়ার্নিং নেই।")

        reasons = "\n".join([f"{i+1}. {r}" for i, r in enumerate(user_warns)])
        embed = discord.Embed(title=f"⚠️ Warnings for {member.name}", description=reasons, color=0xf1c40f)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="clearwarns", description="Clear all warnings of a user")
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx: commands.Context, member: discord.Member):
        self.warnings.pop(member.id, None)
        await ctx.send(f"✅ {member.mention} এর সকল ওয়ার্নিং মুছে ফেলা হয়েছে।")

    # =====================================================================
    # B. DETAILED LOGGING SYSTEM
    # =====================================================================

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        log_channel = discord.utils.get(message.guild.text_channels, name="server-logs")
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:** `{message.content}`",
                color=0xe74c3c
            )
            embed.timestamp = datetime.datetime.utcnow()
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        log_channel = discord.utils.get(before.guild.text_channels, name="server-logs")
        if log_channel:
            embed = discord.Embed(
                title="✏️ Message Edited",
                description=f"**Author:** {before.author.mention}\n**Channel:** {before.channel.mention}\n\n**Before:** `{before.content}`\n**After:** `{after.content}`",
                color=0xf39c12
            )
            embed.timestamp = datetime.datetime.utcnow()
            await log_channel.send(embed=embed)

    # =====================================================================
    # C. SUPPORT TICKET COMMAND SETUP
    # =====================================================================

    @commands.hybrid_command(name="ticket-setup", description="Setup Ticket Panel in current channel")
    @commands.has_permissions(administrator=True)
    async def ticket_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🎫 Support Ticket System",
            description="কুনো সাহায্য বা রিপোর্টের প্রয়োজন হলে নিচের **'Create Ticket'** বাটনে ক্লিক করুন।",
            color=0x2ecc71
        )
        await ctx.send(embed=embed, view=TicketSetupView())

    # =====================================================================
    # D. REACTION ROLE SETUP COMMAND
    # =====================================================================

    @commands.hybrid_command(name="reactionrole-setup", description="Setup button-based reaction roles")
    @commands.has_permissions(administrator=True)
    async def reactionrole_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📌 Server Role Selector",
            description="নিচের বাটনগুলো ক্লিক করে আপনার পছন্দের রোল নিতে বা সরাতে পারবেন:",
            color=0x5865f2
        )
        await ctx.send(embed=embed, view=ReactionRoleView())

    # =====================================================================
    # E. GIVEAWAY SYSTEM
    # =====================================================================

    @commands.hybrid_command(name="giveaway", description="Start a quick giveaway")
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx: commands.Context, minutes: int, *, prize: str):
        embed = discord.Embed(
            title="🎉 GIVEAWAY TIME! 🎉",
            description=f"**Prize:** {prize}\n**Hosted by:** {ctx.author.mention}\n\nরিঅ্যাক্ট করতে নিচে ক্লিক করুন বা এই মেসেজে রিঅ্যাক্ট দিন!",
            color=0x9b59b6
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        await asyncio.sleep(minutes * 60)

        # Fetch updated message
        msg = await ctx.channel.fetch_message(msg.id)
        users = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        users.append(user)

        if users:
            winner = random.choice(users)
            await ctx.send(f"🎊 অভিনন্দন {winner.mention}! আপনি জিতেছে **{prize}**!")
        else:
            await ctx.send("❌ কেউ গিভওয়েতে অংশগ্রহণ করেনি!")

    # =====================================================================
    # F. CUSTOM TAGS SYSTEM (LIKE CARL-BOT TAGS)
    # =====================================================================

    @commands.hybrid_command(name="tag", description="Create or view custom tags")
    async def tag(self, ctx: commands.Context, action: str, name: str, *, content: str = None):
        name = name.lower()
        if action.lower() == "add":
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("❌ আপনার ট্যাগ তৈরি করার অনুমতি নেই!", ephemeral=True)
            if not content:
                return await ctx.send("❌ ট্যাগের কন্টেন্ট দিন!", ephemeral=True)
            
            self.custom_tags[name] = content
            await ctx.send(f"✅ ট্যাগ **`{name}`** সফলভাবে তৈরি করা হয়েছে!")

        elif action.lower() in ["get", "show"]:
            if name in self.custom_tags:
                await ctx.send(self.custom_tags[name])
            else:
                await ctx.send(f"❌ `{name}` নামের কোনো ট্যাগ পাওয়া যায়নি!", ephemeral=True)

        elif action.lower() == "remove":
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("❌ অনুমতি নেই!", ephemeral=True)
            if name in self.custom_tags:
                del self.custom_tags[name]
                await ctx.send(f"🗑️ ট্যাগ `{name}` ডিলিট করা হয়েছে।")
            else:
                await ctx.send("❌ ট্যাগটি খুঁজে পাওয়া যায়নি।", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdvancedFeatures(bot))