import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import asyncio
from datetime import datetime, timedelta
from config import ROAST_MESSAGES, ROAST_COOLDOWN_SECONDS
from storage.db import get_db


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roast_cooldowns = {}
        self.active_lobbies = {}

    @app_commands.command(name="start", description="Kick off a session — kills the 'who's gonna initiate' paralysis")
    @app_commands.describe(
        activity="Type of activity (game night, movie night, chill, or custom)",
        ping="Ping @here to notify everyone?"
    )
    @app_commands.choices(activity=[
        app_commands.Choice(name="Game Night 🎮", value="game night"),
        app_commands.Choice(name="Movie Night 🎬", value="movie night"),
        app_commands.Choice(name="Chill 😌", value="chill"),
        app_commands.Choice(name="Custom", value="custom"),
    ])
    async def start(self, interaction: discord.Interaction, activity: str, ping: bool = False, custom: str = None):
        activity_label = custom if (activity == "custom" and custom) else activity

        activity_emojis = {
            "game night": "🎮",
            "movie night": "🎬",
            "chill": "😌",
        }
        emoji = activity_emojis.get(activity, "🔥")

        # Find a VC to suggest
        vc_suggestion = None
        for vc in interaction.guild.voice_channels:
            if "main" in vc.name.lower() or "general" in vc.name.lower():
                vc_suggestion = vc
                break
        if not vc_suggestion and interaction.guild.voice_channels:
            vc_suggestion = interaction.guild.voice_channels[0]

        embed = discord.Embed(
            title=f"{emoji} {activity_label.title()} — LET'S GO",
            description=f"**{interaction.user.display_name}** is starting a session. Who's in?",
            color=discord.Color.orange()
        )
        if vc_suggestion:
            embed.add_field(name="Suggested VC", value=vc_suggestion.mention, inline=True)
        embed.add_field(name="Activity", value=activity_label.title(), inline=True)
        embed.set_footer(text="React ✅ to join in or just pull up to VC")

        content = "@here" if ping else ""
        await interaction.response.send_message(content=content, embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")

    @app_commands.command(name="roast", description="Roast a member — opt-in fun only")
    @app_commands.describe(target="Who's getting roasted?")
    async def roast(self, interaction: discord.Interaction, target: discord.Member):
        user_id = interaction.user.id
        now = datetime.utcnow().timestamp()

        if user_id in self.roast_cooldowns:
            elapsed = now - self.roast_cooldowns[user_id]
            if elapsed < ROAST_COOLDOWN_SECONDS:
                remaining = int(ROAST_COOLDOWN_SECONDS - elapsed)
                await interaction.response.send_message(
                    f"⏳ Cool down — {remaining}s until next roast.", ephemeral=True
                )
                return

        if target.id == self.bot.user.id:
            await interaction.response.send_message("Nice try. I roast, I don't get roasted. 😤", ephemeral=True)
            return

        roast = random.choice(ROAST_MESSAGES).format(target=target.display_name)
        self.roast_cooldowns[user_id] = now

        embed = discord.Embed(
            description=f"🔥 {roast}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Requested by {interaction.user.display_name} · opt-in humor only")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="lfg", description="Looking for group — no more 'who's down?' threads that die in 3 messages")
    @app_commands.describe(game="What game?", size="How many people needed?")
    async def lfg(self, interaction: discord.Interaction, game: str, size: int):
        if size < 2 or size > 20:
            await interaction.response.send_message("Size must be between 2 and 20.", ephemeral=True)
            return

        expires_at = datetime.utcnow() + timedelta(minutes=30)
        members = [interaction.user.id]
        members_str = json.dumps(members)

        embed = discord.Embed(
            title=f"🎮 LFG — {game}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Game", value=game, inline=True)
        embed.add_field(name="Spots", value=f"{len(members)}/{size}", inline=True)
        embed.add_field(name="Players", value=interaction.user.mention, inline=False)
        embed.add_field(name="Expires", value=f"<t:{int(expires_at.timestamp())}:R>", inline=False)
        embed.set_footer(text="React ✅ to join this lobby")

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")

        async with await get_db() as db:
            await db.execute(
                """INSERT INTO lfg_lobbies
                   (guild_id, channel_id, message_id, creator_id, game, size, members, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (interaction.guild_id, interaction.channel_id, msg.id,
                 interaction.user.id, game, size, members_str, expires_at)
            )
            await db.commit()

        # Schedule expiry check
        await asyncio.sleep(30 * 60)
        async with await get_db() as db:
            async with db.execute(
                "SELECT id FROM lfg_lobbies WHERE message_id = ?", (msg.id,)
            ) as cursor:
                row = await cursor.fetchone()
            if row:
                await db.execute("DELETE FROM lfg_lobbies WHERE message_id = ?", (msg.id,))
                await db.commit()
                try:
                    expired_embed = discord.Embed(
                        title=f"⏰ LFG Expired — {game}",
                        description="This lobby didn't fill up in time.",
                        color=discord.Color.greyple()
                    )
                    await msg.edit(embed=expired_embed)
                except Exception:
                    pass


async def setup(bot):
    await bot.add_cog(Fun(bot))
