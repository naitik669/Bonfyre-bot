import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from config import HIGHLIGHT_STAR_THRESHOLD
from storage.db import get_db


class Highlights(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def post_highlight(self, message: discord.Message):
        """Post a message to #highlights if it hasn't been posted already."""
        async with await get_db() as db:
            async with db.execute(
                "SELECT message_id FROM highlights WHERE message_id = ?", (message.id,)
            ) as cursor:
                existing = await cursor.fetchone()

        if existing:
            return

        highlights_channel = discord.utils.get(message.guild.text_channels, name="highlights")
        if not highlights_channel:
            return

        embed = discord.Embed(
            description=message.content or "*[non-text content]*",
            color=discord.Color.gold(),
            timestamp=message.created_at
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.display_avatar.url
        )
        embed.add_field(name="Source", value=f"[Jump to message]({message.jump_url})", inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        embed.set_footer(text="⭐ Highlight")

        await highlights_channel.send(embed=embed)

        async with await get_db() as db:
            await db.execute(
                """INSERT OR IGNORE INTO highlights
                   (message_id, guild_id, channel_id, author_id, content, jump_url)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (message.id, message.guild.id, message.channel.id,
                 message.author.id, message.content, message.jump_url)
            )
            await db.commit()

    @app_commands.command(name="highlights", description="See recent server highlights")
    async def highlights_cmd(self, interaction: discord.Interaction):
        async with await get_db() as db:
            async with db.execute(
                """SELECT content, jump_url, posted_at FROM highlights
                   WHERE guild_id = ? ORDER BY posted_at DESC LIMIT 5""",
                (interaction.guild_id,)
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message("No highlights yet. React ⭐ to any message to add one!", ephemeral=True)
            return

        embed = discord.Embed(title="⭐ Recent Highlights", color=discord.Color.gold())
        for content, jump_url, posted_at in rows:
            snippet = (content[:80] + "…") if content and len(content) > 80 else (content or "[media]")
            embed.add_field(name=snippet, value=f"[Jump]({jump_url})", inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Highlights(bot))
