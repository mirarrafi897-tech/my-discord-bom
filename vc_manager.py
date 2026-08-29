import discord
from discord.ext import commands

# =====================================================================
# 1. VC CONTROL VIEW (Interactive Buttons for Personal Voice Rooms)
# =====================================================================

class VCControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="vc_lock_btn")
    async def lock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice and interaction.user.voice.channel
        if not vc:
            return await interaction.response.send_message("❌ You are not in a voice channel!", ephemeral=True)

        await vc.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 Your voice channel has been **locked**.", ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.success, emoji="🔓", custom_id="vc_unlock_btn")
    async def unlock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice and interaction.user.voice.channel
        if not vc:
            return await interaction.response.send_message("❌ You are not in a voice channel!", ephemeral=True)

        await vc.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("🔓 Your voice channel has been **unlocked**.", ephemeral=True)

    @discord.ui.button(label="Hide", style=discord.ButtonStyle.secondary, emoji="🙈", custom_id="vc_hide_btn")
    async def hide_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice and interaction.user.voice.channel
        if not vc:
            return await interaction.response.send_message("❌ You are not in a voice channel!", ephemeral=True)

        await vc.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.response.send_message("🙈 Your voice channel has been **hidden**.", ephemeral=True)

    @discord.ui.button(label="Unhide", style=discord.ButtonStyle.primary, emoji="👁️", custom_id="vc_unhide_btn")
    async def unhide_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice and interaction.user.voice.channel
        if not vc:
            return await interaction.response.send_message("❌ You are not in a voice channel!", ephemeral=True)

        await vc.set_permissions(interaction.guild.default_role, view_channel=True)
        await interaction.response.send_message("👁️ Your voice channel is now **visible**.", ephemeral=True)


# =====================================================================
# 2. VC SETUP VIEW (Join-to-Create Trigger Panel)
# =====================================================================

class VCSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Setup Voice Control Panel", style=discord.ButtonStyle.primary, emoji="🔊", custom_id="vc_setup_panel_btn")
    async def setup_panel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ You need Manage Channels permission to deploy this panel!", ephemeral=True)

        embed = discord.Embed(
            title="🔊 Royal Voice Control Panel",
            description="Use the buttons below to manage your temporary voice channel directly while connected to your room.",
            color=0x3498db
        )
        embed.set_footer(text=f"{interaction.guild.name} • Voice Manager")
        await interaction.channel.send(embed=embed, view=VCControlView(interaction.client))
        await interaction.response.send_message("✅ Voice Control Panel deployed successfully!", ephemeral=True)


# =====================================================================
# 3. VC MANAGER COG (Join-to-Create Logic & Setup Commands)
# =====================================================================

class VCManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = {} # {channel_id: owner_id}

    @commands.hybrid_command(name="vc-setup", description="Deploy the Join-to-Create Voice system and control panel")
    @commands.has_permissions(administrator=True)
    async def vc_setup(self, ctx: commands.Context):
        guild = ctx.guild

        # Create category and join-to-create channel if not present
        category = discord.utils.get(guild.categories, name="ROYAL VOICE CHANNELS")
        if not category:
            category = await guild.create_category("ROYAL VOICE CHANNELS")

        existing_trigger = discord.utils.get(category.voice_channels, name="➕ Create Voice")
        if not existing_trigger:
            await guild.create_voice_channel("➕ Create Voice", category=category)

        embed = discord.Embed(
            title="🔊 Join-to-Create Voice System Setup",
            description="The Voice Manager has been successfully configured!\n\n"
                        "• **Trigger Channel:** `➕ Create Voice`\n"
                        "• Join the trigger channel to automatically create your personal voice room.",
            color=0x2ecc71
        )
        await ctx.send(embed=embed, view=VCSetupView())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        # User joined the "Create Voice" channel
        if after.channel and after.channel.name == "➕ Create Voice":
            category = after.channel.category
            new_channel_name = f"🔊 {member.name}'s Room"

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
                member: discord.PermissionOverwrite(manage_channels=True, connect=True, move_members=True)
            }

            try:
                new_vc = await guild.create_voice_channel(
                    name=new_channel_name,
                    category=category,
                    overwrites=overwrites,
                    reason="[VC MANAGER] User triggered Join-to-Create room."
                )
                self.active_channels[new_vc.id] = member.id
                await member.move_to(new_vc)
            except Exception:
                pass

        # Check if empty temporary channels need to be deleted
        if before.channel and before.channel.id in self.active_channels:
            if len(before.channel.members) == 0:
                try:
                    owner_id = self.active_channels.pop(before.channel.id, None)
                    await before.channel.delete(reason="[VC MANAGER] Temporary voice channel empty.")
                except Exception:
                    pass

async def setup(bot):
    await bot.add_cog(VCManager(bot))