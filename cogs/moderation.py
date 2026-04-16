import discord
from discord.ext import commands
from collections import defaultdict, deque
from datetime import datetime
from config import SPAM_MESSAGE_THRESHOLD, SPAM_TIME_WINDOW_SECONDS


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_history = defaultdict(lambda: deque())
        self.warned_users = set()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        key = (message.guild.id, message.author.id)
        now = datetime.utcnow().timestamp()

        q = self.message_history[key]
        q.append(now)

        # Remove messages outside the time window
        while q and now - q[0] > SPAM_TIME_WINDOW_SECONDS:
            q.popleft()

        if len(q) >= SPAM_MESSAGE_THRESHOLD:
            if key not in self.warned_users:
                self.warned_users.add(key)
                try:
                    await message.channel.send(
                        f"{message.author.mention} slow down — that looks like spam.",
                        delete_after=5
                    )
                except Exception:
                    pass
        else:
            self.warned_users.discard(key)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
