import discord
from discord.ext import commands

# --- TEMPORARY VC CONTROL PANEL VIEW ---
class VCControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🔒 Lock", style=discord.ButtonStyle.danger, custom_id="vc_lock")
    async def lock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice and interaction.user.voice.channel
        if not vc:
            return await interaction.response.send_message("❌ আপনি কোনো ভয়েস চ্যানেলে নেই!", ephemeral=True)
        
        await vc.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 আপনার ভয়েস চ্যানেলটি লক করা হয়েছে।", ephemeral=True)

    @discord.ui.button(label="🔓 Unlock", style=discord.ButtonStyle.success, custom_id="vc_unlock")
    async def unlock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice and interaction.user.voice.channel
        if not vc:
            return await interaction.response.send_message("❌ আপনি কোনো ভয়েস চ্যানেলে নেই!", ephemeral=True)
        
        await vc.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("🔓 আপনার ভয়েস চ্যানেলটি আনলক করা হয়েছে।", ephemeral=True)

    @discord.ui.button(label="👻 Hide", style=discord.ButtonStyle.secondary, custom_id="vc_hide")
    async def hide_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice and interaction.user.voice.channel
        if not vc:
            return await interaction.response.send_message("❌ আপনি কোনো ভয়েস চ্যানেলে নেই!", ephemeral=True)
        
        await vc.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.response.send_message("👻 আপনার ভয়েস চ্যানেলটি হাইড করা হয়েছে।", ephemeral=True)

    @discord.ui.button(label="👀 Unhide", style=discord.ButtonStyle.primary, custom_id="vc_unhide")
    async def unhide_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.user.voice and interaction.user.voice.channel
        if not vc:
            return await interaction.response.send_message("❌ আপনি কোনো ভয়েস চ্যানেলে নেই!", ephemeral=True)
        
        await vc.set_permissions(interaction.guild.default_role, view_channel=True)
        await interaction.response.send_message("👀 আপনার ভয়েস চ্যানেলটি দৃশ্যমান করা হয়েছে।", ephemeral=True)


# --- VC SETUP PANEL VIEW ---
class VCSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="➕ Create VC", style=discord.ButtonStyle.success, custom_id="create_user_vc_btn")
    async def create_vc_button(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user

        # Check if user already has a VC
        existing_vc = discord.utils.get(guild.voice_channels, name=f"🔊 {member.name}'s VC")
        if existing_vc:
            if member.voice:
                await member.move_to(existing_vc)
            return await interaction.response.send_message(f"⚠️ আপনার ইতোমধ্যে একটি ভয়েস চ্যানেল খোলা আছে: {existing_vc.mention}", ephemeral=True)

        category = member.voice.channel.category if member.voice and member.voice.channel.category else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
            member: discord.PermissionOverwrite(manage_channels=True, manage_permissions=True, mute_members=True, deafen_members=True, move_members=True)
        }

        try:
            new_vc = await guild.create_voice_channel(
                name=f"🔊 {member.name}'s VC",
                category=category,
                overwrites=overwrites,
                reason="[TEMP VC] User requested custom voice channel"
            )

            if member.voice:
                await member.move_to(new_vc)

            await interaction.response.send_message(f"✅ আপনার ভয়েস চ্যানেল সফলভাবে তৈরি হয়েছে: {new_vc.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ চ্যানেল তৈরি করতে সমস্যা হয়েছে: `{e}`", ephemeral=True)


class TempVoiceManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vc-setup", description="Setup official Join-to-Create Voice Panel")
    @commands.has_permissions(administrator=True)
    async def vc_setup(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🔊 Temporary Voice Generator",
            description="নিচের **'Create VC'** বাটনে ক্লিক করে এক ক্লিকেই আপনার নিজস্ব ব্যক্তিগত ভয়েস চ্যানেল তৈরি করতে পারবেন!\n\n"
                        "• রুম কন্ট্রোল করার জন্য নিচে কন্ট্রোল প্যানেল দেওয়া আছে।",
            color=0x5865f2
        )
        embed.set_footer(text=f"{ctx.guild.name} • Voice Management System")
        
        # Send both Setup Button and Control Panel view
        view = VCSetupView()
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # Auto delete empty custom VCs
        if before.channel and before.channel != after.channel:
            if before.channel.name.endswith("'s VC") and len(before.channel.members) == 0:
                try:
                    await before.channel.delete(reason="[TEMP VC] Empty temporary voice channel cleaned up")
                except Exception:
                    pass

async def setup(bot):
    await bot.add_cog(TempVoiceManager(bot))