import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, date
from storage.db import get_db


class Streak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def record_activity(self, guild_id: int):
        """Record activity for streak tracking. Called from on_message and VC events."""
        today = date.today().isoformat()

        async with await get_db() as db:
            async with db.execute(
                "SELECT current_streak, last_active_date, longest_streak FROM streaks WHERE guild_id = ?",
                (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()

            if not row:
                await db.execute(
                    "INSERT INTO streaks (guild_id, current_streak, last_active_date, longest_streak) VALUES (?, 1, ?, 1)",
                    (guild_id, today)
                )
                await db.commit()
                return

            current_streak, last_active_date, longest_streak = row

            if last_active_date == today:
                return  # Already counted today

            yesterday = (datetime.utcnow().replace(hour=0, minute=0, second=0) - __import__('datetime').timedelta(days=1)).date().isoformat()

            if last_active_date == yesterday:
                new_streak = current_streak + 1
            else:
                new_streak = 1  # Streak broken

            new_longest = max(longest_streak, new_streak)

            await db.execute(
                """UPDATE streaks SET current_streak = ?, last_active_date = ?, longest_streak = ?
                   WHERE guild_id = ?""",
                (new_streak, today, new_longest, guild_id)
            )
            await db.commit()

            # Post dramatic announcement if streak breaks
            if last_active_date != yesterday and last_active_date and current_streak > 1:
                guild = self.bot.get_guild(guild_id)
                if guild:
                    channel = discord.utils.get(guild.text_channels, name="general") or \
                              discord.utils.get(guild.text_channels, name="status")
                    if channel:
                        embed = discord.Embed(
                            title="💔 STREAK BROKEN",
                            description=f"The server's {current_streak}-day activity streak just ended. Restart it today.",
                            color=discord.Color.red()
                        )
                        await channel.send(embed=embed)

    @app_commands.command(name="streak", description="Check the server's daily activity streak")
    async def streak(self, interaction: discord.Interaction):
        async with await get_db() as db:
            async with db.execute(
                "SELECT current_streak, last_active_date, longest_streak FROM streaks WHERE guild_id = ?",
                (interaction.guild_id,)
            ) as cursor:
                row = await cursor.fetchone()

        if not row or row[0] == 0:
            await interaction.response.send_message(
                "No streak yet. Send a message or join VC to start one!", ephemeral=True
            )
            return

        current_streak, last_active_date, longest_streak = row
        today = date.today().isoformat()
        is_alive = last_active_date == today

        fire = "🔥" * min(current_streak, 10)
        embed = discord.Embed(
            title="🔥 Server Streak",
            color=discord.Color.orange() if is_alive else discord.Color.greyple()
        )
        embed.add_field(name="Current Streak", value=f"{current_streak} day(s) {fire}", inline=True)
        embed.add_field(name="Best Streak", value=f"{longest_streak} day(s)", inline=True)
        embed.add_field(name="Last Active", value=last_active_date or "Never", inline=True)
        if not is_alive:
            embed.set_footer(text="⚠️ Streak at risk — someone talk or jump in VC!")
        else:
            embed.set_footer(text="Keep it going, don't let it die.")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Streak(bot))
