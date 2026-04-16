import discord
from discord import app_commands
from discord.ext import commands
from storage.db import get_db


class Clutch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clutch", description="Opt in or out of Clutch Mode — get pinged when someone's alone in VC")
    @app_commands.choices(action=[
        app_commands.Choice(name="Opt in", value="in"),
        app_commands.Choice(name="Opt out", value="out"),
        app_commands.Choice(name="Status", value="status"),
    ])
    async def clutch(self, interaction: discord.Interaction, action: str = "status"):
        if action == "in":
            async with await get_db() as db:
                await db.execute(
                    "INSERT OR IGNORE INTO clutch_opt_in (guild_id, user_id) VALUES (?, ?)",
                    (interaction.guild_id, interaction.user.id)
                )
                await db.commit()
            await interaction.response.send_message(
                "✅ You're now in the Clutch pool — you'll get pinged when someone's alone in VC.",
                ephemeral=True
            )

        elif action == "out":
            async with await get_db() as db:
                await db.execute(
                    "DELETE FROM clutch_opt_in WHERE guild_id = ? AND user_id = ?",
                    (interaction.guild_id, interaction.user.id)
                )
                await db.commit()
            await interaction.response.send_message(
                "👋 You've opted out of Clutch Mode.",
                ephemeral=True
            )

        elif action == "status":
            async with await get_db() as db:
                async with db.execute(
                    "SELECT user_id FROM clutch_opt_in WHERE guild_id = ?",
                    (interaction.guild_id,)
                ) as cursor:
                    rows = await cursor.fetchall()

            opted_in = [interaction.guild.get_member(r[0]) for r in rows]
            opted_in = [m for m in opted_in if m]

            if not opted_in:
                await interaction.response.send_message(
                    "Nobody is opted into Clutch Mode yet. Use `/clutch in` to join.",
                    ephemeral=True
                )
                return

            names = ", ".join(m.display_name for m in opted_in)
            await interaction.response.send_message(
                f"🔔 Clutch pool ({len(opted_in)} members): {names}",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Clutch(bot))
