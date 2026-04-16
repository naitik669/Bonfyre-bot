import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from storage.db import get_db
import json


class Wrapped(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wrapped", description="See the Crazie Wrapped — monthly recap for your friend group")
    async def wrapped(self, interaction: discord.Interaction):
        await interaction.response.defer()

        guild_id = interaction.guild_id
        month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()

        async with await get_db() as db:
            # Most active users
            async with db.execute(
                """SELECT user_id, COUNT(*) as cnt FROM activity_log
                   WHERE guild_id = ? AND created_at >= ? AND activity_type = 'message'
                   GROUP BY user_id ORDER BY cnt DESC LIMIT 5""",
                (guild_id, month_ago)
            ) as cursor:
                top_talkers = await cursor.fetchall()

            # Most lore added
            async with db.execute(
                """SELECT COUNT(*) FROM lore WHERE guild_id = ? AND created_at >= ?""",
                (guild_id, month_ago)
            ) as cursor:
                lore_count = (await cursor.fetchone())[0]

            # Total highlights
            async with db.execute(
                """SELECT COUNT(*) FROM highlights WHERE guild_id = ? AND posted_at >= ?""",
                (guild_id, month_ago)
            ) as cursor:
                highlight_count = (await cursor.fetchone())[0]

            # Top quote author
            async with db.execute(
                """SELECT author_id, COUNT(*) as cnt FROM quotes
                   WHERE guild_id = ? AND created_at >= ?
                   GROUP BY author_id ORDER BY cnt DESC LIMIT 1""",
                (guild_id, month_ago)
            ) as cursor:
                top_quoted = await cursor.fetchone()

            # Most beefs
            async with db.execute(
                """SELECT initiator_id, COUNT(*) as cnt FROM beef
                   WHERE guild_id = ? AND created_at >= ?
                   GROUP BY initiator_id ORDER BY cnt DESC LIMIT 1""",
                (guild_id, month_ago)
            ) as cursor:
                top_beef = await cursor.fetchone()

            # Most decisive /decide user
            async with db.execute(
                """SELECT result, COUNT(*) as cnt FROM decide_log
                   WHERE guild_id = ? AND decided_at >= ?
                   GROUP BY result ORDER BY cnt DESC LIMIT 1""",
                (guild_id, month_ago)
            ) as cursor:
                top_decide = await cursor.fetchone()

        now = datetime.utcnow()
        embed = discord.Embed(
            title=f"🎉 Crazie Wrapped — {now.strftime('%B %Y')}",
            description="Your friend group's monthly recap. Spotify Wrapped but make it ours.",
            color=discord.Color.purple()
        )

        # Top talkers
        if top_talkers:
            talker_lines = []
            for i, (uid, cnt) in enumerate(top_talkers, 1):
                m = interaction.guild.get_member(uid)
                name = m.display_name if m else f"<@{uid}>"
                talker_lines.append(f"**#{i}** {name} — {cnt} messages")
            embed.add_field(name="💬 Most Active", value="\n".join(talker_lines), inline=False)
        else:
            embed.add_field(name="💬 Most Active", value="No messages tracked yet", inline=False)

        embed.add_field(name="📖 Lore Entries Added", value=str(lore_count), inline=True)
        embed.add_field(name="⭐ Highlights Captured", value=str(highlight_count), inline=True)

        if top_quoted:
            m = interaction.guild.get_member(top_quoted[0])
            name = m.display_name if m else f"<@{top_quoted[0]}>"
            embed.add_field(name="💬 Most Quoted", value=f"{name} ({top_quoted[1]} quotes)", inline=True)

        if top_beef:
            m = interaction.guild.get_member(top_beef[0])
            name = m.display_name if m else f"<@{top_beef[0]}>"
            embed.add_field(name="🥩 Beef King", value=f"{name} ({top_beef[1]} beefs)", inline=True)

        if top_decide:
            embed.add_field(name="🎲 Most Decided Option", value=top_decide[0], inline=True)

        embed.set_footer(text=f"Generated {now.strftime('%B %d, %Y')} · Crazie Server Bot")
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Wrapped(bot))
