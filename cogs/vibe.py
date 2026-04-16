import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from storage.db import get_db


class VibeCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vibecheck", description="Rate the group's energy today — anonymous 1-5 poll")
    @app_commands.describe(score="Your vibe score from 1 (dead) to 5 (peak)")
    async def vibecheck(self, interaction: discord.Interaction, score: int):
        if score < 1 or score > 5:
            await interaction.response.send_message("Score must be 1–5.", ephemeral=True)
            return

        today = datetime.utcnow().date().isoformat()

        async with await get_db() as db:
            # Check if already voted today
            async with db.execute(
                """SELECT id FROM vibe_checks
                   WHERE guild_id = ? AND user_id = ? AND DATE(created_at) = ?""",
                (interaction.guild_id, interaction.user.id, today)
            ) as cursor:
                existing = await cursor.fetchone()

            if existing:
                await interaction.response.send_message(
                    "You already submitted a vibe check today. Come back tomorrow.", ephemeral=True
                )
                return

            await db.execute(
                "INSERT INTO vibe_checks (guild_id, user_id, score) VALUES (?, ?, ?)",
                (interaction.guild_id, interaction.user.id, score)
            )
            await db.commit()

            # Get today's average
            async with db.execute(
                """SELECT AVG(score), COUNT(*) FROM vibe_checks
                   WHERE guild_id = ? AND DATE(created_at) = ?""",
                (interaction.guild_id, today)
            ) as cursor:
                avg_score, count = await cursor.fetchone()

        bars = "█" * score + "░" * (5 - score)
        avg_display = f"{avg_score:.1f}" if avg_score else "N/A"

        embed = discord.Embed(
            title="📊 Vibe Check Submitted",
            color=discord.Color.purple()
        )
        embed.add_field(name="Your Score", value=f"{bars} ({score}/5)", inline=False)
        embed.add_field(name="Server Average Today", value=f"{avg_display}/5 ({count} responses)", inline=False)
        embed.set_footer(text="Anonymous · results are aggregate only")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="vibereport", description="See the weekly vibe report")
    async def vibereport(self, interaction: discord.Interaction):
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

        async with await get_db() as db:
            async with db.execute(
                """SELECT DATE(created_at) as day, AVG(score) as avg, COUNT(*) as cnt
                   FROM vibe_checks WHERE guild_id = ? AND created_at >= ?
                   GROUP BY day ORDER BY day""",
                (interaction.guild_id, week_ago)
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message(
                "No vibe data for the past week. Use `/vibecheck` to start tracking.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📈 Weekly Vibe Report",
            color=discord.Color.purple()
        )

        for day, avg, cnt in rows:
            bars = "█" * round(avg) + "░" * (5 - round(avg))
            embed.add_field(
                name=day,
                value=f"{bars} {avg:.1f}/5 ({cnt} votes)",
                inline=False
            )

        overall_avg = sum(r[1] for r in rows) / len(rows)
        embed.set_footer(text=f"7-day average: {overall_avg:.1f}/5")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(VibeCheck(bot))
