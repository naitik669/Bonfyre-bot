import discord
from discord import app_commands
from discord.ext import commands
from storage.db import get_db


class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quote", description="Pull a saved quote from the archive")
    @app_commands.describe(member="Get a quote from a specific person")
    async def quote(self, interaction: discord.Interaction, member: discord.Member = None):
        async with await get_db() as db:
            if member:
                async with db.execute(
                    "SELECT content, author_id, jump_url, created_at FROM quotes WHERE guild_id = ? AND author_id = ? ORDER BY RANDOM() LIMIT 1",
                    (interaction.guild_id, member.id)
                ) as cursor:
                    row = await cursor.fetchone()
            else:
                async with db.execute(
                    "SELECT content, author_id, jump_url, created_at FROM quotes WHERE guild_id = ? ORDER BY RANDOM() LIMIT 1",
                    (interaction.guild_id,)
                ) as cursor:
                    row = await cursor.fetchone()

        if not row:
            msg = f"No quotes saved for {member.display_name} yet." if member else "No quotes saved yet. React 💬 to any message to save one."
            await interaction.response.send_message(msg, ephemeral=True)
            return

        content, author_id, jump_url, created_at = row
        author = interaction.guild.get_member(author_id)

        embed = discord.Embed(
            description=f'"{content}"',
            color=discord.Color.teal()
        )
        embed.set_author(
            name=author.display_name if author else "Unknown",
            icon_url=author.display_avatar.url if author else None
        )
        if jump_url:
            embed.add_field(name="Source", value=f"[Jump to original]({jump_url})")
        embed.set_footer(text=f"Saved · {created_at[:10] if created_at else ''}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quotes", description="List recent saved quotes")
    async def quotes_list(self, interaction: discord.Interaction):
        async with await get_db() as db:
            async with db.execute(
                "SELECT content, author_id, created_at FROM quotes WHERE guild_id = ? ORDER BY created_at DESC LIMIT 8",
                (interaction.guild_id,)
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message("No quotes yet. React 💬 to messages to start the archive.", ephemeral=True)
            return

        embed = discord.Embed(title="💬 Quote Archive", color=discord.Color.teal())
        for content, author_id, created_at in rows:
            author = interaction.guild.get_member(author_id)
            snippet = (content[:60] + "…") if len(content) > 60 else content
            embed.add_field(
                name=f'"{snippet}"',
                value=f"— {author.display_name if author else 'Unknown'}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Quotes(bot))
