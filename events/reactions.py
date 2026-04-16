import discord
from discord.ext import commands
from storage.db import get_db
from datetime import datetime
import json


class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        if not payload.guild_id:
            return

        emoji = str(payload.emoji)

        # ⭐ — Highlight system
        if emoji == "⭐":
            await self._handle_highlight(payload)

        # 📖 — Lore system
        elif emoji == "📖":
            await self._handle_lore(payload)

        # 💬 — Quote system
        elif emoji == "💬":
            await self._handle_quote(payload)

        # ✅ — LFG lobby join
        elif emoji == "✅":
            await self._handle_lfg_join(payload)

    async def _handle_highlight(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return

        # Check star count threshold
        for reaction in message.reactions:
            if str(reaction.emoji) == "⭐" and reaction.count >= 1:
                highlights_cog = self.bot.get_cog("Highlights")
                if highlights_cog:
                    await highlights_cog.post_highlight(message)
                break

    async def _handle_lore(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return

        if not message.content:
            return

        async with await get_db() as db:
            # Check if already saved as lore
            async with db.execute(
                "SELECT id FROM lore WHERE guild_id = ? AND content = ? AND author_id = ?",
                (payload.guild_id, message.content, message.author.id)
            ) as cursor:
                existing = await cursor.fetchone()

            if not existing:
                await db.execute(
                    "INSERT INTO lore (guild_id, author_id, content) VALUES (?, ?, ?)",
                    (payload.guild_id, message.author.id, message.content)
                )
                await db.commit()

                try:
                    reactor = guild.get_member(payload.user_id)
                    await channel.send(
                        f"📖 Lore captured: *\"{message.content[:80]}{'...' if len(message.content) > 80 else ''}\"*",
                        delete_after=5
                    )
                except Exception:
                    pass

    async def _handle_quote(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return

        if not message.content:
            return

        async with await get_db() as db:
            await db.execute(
                """INSERT OR IGNORE INTO quotes (guild_id, message_id, author_id, content, jump_url)
                   VALUES (?, ?, ?, ?, ?)""",
                (payload.guild_id, payload.message_id, message.author.id,
                 message.content, message.jump_url)
            )
            await db.commit()

        try:
            await channel.send(
                f"💬 Quote saved from **{message.author.display_name}**.",
                delete_after=4
            )
        except Exception:
            pass

    async def _handle_lfg_join(self, payload: discord.RawReactionActionEvent):
        async with await get_db() as db:
            async with db.execute(
                "SELECT id, members, size, game, creator_id, channel_id FROM lfg_lobbies WHERE message_id = ?",
                (payload.message_id,)
            ) as cursor:
                row = await cursor.fetchone()

        if not row:
            return

        lobby_id, members_str, size, game, creator_id, channel_id = row
        members = json.loads(members_str)

        if payload.user_id in members:
            return

        members.append(payload.user_id)

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(channel_id)

        if len(members) >= size:
            # Lobby is full — ping everyone
            mentions = " ".join(f"<@{uid}>" for uid in members)
            embed = discord.Embed(
                title=f"🎮 Lobby Full — {game}",
                description=f"All {size} slots filled. Let's go!\n{mentions}",
                color=discord.Color.green()
            )
            try:
                await channel.send(embed=embed)
            except Exception:
                pass
            async with await get_db() as db:
                await db.execute("DELETE FROM lfg_lobbies WHERE id = ?", (lobby_id,))
                await db.commit()
        else:
            async with await get_db() as db:
                await db.execute(
                    "UPDATE lfg_lobbies SET members = ? WHERE id = ?",
                    (json.dumps(members), lobby_id)
                )
                await db.commit()

            # Update the lobby embed
            try:
                msg_channel = guild.get_channel(payload.channel_id)
                msg = await msg_channel.fetch_message(payload.message_id)
                embed = msg.embeds[0] if msg.embeds else None
                if embed:
                    member_names = " ".join(f"<@{uid}>" for uid in members)
                    new_embed = discord.Embed(
                        title=f"🎮 LFG — {game}",
                        color=discord.Color.blue()
                    )
                    new_embed.add_field(name="Game", value=game, inline=True)
                    new_embed.add_field(name="Spots", value=f"{len(members)}/{size}", inline=True)
                    new_embed.add_field(name="Players", value=member_names, inline=False)
                    new_embed.set_footer(text="React ✅ to join this lobby")
                    await msg.edit(embed=new_embed)
            except Exception:
                pass


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Clutch Mode — ping random opt-in user when VC drops to 1 person."""
        if member.bot:
            return

        if after.channel and len([m for m in after.channel.members if not m.bot]) == 1:
            await self._check_clutch(member.guild, after.channel, after.channel.members[0])

        # Track VC activity for streak
        if after.channel and not before.channel:
            streak_cog = member._state._get_client().get_cog("Streak") if hasattr(member, '_state') else None
            if not streak_cog:
                streak_cog = self.bot.get_cog("Streak")
            if streak_cog:
                await streak_cog.record_activity(member.guild.id)

    async def _check_clutch(self, guild: discord.Guild, channel: discord.VoiceChannel, lone_member: discord.Member):
        from config import CLUTCH_COOLDOWN_MINUTES, CLUTCH_MESSAGES
        import random
        from datetime import datetime, timedelta

        now = datetime.utcnow()

        async with await get_db() as db:
            async with db.execute(
                "SELECT last_ping FROM clutch_cooldown WHERE guild_id = ? AND channel_id = ?",
                (guild.id, channel.id)
            ) as cursor:
                row = await cursor.fetchone()

        if row:
            last_ping = datetime.fromisoformat(row[0])
            if (now - last_ping).total_seconds() < CLUTCH_COOLDOWN_MINUTES * 60:
                return

        # Get opt-in members who are online and not in VC
        async with await get_db() as db:
            async with db.execute(
                "SELECT user_id FROM clutch_opt_in WHERE guild_id = ?",
                (guild.id,)
            ) as cursor:
                opt_in_rows = await cursor.fetchall()

        opt_in_ids = [r[0] for r in opt_in_rows]
        eligible = [
            m for m in guild.members
            if m.id in opt_in_ids
            and m.id != lone_member.id
            and not m.bot
            and m.status != discord.Status.offline
            and (not m.voice or m.voice.channel is None)
        ]

        if not eligible:
            return

        pinged = random.choice(eligible)
        msg_template = random.choice(CLUTCH_MESSAGES)
        message = msg_template.format(lonely=lone_member.display_name, pinged=pinged.mention)

        general = discord.utils.get(guild.text_channels, name="general")
        if general:
            await general.send(message)

        async with await get_db() as db:
            await db.execute(
                """INSERT INTO clutch_cooldown (guild_id, channel_id, last_ping) VALUES (?, ?, ?)
                   ON CONFLICT(guild_id, channel_id) DO UPDATE SET last_ping = excluded.last_ping""",
                (guild.id, channel.id, now.isoformat())
            )
            await db.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        pass  # No deduplication needed for remove events in current design


async def setup(bot):
    await bot.add_cog(Reactions(bot))
