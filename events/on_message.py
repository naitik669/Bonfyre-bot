import discord
from discord.ext import commands
from storage.db import get_db
from datetime import datetime


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Log for streak tracking and wrapped stats
        async with await get_db() as db:
            await db.execute(
                "INSERT INTO activity_log (guild_id, user_id, activity_type) VALUES (?, ?, 'message')",
                (message.guild.id, message.author.id)
            )
            await db.commit()

        # Update streak
        streak_cog = self.bot.get_cog("Streak")
        if streak_cog:
            await streak_cog.record_activity(message.guild.id)


async def setup(bot):
    await bot.add_cog(OnMessage(bot))
