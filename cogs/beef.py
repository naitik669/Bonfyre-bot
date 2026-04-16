import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from storage.db import get_db


class Beef(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="beef", description="Start or resolve a beef — opt-in rivalry system, pure comedy")
    @app_commands.describe(
        action="Start or resolve?",
        member="Who's the beef with?",
        reason="What's the beef about?"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Start beef", value="start"),
        app_commands.Choice(name="Resolve beef", value="resolve"),
        app_commands.Choice(name="Leaderboard", value="leaderboard"),
    ])
    async def beef(
        self,
        interaction: discord.Interaction,
        action: str,
        member: discord.Member = None,
        reason: str = None
    ):
        if action == "start":
            if not member:
                await interaction.response.send_message("You need to pick someone to beef with.", ephemeral=True)
                return
            if member.id == interaction.user.id:
                await interaction.response.send_message("Can't beef with yourself bro 💀", ephemeral=True)
                return

            async with await get_db() as db:
                # Check if beef already exists
                async with db.execute(
                    """SELECT id FROM beef WHERE guild_id = ? AND initiator_id = ? AND target_id = ? AND resolved = 0""",
                    (interaction.guild_id, interaction.user.id, member.id)
                ) as cursor:
                    existing = await cursor.fetchone()
                if existing:
                    await interaction.response.send_message(
                        f"You already have unresolved beef with {member.display_name}.", ephemeral=True
                    )
                    return

                cursor = await db.execute(
                    "INSERT INTO beef (guild_id, initiator_id, target_id, reason) VALUES (?, ?, ?, ?)",
                    (interaction.guild_id, interaction.user.id, member.id, reason or "no reason given")
                )
                await db.commit()
                beef_id = cursor.lastrowid

            beef_channel = discord.utils.get(interaction.guild.text_channels, name="beef-log")

            embed = discord.Embed(
                title="🥩 NEW BEEF ALERT",
                color=discord.Color.red()
            )
            embed.add_field(name="Initiator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Target", value=member.mention, inline=True)
            embed.add_field(name="Reason", value=reason or "no reason given", inline=False)
            embed.add_field(name="Beef ID", value=f"#{beef_id}", inline=True)
            embed.set_footer(text="React 🏆 to vote for winner · React 🤝 to call a truce")

            await interaction.response.send_message(embed=embed)
            msg = await interaction.original_response()
            await msg.add_reaction("🏆")
            await msg.add_reaction("🤝")

            if beef_channel and beef_channel.id != interaction.channel_id:
                await beef_channel.send(embed=embed)

        elif action == "resolve":
            if not member:
                await interaction.response.send_message("Specify who the beef was with.", ephemeral=True)
                return

            async with await get_db() as db:
                async with db.execute(
                    """SELECT id FROM beef WHERE guild_id = ? AND (
                        (initiator_id = ? AND target_id = ?) OR
                        (initiator_id = ? AND target_id = ?)
                    ) AND resolved = 0""",
                    (interaction.guild_id, interaction.user.id, member.id, member.id, interaction.user.id)
                ) as cursor:
                    row = await cursor.fetchone()

                if not row:
                    await interaction.response.send_message(
                        f"No active beef found with {member.display_name}.", ephemeral=True
                    )
                    return

                await db.execute(
                    "UPDATE beef SET resolved = 1 WHERE id = ?", (row[0],)
                )
                await db.commit()

            embed = discord.Embed(
                title="🤝 Beef Resolved",
                description=f"{interaction.user.mention} and {member.mention} squashed it.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        elif action == "leaderboard":
            async with await get_db() as db:
                async with db.execute(
                    """SELECT initiator_id, COUNT(*) as count FROM beef
                       WHERE guild_id = ? GROUP BY initiator_id ORDER BY count DESC LIMIT 10""",
                    (interaction.guild_id,)
                ) as cursor:
                    rows = await cursor.fetchall()

            if not rows:
                await interaction.response.send_message("No beefs recorded yet. Stay peaceful... or don't.", ephemeral=True)
                return

            embed = discord.Embed(title="🥩 Beef Leaderboard", color=discord.Color.red())
            for i, (user_id, count) in enumerate(rows, 1):
                member_obj = interaction.guild.get_member(user_id)
                name = member_obj.display_name if member_obj else f"<@{user_id}>"
                embed.add_field(name=f"#{i} {name}", value=f"{count} beef(s) started", inline=False)
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Beef(bot))
