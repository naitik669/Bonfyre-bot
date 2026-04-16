import discord
from discord import app_commands
from discord.ext import commands


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Initialize a clean, optimized server structure in under 30 seconds")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        await interaction.followup.send("⚙️ Setting up your server... this'll take a moment.", ephemeral=True)

        # Delete existing channels/categories (optional clean slate approach)
        # We'll create the structure without deleting existing content

        # Create roles if they don't exist
        core_role = discord.utils.get(guild.roles, name="Core")
        if not core_role:
            core_role = await guild.create_role(
                name="Core",
                color=discord.Color.purple(),
                reason="CSB Setup"
            )

        # Define overwrites
        default_overwrite = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            core_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        core_only_overwrite = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            core_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        voice_overwrite = {
            guild.default_role: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
            core_role: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True, move_members=True),
        }

        existing_names = [c.name for c in guild.categories]

        # HANGOUT category
        if "Hangout" not in existing_names:
            hangout = await guild.create_category("Hangout", overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=True)
            })
            await guild.create_text_channel("general", category=hangout, overwrites=default_overwrite)
            await guild.create_text_channel("highlights", category=hangout, overwrites=default_overwrite)
            await guild.create_text_channel("beef-log", category=hangout, overwrites=default_overwrite)
            await guild.create_text_channel("status", category=hangout, overwrites=default_overwrite)

        # VOICE category
        if "Voice" not in existing_names:
            voice_cat = await guild.create_category("Voice", overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=True)
            })
            await guild.create_voice_channel("Main VC", category=voice_cat, overwrites=voice_overwrite)
            await guild.create_voice_channel("Chill VC", category=voice_cat, overwrites=voice_overwrite)
            await guild.create_voice_channel("Game VC", category=voice_cat, overwrites=voice_overwrite)

        # CORE (private) category
        if "Core" not in existing_names:
            core_cat = await guild.create_category("Core", overwrites=core_only_overwrite)
            await guild.create_text_channel("core-chat", category=core_cat, overwrites=core_only_overwrite)
            await guild.create_text_channel("announcements", category=core_cat, overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                core_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            })

        # SYSTEM category
        if "System" not in existing_names:
            system_cat = await guild.create_category("System", overwrites=core_only_overwrite)
            await guild.create_text_channel("bot-logs", category=system_cat, overwrites=core_only_overwrite)

        embed = discord.Embed(
            title="✅ Server Setup Complete",
            description="Your Crazie Server is ready to go.",
            color=discord.Color.green()
        )
        embed.add_field(name="Categories Created", value="Hangout · Voice · Core · System", inline=False)
        embed.add_field(name="Roles Created", value="Core (purple) — assign this to your inner circle", inline=False)
        embed.add_field(name="Channels", value="#general · #highlights · #beef-log · #status · VCs · Core channels", inline=False)
        embed.set_footer(text="Run /setup again anytime to add missing channels. Existing ones won't be touched.")

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Setup(bot))
