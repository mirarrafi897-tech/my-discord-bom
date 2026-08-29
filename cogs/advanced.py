import discord
from discord.ext import commands
import asyncio
import datetime

# =====================================================================
# 1. TICKET CLOSE VIEW (Persistent View for Closing Tickets)
# =====================================================================

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="royal_close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏳ Ticket will be permanently deleted in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason="[TICKET CLOSED] Support session ended.")
        except Exception:
            pass

# =====================================================================
# 2. TICKET SETUP VIEW (Persistent View for Creating Tickets)
# =====================================================================

class TicketSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.success, emoji="🎫", custom_id="royal_create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="ROYAL SUPPORT TICKETS")
        if not category:
            category = await guild.create_category("ROYAL SUPPORT TICKETS")

        # Check if user already has an active ticket channel
        existing_channel = discord.utils.get(category.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_channel:
            return await interaction.response.send_message(f"❌ You already have an active ticket open: {existing_channel.mention}", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites,
            reason="[TICKET SYSTEM] New support ticket generated."
        )

        embed = discord.Embed(
            title=f"🎫 Support Ticket • {interaction.user.name}",
            description="Welcome! Please describe your issue in detail. Our royal staff team will assist you shortly.\nClick the button below whenever you wish to close this ticket.",
            color=0x3498db
        )
        embed.timestamp = datetime.datetime.utcnow()
        await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketCloseView())
        await interaction.response.send_message(f"✅ Your ticket has been successfully created: {ticket_channel.mention}", ephemeral=True)


# =====================================================================
# 3. GAMING REACTION ROLE VIEW (MLBB, FF, ROBLOX with Toggle Control)
# =====================================================================

class GamingRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def _toggle_role(self, interaction: discord.Interaction, role_name: str, emoji: str):
        guild = interaction.guild
        member = interaction.user
        role = discord.utils.get(guild.roles, name=role_name)

        if not role:
            return await interaction.response.send_message(f"❌ The role `{role_name}` does not exist in this server! Please create it first.", ephemeral=True)

        if role in member.roles:
            await member.remove_roles(role, reason="[REACTION ROLE] User toggled role off.")
            await interaction.response.send_message(f"❌ The **{role_name}** role has been successfully removed from you!", ephemeral=True)
        else:
            await member.add_roles(role, reason="[REACTION ROLE] User toggled role on.")
            await interaction.response.send_message(f"✅ You have been successfully assigned the **{role_name}** role!", ephemeral=True)

    @discord.ui.button(label="MLBB", style=discord.ButtonStyle.primary, emoji="🎮", custom_id="role_mlbb_btn")
    async def mlbb_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "MLBB", "🎮")

    @discord.ui.button(label="Free Fire", style=discord.ButtonStyle.success, emoji="🔥", custom_id="role_ff_btn")
    async def ff_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "FF", "🔥")

    @discord.ui.button(label="Roblox", style=discord.ButtonStyle.secondary, emoji="🧱", custom_id="role_roblox_btn")
    async def roblox_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "ROBLOX", "🧱")


# =====================================================================
# 4. ADVANCED COG (Commands for Setup Panels)
# =====================================================================

class AdvancedFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ticket-setup", description="Deploy the royal support ticket panel")
    @commands.has_permissions(administrator=True)
    async def ticket_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🎫 Royal Support Ticket System",
            description="Need assistance, reporting an issue, or partnering with us? Click the **'Create Ticket'** button below to open a secure, private channel with our staff.",
            color=0x2ecc71
        )
        embed.set_footer(text=f"{ctx.guild.name} • Security & Support Core")
        await ctx.send(embed=embed, view=TicketSetupView())

    @commands.hybrid_command(name="gaming-roles-setup", description="Deploy the Gaming reaction role selection panel")
    @commands.has_permissions(administrator=True)
    async def gaming_roles_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🎮 GAMING - Role Selection Panel",
            description="Click the interactive buttons below to claim or remove your favorite gaming roles instantly!\n\n"
                        "🎮 **MLBB** (Mobile Legends: Bang Bang)\n"
                        "🔥 **FF** (Garena Free Fire)\n"
                        "🧱 **ROBLOX** (Roblox Universe)\n\n"
                        "*Note: Click any button again to toggle/remove the role.*",
            color=0x9b59b6
        )
        embed.set_footer(text=f"{ctx.guild.name} • Gaming Community Roles")
        await ctx.send(embed=embed, view=GamingRoleView())

async def setup(bot):
    await bot.add_cog(AdvancedFeatures(bot))