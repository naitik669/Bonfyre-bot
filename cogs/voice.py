import discord
from discord import app_commands
from discord.ext import commands


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_core_or_owner(self, interaction: discord.Interaction) -> bool:
        core_role = discord.utils.get(interaction.guild.roles, name="Core")
        if interaction.user == interaction.guild.owner:
            return True
        if core_role and core_role in interaction.user.roles:
            return True
        return False

    @app_commands.command(name="lockvc", description="Lock all voice channels — Core/Owner only")
    async def lockvc(self, interaction: discord.Interaction):
        if not self.is_core_or_owner(interaction):
            await interaction.response.send_message("🔒 Only Core members or the Owner can do that.", ephemeral=True)
            return

        locked = []
        for channel in interaction.guild.voice_channels:
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            locked.append(channel.name)

        embed = discord.Embed(
            title="🔒 Voice Channels Locked",
            description=f"Locked: {', '.join(locked)}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Locked by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unlockvc", description="Unlock all voice channels — Core/Owner only")
    async def unlockvc(self, interaction: discord.Interaction):
        if not self.is_core_or_owner(interaction):
            await interaction.response.send_message("🔓 Only Core members or the Owner can do that.", ephemeral=True)
            return

        unlocked = []
        for channel in interaction.guild.voice_channels:
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            unlocked.append(channel.name)

        embed = discord.Embed(
            title="🔓 Voice Channels Unlocked",
            description=f"Unlocked: {', '.join(unlocked)}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Unlocked by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="limitvc", description="Set a member limit on a voice channel — Core/Owner only")
    @app_commands.describe(limit="Member limit (0 = no limit)", channel="Which VC to limit (defaults to your current VC)")
    async def limitvc(self, interaction: discord.Interaction, limit: int, channel: discord.VoiceChannel = None):
        if not self.is_core_or_owner(interaction):
            await interaction.response.send_message("Only Core members or the Owner can do that.", ephemeral=True)
            return

        target = channel
        if not target:
            if interaction.user.voice and interaction.user.voice.channel:
                target = interaction.user.voice.channel
            else:
                await interaction.response.send_message("You're not in a VC. Specify a channel or join one.", ephemeral=True)
                return

        if limit < 0 or limit > 99:
            await interaction.response.send_message("Limit must be 0–99 (0 = unlimited).", ephemeral=True)
            return

        await target.edit(user_limit=limit)
        desc = f"No limit" if limit == 0 else f"{limit} members max"
        embed = discord.Embed(
            title="🎚️ VC Limit Updated",
            description=f"**{target.name}** → {desc}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Set by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Voice(bot))
