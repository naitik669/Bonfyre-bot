import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import re
from datetime import datetime, timedelta
from storage.db import get_db


def parse_time(time_str: str) -> int | None:
    """Parse time strings like '30m', '2h', '1h30m' into seconds."""
    pattern = r'(?:(\d+)h)?(?:(\d+)m)?'
    match = re.fullmatch(pattern, time_str.strip().lower())
    if not match or not any(match.groups()):
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    total = hours * 3600 + minutes * 60
    return total if total > 0 else None


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _fire_reminder(self, channel_id: int, user_id: int, message: str, reminder_id: int, delay: float):
        await asyncio.sleep(delay)
        channel = self.bot.get_channel(channel_id)
        if channel:
            user = self.bot.get_user(user_id)
            mention = user.mention if user else f"<@{user_id}>"
            embed = discord.Embed(
                title="⏰ Reminder",
                description=message,
                color=discord.Color.yellow()
            )
            embed.set_footer(text="Set via /remind")
            await channel.send(content=mention, embed=embed)
        async with await get_db() as db:
            await db.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            await db.commit()

    @app_commands.command(name="remind", description="Set a reminder — supports 30m, 2h format")
    @app_commands.describe(time="When to remind you (e.g. 30m, 2h, 1h30m)", message="What to remind you about")
    async def remind(self, interaction: discord.Interaction, time: str, message: str):
        seconds = parse_time(time)
        if seconds is None:
            await interaction.response.send_message(
                "Invalid time format. Use `30m`, `2h`, or `1h30m`.", ephemeral=True
            )
            return

        trigger_at = datetime.utcnow() + timedelta(seconds=seconds)

        async with await get_db() as db:
            cursor = await db.execute(
                "INSERT INTO reminders (guild_id, channel_id, user_id, message, trigger_at) VALUES (?, ?, ?, ?, ?)",
                (interaction.guild_id, interaction.channel_id, interaction.user.id, message, trigger_at)
            )
            await db.commit()
            reminder_id = cursor.lastrowid

        asyncio.create_task(
            self._fire_reminder(interaction.channel_id, interaction.user.id, message, reminder_id, seconds)
        )

        embed = discord.Embed(
            title="✅ Reminder Set",
            description=f"I'll remind you in **{time}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Message", value=message)
        embed.add_field(name="When", value=f"<t:{int(trigger_at.timestamp())}:R>")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="plan", description="Plan a group activity with a reminder")
    @app_commands.describe(time="When (e.g. 30m, 2h)", activity="What's happening?")
    async def plan(self, interaction: discord.Interaction, time: str, activity: str):
        seconds = parse_time(time)
        if seconds is None:
            await interaction.response.send_message(
                "Invalid time format. Use `30m`, `2h`, or `1h30m`.", ephemeral=True
            )
            return

        trigger_at = datetime.utcnow() + timedelta(seconds=seconds)

        async with await get_db() as db:
            cursor = await db.execute(
                "INSERT INTO reminders (guild_id, channel_id, user_id, message, trigger_at) VALUES (?, ?, ?, ?, ?)",
                (interaction.guild_id, interaction.channel_id, interaction.user.id, activity, trigger_at)
            )
            await db.commit()
            reminder_id = cursor.lastrowid

        embed = discord.Embed(
            title="📅 Activity Planned",
            description=f"**{activity}** starts in **{time}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Scheduled by", value=interaction.user.mention)
        embed.add_field(name="When", value=f"<t:{int(trigger_at.timestamp())}:R>")
        embed.set_footer(text="I'll ping here when it's time.")
        await interaction.response.send_message(embed=embed)

        asyncio.create_task(
            self._fire_reminder(interaction.channel_id, interaction.user.id, f"🔔 Time for **{activity}**!", reminder_id, seconds)
        )


async def setup(bot):
    await bot.add_cog(Reminders(bot))
