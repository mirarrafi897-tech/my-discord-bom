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
        await interaction.response.send_message("⏳ Ticket will be deleted in 5 seconds...", ephemeral=True)
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
            return await interaction.response.send_message(f"❌ You already have an active ticket: {existing_channel.mention}", ephemeral=True)

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
            description="Please wait for the staff members. They will assist you shortly.\nClick the button below to close this ticket.",
            color=0x3498db
        )
        await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketCloseView())
        await interaction.response.send_message(f"✅ Your ticket has been successfully created: {ticket_channel.mention}", ephemeral=True)


# =====================================================================
# 2. REACTION ROLE BUTTON VIEW (GAMING: MLBB, FF, ROBLOX)
# =====================================================================

class ReactionRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def handle_role(self, interaction: discord.Interaction, role_name: str, emoji: str):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name=role_name)

        if not role:
            return await interaction.response.send_message(f"❌ The role `{role_name}` does not exist in this server! Please create it first.", ephemeral=True)

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"❌ The `{role_name}` role has been removed from you!", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ You have been successfully given the `{role_name}` role!", ephemeral=True)

    @discord.ui.button(label="MLBB", style=discord.ButtonStyle.primary, emoji="🎮", custom_id="role_mlbb")
    async def mlbb_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "MLBB", "🎮")

    @discord.ui.button(label="Free Fire", style=discord.ButtonStyle.success, emoji="🔥", custom_id="role_ff")
    async def ff_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "FF", "🔥")

    @discord.ui.button(label="Roblox", style=discord.ButtonStyle.secondary, emoji="🧱", custom_id="role_roblox")
    async def roblox_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_role(interaction, "ROBLOX", "🧱")


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

        if warn_count >= 3:
            try:
                await member.timeout(discord.utils.utcnow() + datetime.timedelta(hours=1), reason="[AUTO-MOD] Reached 3 warnings")
                await ctx.send(f"🚨 {member.mention} has reached **3 warnings** and has been auto-timed out for 1 hour!")
            except Exception:
                pass

    @commands.hybrid_command(name="warnings", description="Check warnings of a user")
    async def warnings_list(self, ctx: commands.Context, member: discord.Member):
        user_warns = self.warnings.get(member.id, [])
        if not user_warns:
            return await ctx.send(f"✅ {member.mention} has no warnings.")

        reasons = "\n".join([f"{i+1}. {r}" for i, r in enumerate(user_warns)])
        embed = discord.Embed(title=f"⚠️ Warnings for {member.name}", description=reasons, color=0xf1c40f)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="clearwarns", description="Clear all warnings of a user")
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx: commands.Context, member: discord.Member):
        self.warnings.pop(member.id, None)
        await ctx.send(f"✅ All warnings have been cleared for {member.mention}.")

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
            description="If you need any help or want to report an issue, click the **'Create Ticket'** button below.",
            color=0x2ecc71
        )
        await ctx.send(embed=embed, view=TicketSetupView())

    # =====================================================================
    # D. GAMING REACTION ROLE SETUP COMMAND
    # =====================================================================

    @commands.hybrid_command(name="reactionrole-setup", description="Setup Gaming Reaction Role Panel")
    @commands.has_permissions(administrator=True)
    async def reactionrole_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🎮 GAMING - Role Selection Panel",
            description="Click the buttons below to select or remove your favorite gaming roles:\n\n"
                        "🎮 **MLBB** (Mobile Legends)\n"
                        "🔥 **FF** (Free Fire)\n"
                        "🧱 **ROBLOX** (Roblox)\n\n"
                        "*Click the buttons again to toggle the roles off.*",
            color=0x5865f2
        )
        embed.set_footer(text=f"{ctx.guild.name} • Gaming Roles")
        await ctx.send(embed=embed, view=ReactionRoleView())

    # =====================================================================
    # E. GIVEAWAY SYSTEM
    # =====================================================================

    @commands.hybrid_command(name="giveaway", description="Start a quick giveaway")
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx: commands.Context, minutes: int, *, prize: str):
        embed = discord.Embed(
            title="🎉 GIVEAWAY TIME! 🎉",
            description=f"**Prize:** {prize}\n**Hosted by:** {ctx.author.mention}\n\nReact with 🎉 to enter the giveaway!",
            color=0x9b59b6
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        await asyncio.sleep(minutes * 60)

        msg = await ctx.channel.fetch_message(msg.id)
        users = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        users.append(user)

        if users:
            winner = random.choice(users)
            await ctx.send(f"🎊 Congratulations {winner.mention}! You won **{prize}**!")
        else:
            await ctx.send("❌ No one entered the giveaway!")

    # =====================================================================
    # F. CUSTOM TAGS SYSTEM
    # =====================================================================

    @commands.hybrid_command(name="tag", description="Create or view custom tags")
    async def tag(self, ctx: commands.Context, action: str, name: str, *, content: str = None):
        name = name.lower()
        if action.lower() == "add":
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("❌ You do not have permission to create tags!", ephemeral=True)
            if not content:
                return await ctx.send("❌ Please provide content for the tag!", ephemeral=True)
            
            self.custom_tags[name] = content
            await ctx.send(f"✅ Tag **`{name}`** has been successfully created!")

        elif action.lower() in ["get", "show"]:
            if name in self.custom_tags:
                await ctx.send(self.custom_tags[name])
            else:
                await ctx.send(f"❌ No tag found with the name `{name}`!", ephemeral=True)

        elif action.lower() == "remove":
            if not ctx.author.guild_permissions.manage_guild:
                return await ctx.send("❌ Permission denied!", ephemeral=True)
            if name in self.custom_tags:
                del self.custom_tags[name]
                await ctx.send(f"🗑️ Tag `{name}` has been deleted.")
            else:
                await ctx.send("❌ Tag not found.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdvancedFeatures(bot))