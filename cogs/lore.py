import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from storage.db import get_db


class Lore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lore", description="Access the server lore archive — inside jokes, bits, and moments")
    @app_commands.describe(
        action="What to do",
        text="Lore entry text (for 'add')",
        member="Filter lore by member (optional)",
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Random lore entry", value="random"),
        app_commands.Choice(name="Add lore entry", value="add"),
        app_commands.Choice(name="List recent lore", value="list"),
    ])
    async def lore(
        self,
        interaction: discord.Interaction,
        action: str = "random",
        text: str = None,
        member: discord.Member = None
    ):
        if action == "add":
            if not text:
                await interaction.response.send_message("Provide some text with the `text` option.", ephemeral=True)
                return
            async with await get_db() as db:
                await db.execute(
                    "INSERT INTO lore (guild_id, author_id, target_id, content) VALUES (?, ?, ?, ?)",
                    (interaction.guild_id, interaction.user.id, member.id if member else None, text)
                )
                await db.commit()
            embed = discord.Embed(
                title="📖 Lore Added",
                description=text,
                color=discord.Color.purple()
            )
            embed.set_footer(text=f"Logged by {interaction.user.display_name}")
            await interaction.response.send_message(embed=embed)

        elif action == "random":
            async with await get_db() as db:
                if member:
                    async with db.execute(
                        "SELECT content, author_id, created_at FROM lore WHERE guild_id = ? AND target_id = ? ORDER BY RANDOM() LIMIT 1",
                        (interaction.guild_id, member.id)
                    ) as cursor:
                        row = await cursor.fetchone()
                else:
                    async with db.execute(
                        "SELECT content, author_id, created_at FROM lore WHERE guild_id = ? ORDER BY RANDOM() LIMIT 1",
                        (interaction.guild_id,)
                    ) as cursor:
                        row = await cursor.fetchone()

            if not row:
                await interaction.response.send_message(
                    "No lore yet. React 📖 to a message or use `/lore add` to start the archive.", ephemeral=True
                )
                return

            content, author_id, created_at = row
            author = interaction.guild.get_member(author_id)
            embed = discord.Embed(
                title="📖 Server Lore",
                description=content,
                color=discord.Color.purple()
            )
            embed.set_footer(
                text=f"Logged by {author.display_name if author else 'Unknown'} · {created_at[:10] if created_at else ''}"
            )
            await interaction.response.send_message(embed=embed)

        elif action == "list":
            async with await get_db() as db:
                async with db.execute(
                    "SELECT content, author_id, created_at FROM lore WHERE guild_id = ? ORDER BY created_at DESC LIMIT 8",
                    (interaction.guild_id,)
                ) as cursor:
                    rows = await cursor.fetchall()

            if not rows:
                await interaction.response.send_message("No lore entries yet.", ephemeral=True)
                return

            embed = discord.Embed(title="📖 Recent Lore", color=discord.Color.purple())
            for content, author_id, created_at in rows:
                author = interaction.guild.get_member(author_id)
                snippet = (content[:60] + "…") if len(content) > 60 else content
                embed.add_field(
                    name=snippet,
                    value=f"by {author.display_name if author else 'Unknown'} · {created_at[:10] if created_at else ''}",
                    inline=False
                )
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Lore(bot))
