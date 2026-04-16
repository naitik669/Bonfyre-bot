import discord
from discord.ext import commands
import asyncio
import os
import sys
from dotenv import load_dotenv
from storage.db import init_db

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    print("ERROR: DISCORD_TOKEN not set. Please add it to your environment secrets.")
    sys.exit(1)

COGS = [
    "cogs.setup",
    "cogs.utility",
    "cogs.voice",
    "cogs.fun",
    "cogs.reminders",
    "cogs.highlights",
    "cogs.lore",
    "cogs.quotes",
    "cogs.beef",
    "cogs.wrapped",
    "cogs.streak",
    "cogs.vibe",
    "cogs.moderation",
    "cogs.clutch",
    "events.on_join",
    "events.on_message",
    "events.reactions",
]


class CrazieBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True   # Privileged — enable in Dev Portal
        intents.members = True           # Privileged — enable in Dev Portal
        intents.presences = True         # Privileged — enable in Dev Portal (for clutch mode online status)
        intents.reactions = True
        intents.voice_states = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        await init_db()
        for cog in COGS:
            try:
                await self.load_extension(cog)
                print(f"  ✓ Loaded {cog}")
            except Exception as e:
                print(f"  ✗ Failed to load {cog}: {e}")
        await self.tree.sync()
        print("Slash commands synced globally.")

    async def on_ready(self):
        print(f"\n{'='*40}")
        print(f"  Crazie Server Bot is online!")
        print(f"  Logged in as {self.user} ({self.user.id})")
        print(f"  Serving {len(self.guilds)} guild(s)")
        print(f"{'='*40}\n")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="the server 👀"
            )
        )


async def main():
    bot = CrazieBot()
    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
