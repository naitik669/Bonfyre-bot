import discord
from discord.ext import commands


class OnJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # Auto-assign default role if it exists
        default_role = discord.utils.get(guild.roles, name="Member")
        if default_role:
            try:
                await member.add_roles(default_role, reason="Auto-assigned on join")
            except discord.Forbidden:
                pass

        # Send welcome DM
        try:
            embed = discord.Embed(
                title=f"Welcome to {guild.name} 👋",
                description=(
                    f"Hey **{member.display_name}**, glad you're here.\n\n"
                    f"Check out **#general** to introduce yourself, or jump into a voice channel.\n"
                    f"Use `/vibe` to get a feel for the server, and `/start` when you want to kick something off.\n\n"
                    f"See you in there."
                ),
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            embed.set_footer(text="Crazie Server Bot · powered by good vibes")
            await member.send(embed=embed)
        except discord.Forbidden:
            pass  # DMs closed, that's fine

        # Welcome message in general
        general = discord.utils.get(guild.text_channels, name="general")
        if general:
            welcome_embed = discord.Embed(
                description=f"**{member.mention}** just pulled up. Say what's good. 👋",
                color=discord.Color.purple()
            )
            await general.send(embed=welcome_embed)


async def setup(bot):
    await bot.add_cog(OnJoin(bot))
