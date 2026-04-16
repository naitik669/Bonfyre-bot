import discord
from discord import app_commands
from discord.ext import commands
import random
import json
from datetime import datetime
from config import VIBE_MESSAGES, DECIDE_COOLDOWN_SECONDS
from storage.db import get_db


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.decide_cooldowns = {}

    @app_commands.command(name="decide", description="Pick randomly from 2-10 options — no more 20-minute debates")
    @app_commands.describe(
        option1="First option",
        option2="Second option",
        option3="Third option (optional)",
        option4="Fourth option (optional)",
        option5="Fifth option (optional)",
        option6="Sixth option (optional)",
        option7="Seventh option (optional)",
        option8="Eighth option (optional)",
        option9="Ninth option (optional)",
        option10="Tenth option (optional)",
    )
    async def decide(
        self,
        interaction: discord.Interaction,
        option1: str,
        option2: str,
        option3: str = None,
        option4: str = None,
        option5: str = None,
        option6: str = None,
        option7: str = None,
        option8: str = None,
        option9: str = None,
        option10: str = None,
    ):
        # Rate limiting
        user_id = interaction.user.id
        now = datetime.utcnow().timestamp()
        if user_id in self.decide_cooldowns:
            elapsed = now - self.decide_cooldowns[user_id]
            if elapsed < DECIDE_COOLDOWN_SECONDS:
                remaining = int(DECIDE_COOLDOWN_SECONDS - elapsed)
                await interaction.response.send_message(
                    f"⏳ Chill — you can decide again in {remaining}s.", ephemeral=True
                )
                return

        options = [o for o in [option1, option2, option3, option4, option5,
                                option6, option7, option8, option9, option10] if o]
        result = random.choice(options)
        self.decide_cooldowns[user_id] = now

        # Log the decision
        async with await get_db() as db:
            await db.execute(
                "INSERT INTO decide_log (guild_id, options, result, decided_at) VALUES (?, ?, ?, ?)",
                (interaction.guild_id, json.dumps(options), result, datetime.utcnow())
            )
            await db.commit()

        embed = discord.Embed(
            title="🎲 The Bot Has Spoken",
            color=discord.Color.purple()
        )
        embed.add_field(name="Options", value=" · ".join(options), inline=False)
        embed.add_field(name="Decision", value=f"**{result}**", inline=False)
        embed.set_footer(text=f"Decided by {interaction.user.display_name} • No take-backs.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vibe", description="Get a random Crazie vibe check")
    async def vibe(self, interaction: discord.Interaction):
        msg = random.choice(VIBE_MESSAGES)
        embed = discord.Embed(
            description=f"**{msg}**",
            color=discord.Color.og_blurple()
        )
        embed.set_footer(text="Crazie Server Bot · vibe certified")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(message="What should the bot say?")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message("✅ Sent.", ephemeral=True)
        await interaction.channel.send(message)


async def setup(bot):
    await bot.add_cog(Utility(bot))
