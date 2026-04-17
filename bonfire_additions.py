"""
╔══════════════════════════════════════════════════════════════╗
║              🔥 BONFIRE BOT · ADDITIONS v3.0                 ║
║         12 God-Tier Features for Real Friend Servers         ║
╠══════════════════════════════════════════════════════════════╣
║  Drop this file next to main.py and import at the bottom     ║
║  Add all new cog classes to ALL_COGS in main.py              ║
╚══════════════════════════════════════════════════════════════╝

HOW TO INTEGRATE:
1. Place bonfire_additions.py in the same directory as main.py
2. At the top of main.py add:   from bonfire_additions import *
3. Add all new cog classes to the ALL_COGS list in main.py
4. Add the new DB table statements to init_db() in main.py
   (or just call init_db_additions() once on startup)

NEW COMMANDS ADDED:
  /bonk give/balance/leaderboard/shop
  /buy  (spend bonks on perks)
  /mood (daily mood check-in → squad heatmap)
  /moodmap (see the squad's emotional radar)
  /ship (nominate a ship or view brackets)
  /capsule seal/open (time capsule messages)
  /prophecy write/reveal (sealed 30-day prophecies)
  /rolleroulette (swap two people's nicknames for 24h)
  /snapshotstory (auto-collage of this week in the server)
  /heatmap (activity heatmap by hour/day)
  /combostats (see squad simultaneous activity streaks)
  /unhinged (weekly toxicity/roast leaderboard)
"""

import asyncio
import json
import random
import os
from collections import defaultdict
from datetime import datetime, timedelta, UTC, date

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks

# ── re-use helpers from main.py ────────────────────────────────
# These are defined in main.py; we reference them at runtime.
# If running standalone, define fallbacks below.
try:
    from __main__ import (
        get_db, bonfire_footer, log_timeline, check_achievement,
        _is_core, PRIMARY, TEAL, PURPLE, GOLD, DARK_GREY, ORANGE,
        progress_bar
    )
except ImportError:
    # Fallback stubs so the file parses cleanly even in isolation
    DB_PATH = os.path.join(os.path.dirname(__file__), "storage", "bonfire.db")
    def get_db():
        return aiosqlite.connect(DB_PATH)
    def bonfire_footer(f):
        return f"🔥 Bonfire · {f} · {datetime.now(UTC).strftime('%b %d %H:%M')} UTC"
    async def log_timeline(*a, **kw): pass
    async def check_achievement(*a, **kw): pass
    def _is_core(m): return True
    def progress_bar(v, m, l=10):
        if m == 0: return "░" * l
        return "█" * round((v/m)*l) + "░" * (l - round((v/m)*l))
    PRIMARY   = discord.Color.from_str("#FF4500")
    TEAL      = discord.Color.from_str("#4ECDC4")
    PURPLE    = discord.Color.from_str("#9B59B6")
    GOLD      = discord.Color.from_str("#F1C40F")
    DARK_GREY = discord.Color.from_str("#2C2F33")
    ORANGE    = discord.Color.from_str("#E67E22")


# ─────────────────────────────────────────────────────────────
# [NEW DB TABLES]
# Add these to init_db() in main.py, or call init_db_additions()
# ─────────────────────────────────────────────────────────────

ADDITIONS_TABLES = [
    # Bonk economy
    """CREATE TABLE IF NOT EXISTS bonk_ledger (
        guild_id   INTEGER,
        user_id    INTEGER,
        balance    INTEGER DEFAULT 0,
        lifetime   INTEGER DEFAULT 0,
        PRIMARY KEY (guild_id, user_id)
    )""",
    """CREATE TABLE IF NOT EXISTS bonk_transactions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        from_id     INTEGER,
        to_id       INTEGER,
        amount      INTEGER,
        reason      TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS bonk_shop_purchases (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        user_id     INTEGER,
        item_key    TEXT,
        target_id   INTEGER,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Mood board
    """CREATE TABLE IF NOT EXISTS mood_checkins (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        user_id     INTEGER,
        mood        TEXT,
        note        TEXT,
        score       INTEGER,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Ship wars
    """CREATE TABLE IF NOT EXISTS ships (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        user1_id    INTEGER,
        user2_id    INTEGER,
        nominator_id INTEGER,
        ship_name   TEXT,
        votes       INTEGER DEFAULT 0,
        voters      TEXT DEFAULT '[]',
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Time capsules
    """CREATE TABLE IF NOT EXISTS time_capsules (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        author_id   INTEGER,
        target_id   INTEGER,
        message     TEXT,
        reveal_at   TIMESTAMP,
        revealed    INTEGER DEFAULT 0,
        channel_id  INTEGER,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Prophecies
    """CREATE TABLE IF NOT EXISTS prophecies (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        author_id   INTEGER,
        target_id   INTEGER,
        prophecy    TEXT,
        reveal_at   TIMESTAMP,
        revealed    INTEGER DEFAULT 0,
        channel_id  INTEGER,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Role roulette log
    """CREATE TABLE IF NOT EXISTS role_roulette (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        user1_id    INTEGER,
        user2_id    INTEGER,
        old_nick1   TEXT,
        old_nick2   TEXT,
        restore_at  TIMESTAMP,
        restored    INTEGER DEFAULT 0,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Combo streak (simultaneous activity)
    """CREATE TABLE IF NOT EXISTS combo_streaks (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        members     TEXT,
        count       INTEGER,
        peak_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Activity heatmap (hour/day buckets)
    """CREATE TABLE IF NOT EXISTS activity_heatmap (
        guild_id    INTEGER,
        dow         INTEGER,
        hour        INTEGER,
        count       INTEGER DEFAULT 0,
        PRIMARY KEY (guild_id, dow, hour)
    )""",
    # Roast/unhinged counter
    """CREATE TABLE IF NOT EXISTS roast_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        user_id     INTEGER,
        target_id   INTEGER,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Snapshot story log
    """CREATE TABLE IF NOT EXISTS snapshot_stories (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id    INTEGER,
        message_ids TEXT DEFAULT '[]',
        posted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
]

async def init_db_additions():
    """Call this once to create the new tables. Safe to call repeatedly."""
    async with get_db() as db:
        for stmt in ADDITIONS_TABLES:
            await db.execute(stmt)
        await db.commit()


# ─────────────────────────────────────────────────────────────
# BONK ECONOMY
# The squad's internal social currency.
# Earned automatically for: messages, highlights, quotes, VC time,
# completing challenges, winning bets, being roasted, vouch given.
# Spent in the /buy shop for real Discord perks.
# ─────────────────────────────────────────────────────────────

BONK_EARN_RATES = {
    "message":        1,    # per message (capped at 50/day)
    "highlight":      25,   # your message gets highlighted
    "quoted":         15,   # your message gets quoted
    "vc_minute":      2,    # per minute in VC (capped at 60/day)
    "challenge_done": 100,  # complete a weekly challenge
    "beef_resolved":  30,   # you resolve a beef
    "lore_added":     10,   # you add lore
    "vouch_given":    20,   # you vouch for someone
    "bet_won":        50,   # you win a bet
}

BONK_SHOP = {
    "rename_channel": {
        "name": "📝 Rename a channel (24h)",
        "desc": "Rename any text channel to anything you want for 24 hours.",
        "cost": 500,
        "needs_target_channel": True,
    },
    "force_roast": {
        "name": "🔥 Force Roast someone",
        "desc": "Bot posts a roast about your target in general. They can't refuse.",
        "cost": 150,
        "needs_target_member": True,
    },
    "roast_immunity": {
        "name": "🛡️ Roast Immunity (24h)",
        "desc": "Bot refuses to roast you for 24 hours. Coward price.",
        "cost": 200,
        "needs_target_member": False,
    },
    "vip_role": {
        "name": "👑 VIP Role (48h)",
        "desc": "Temporary gold VIP role that shows above everyone.",
        "cost": 750,
        "needs_target_member": False,
    },
    "truth_bomb": {
        "name": "💣 Truth Bomb",
        "desc": "Bot DMs your target a random ToD truth — they have to answer publicly.",
        "cost": 100,
        "needs_target_member": True,
    },
    "nickname_lock": {
        "name": "🔒 Lock someone's nickname (1h)",
        "desc": "Change and lock a member's nickname for 1 hour.",
        "cost": 300,
        "needs_target_member": True,
    },
    "spotlight": {
        "name": "🔦 Spotlight post",
        "desc": "Bot posts a hype post about you in general. Pure flex.",
        "cost": 250,
        "needs_target_member": False,
    },
    "confession_reveal": {
        "name": "🕵️ Reveal a confession",
        "desc": "Bot reveals the author of the most recent confession (with their consent prompt).",
        "cost": 400,
        "needs_target_member": False,
    },
}

SPOTLIGHT_LINES = [
    "{user} is built different and everyone knows it. Undeniable presence.",
    "Reminder that {user} has been carrying this server for a while now. Respect.",
    "{user} is operating on a level most of you can't see yet. Watch.",
    "The data is in: {user} is objectively the most locked-in person here.",
    "{user} said nothing but the vibes were immaculate. That's called talent.",
    "Real ones know {user} has been the backbone of this server from day one.",
]


class BonkEconomy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._msg_counts: dict = defaultdict(lambda: defaultdict(int))  # guild→user→count today
        self._vc_minutes: dict = defaultdict(lambda: defaultdict(int))  # guild→user→mins today
        self._immunity: dict   = {}  # user_id → expiry timestamp
        self._vip_roles: dict  = {}  # guild_id → {user_id: expiry}
        self.daily_reset_task.start()
        self.vc_ticker.start()

    def cog_unload(self):
        self.daily_reset_task.cancel()
        self.vc_ticker.cancel()

    # ── Internal helpers ──────────────────────────────────────

    async def _ensure_user(self, guild_id: int, user_id: int):
        async with get_db() as db:
            await db.execute(
                "INSERT OR IGNORE INTO bonk_ledger (guild_id, user_id) VALUES (?,?)",
                (guild_id, user_id))
            await db.commit()

    async def get_balance(self, guild_id: int, user_id: int) -> int:
        await self._ensure_user(guild_id, user_id)
        async with get_db() as db:
            async with db.execute(
                "SELECT balance FROM bonk_ledger WHERE guild_id=? AND user_id=?",
                (guild_id, user_id)) as cur:
                row = await cur.fetchone()
        return row[0] if row else 0

    async def earn(self, guild_id: int, user_id: int, amount: int, reason: str):
        await self._ensure_user(guild_id, user_id)
        async with get_db() as db:
            await db.execute(
                "UPDATE bonk_ledger SET balance=balance+?, lifetime=lifetime+?"
                " WHERE guild_id=? AND user_id=?",
                (amount, amount, guild_id, user_id))
            await db.execute(
                "INSERT INTO bonk_transactions (guild_id, from_id, to_id, amount, reason)"
                " VALUES (?,?,?,?,?)",
                (guild_id, 0, user_id, amount, reason))
            await db.commit()

    async def spend(self, guild_id: int, user_id: int, amount: int, reason: str) -> bool:
        balance = await self.get_balance(guild_id, user_id)
        if balance < amount:
            return False
        async with get_db() as db:
            await db.execute(
                "UPDATE bonk_ledger SET balance=balance-? WHERE guild_id=? AND user_id=?",
                (amount, guild_id, user_id))
            await db.execute(
                "INSERT INTO bonk_transactions (guild_id, from_id, to_id, amount, reason)"
                " VALUES (?,?,?,?,?)",
                (guild_id, user_id, 0, -amount, reason))
            await db.commit()
        return True

    async def on_message_earn(self, guild_id: int, user_id: int):
        today = date.today().isoformat()
        key   = (today, guild_id, user_id)
        self._msg_counts[key] = self._msg_counts.get(key, 0) + 1
        if self._msg_counts[key] <= 50:
            await self.earn(guild_id, user_id, BONK_EARN_RATES["message"], "message")

    async def on_event_earn(self, guild_id: int, user_id: int, event_key: str):
        amount = BONK_EARN_RATES.get(event_key, 0)
        if amount:
            await self.earn(guild_id, user_id, amount, event_key)

    def is_immune(self, user_id: int) -> bool:
        exp = self._immunity.get(user_id)
        return exp and datetime.now(UTC).timestamp() < exp

    @tasks.loop(hours=24)
    async def daily_reset_task(self):
        self._msg_counts.clear()
        self._vc_minutes.clear()
        # Check and remove expired VIPs
        now = datetime.now(UTC).timestamp()
        for guild_id, users in list(self._vip_roles.items()):
            for uid, exp in list(users.items()):
                if now > exp:
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        member = guild.get_member(uid)
                        vip_role = discord.utils.get(guild.roles, name="👑 VIP")
                        if member and vip_role and vip_role in member.roles:
                            try:
                                await member.remove_roles(vip_role, reason="VIP expired")
                            except Exception:
                                pass
                    del self._vip_roles[guild_id][uid]

    @daily_reset_task.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def vc_ticker(self):
        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if member.bot:
                        continue
                    today = date.today().isoformat()
                    key   = (today, guild.id, member.id)
                    mins  = self._vc_minutes.get(key, 0)
                    if mins < 60:
                        await self.earn(guild.id, member.id, BONK_EARN_RATES["vc_minute"], "vc_minute")
                        self._vc_minutes[key] = mins + 1

    @vc_ticker.before_loop
    async def before_ticker(self):
        await self.bot.wait_until_ready()

    # ── Slash commands ────────────────────────────────────────

    @app_commands.command(name="bonk", description="🪙 Bonk economy — give, check balance, leaderboard")
    @app_commands.describe(action="What to do", member="Target member", amount="Amount to give")
    @app_commands.choices(action=[
        app_commands.Choice(name="My balance",    value="balance"),
        app_commands.Choice(name="Give bonks",    value="give"),
        app_commands.Choice(name="Leaderboard",   value="leaderboard"),
        app_commands.Choice(name="Transactions",  value="history"),
    ])
    async def bonk(self, interaction: discord.Interaction,
                   action: str = "balance",
                   member: discord.Member = None,
                   amount: int = 10):
        gid = interaction.guild_id
        uid = interaction.user.id

        if action == "balance":
            target = member or interaction.user
            bal = await self.get_balance(gid, target.id)
            async with get_db() as db:
                async with db.execute(
                    "SELECT lifetime FROM bonk_ledger WHERE guild_id=? AND user_id=?",
                    (gid, target.id)) as cur:
                    row = await cur.fetchone()
            lifetime = row[0] if row else 0
            embed = discord.Embed(title=f"🪙 {target.display_name}'s Bonk Balance", color=GOLD)
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.add_field(name="💰 Current",  value=f"**{bal:,}** 🪙", inline=True)
            embed.add_field(name="📈 All-time",  value=f"{lifetime:,} 🪙",  inline=True)
            bar = progress_bar(bal, max(bal, 1000))
            embed.add_field(name="Progress to 1k", value=bar, inline=False)
            embed.set_footer(text=bonfire_footer("Bonk Economy"))
            await interaction.response.send_message(embed=embed)

        elif action == "give":
            if not member:
                await interaction.response.send_message("Specify who to give bonks to.", ephemeral=True); return
            if member.id == uid:
                await interaction.response.send_message("Can't give bonks to yourself 💀", ephemeral=True); return
            if not 1 <= amount <= 500:
                await interaction.response.send_message("Give between 1–500 bonks.", ephemeral=True); return
            success = await self.spend(gid, uid, amount, f"gift to {member.id}")
            if not success:
                bal = await self.get_balance(gid, uid)
                await interaction.response.send_message(
                    f"Broke. You only have {bal} 🪙", ephemeral=True); return
            await self.earn(gid, member.id, amount, f"gift from {uid}")
            embed = discord.Embed(
                title="🪙 Bonks Sent",
                description=f"{interaction.user.mention} → {member.mention}\n**{amount:,} 🪙**",
                color=GOLD)
            embed.set_footer(text=bonfire_footer("Bonk Economy"))
            await interaction.response.send_message(embed=embed)

        elif action == "leaderboard":
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, balance, lifetime FROM bonk_ledger WHERE guild_id=?"
                    " ORDER BY balance DESC LIMIT 10", (gid,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("Nobody has bonks yet.", ephemeral=True); return
            embed = discord.Embed(title="🪙 Bonk Leaderboard", color=GOLD)
            medals = ["🥇","🥈","🥉"]
            for i, (user_id, bal, lifetime) in enumerate(rows, 1):
                m = interaction.guild.get_member(user_id)
                medal = medals[i-1] if i <= 3 else f"#{i}"
                bar   = progress_bar(bal, rows[0][1])
                embed.add_field(
                    name=f"{medal} {m.display_name if m else user_id}",
                    value=f"{bar} {bal:,} 🪙 (all-time: {lifetime:,})",
                    inline=False)
            embed.set_footer(text=bonfire_footer("Bonk Economy"))
            await interaction.response.send_message(embed=embed)

        elif action == "history":
            async with get_db() as db:
                async with db.execute(
                    "SELECT amount, reason, created_at FROM bonk_transactions"
                    " WHERE guild_id=? AND (from_id=? OR to_id=?)"
                    " ORDER BY created_at DESC LIMIT 10",
                    (gid, uid, uid)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No transactions yet.", ephemeral=True); return
            embed = discord.Embed(title="🪙 Transaction History", color=GOLD)
            for amount_val, reason, created_at in rows:
                sign = "+" if amount_val > 0 else ""
                embed.add_field(
                    name=f"{sign}{amount_val} 🪙",
                    value=f"{reason} · {str(created_at)[:16]}",
                    inline=False)
            embed.set_footer(text=bonfire_footer("Bonk Economy"))
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="shop", description="🛒 Browse and buy stuff with your bonks")
    async def shop(self, interaction: discord.Interaction):
        bal = await self.get_balance(interaction.guild_id, interaction.user.id)
        embed = discord.Embed(
            title="🛒 Bonk Shop",
            description=f"Your balance: **{bal:,} 🪙**\nUse `/buy <item>` to purchase.",
            color=GOLD)
        for key, item in BONK_SHOP.items():
            can_afford = "✅" if bal >= item["cost"] else "❌"
            embed.add_field(
                name=f"{can_afford} {item['name']}",
                value=f"{item['desc']}\n**Cost:** {item['cost']:,} 🪙",
                inline=False)
        embed.set_footer(text=bonfire_footer("Bonk Shop"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="buy", description="🛒 Buy something from the Bonk Shop")
    @app_commands.describe(
        item="Item to buy (use /shop to see options)",
        target="Target member (if applicable)",
        channel="Target channel (for rename)",
        rename_to="New channel name (for rename)")
    @app_commands.choices(item=[
        app_commands.Choice(name=v["name"], value=k)
        for k, v in BONK_SHOP.items()
    ])
    async def buy(self, interaction: discord.Interaction,
                  item: str,
                  target: discord.Member = None,
                  channel: discord.TextChannel = None,
                  rename_to: str = None):
        await interaction.response.defer(ephemeral=True)
        gid  = interaction.guild_id
        uid  = interaction.user.id
        shop_item = BONK_SHOP.get(item)
        if not shop_item:
            await interaction.followup.send("Unknown item.", ephemeral=True); return

        cost    = shop_item["cost"]
        success = await self.spend(gid, uid, cost, f"shop:{item}")
        if not success:
            bal = await self.get_balance(gid, uid)
            await interaction.followup.send(
                f"Not enough bonks. You have {bal:,} 🪙, need {cost:,} 🪙.", ephemeral=True); return

        guild = interaction.guild
        gen_ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                  discord.utils.get(guild.text_channels, name="general"))

        if item == "rename_channel":
            ch = channel or interaction.channel
            if not rename_to:
                await interaction.followup.send("Provide a new name with `rename_to`.", ephemeral=True)
                await self.earn(gid, uid, cost, "refund:rename_channel"); return
            old_name = ch.name
            try:
                await ch.edit(name=rename_to[:32], reason=f"Bonk shop: renamed by {interaction.user}")
                asyncio.create_task(self._restore_name(ch, old_name, 86400))
                await interaction.followup.send(
                    f"✅ #{ch.name} renamed to **{rename_to}** for 24h.", ephemeral=True)
                if gen_ch:
                    await gen_ch.send(
                        f"🛒 {interaction.user.mention} just bought a channel rename. "
                        f"**#{old_name}** is now **#{rename_to}** for 24 hours. 💸")
            except Exception as e:
                await interaction.followup.send(f"Failed: {e}", ephemeral=True)
                await self.earn(gid, uid, cost, "refund:rename_channel")

        elif item == "force_roast":
            if not target:
                await interaction.followup.send("Specify a target.", ephemeral=True)
                await self.earn(gid, uid, cost, "refund:force_roast"); return
            if self.is_immune(target.id):
                await interaction.followup.send(f"{target.display_name} has roast immunity active!", ephemeral=True)
                await self.earn(gid, uid, cost, "refund:force_roast"); return
            from __main__ import ROAST_MESSAGES
            roast = random.choice(ROAST_MESSAGES).format(target=target.display_name)
            if gen_ch:
                embed = discord.Embed(description=f"🔥 {roast}", color=discord.Color.red())
                embed.set_thumbnail(url=target.display_avatar.url)
                embed.set_footer(text=f"💸 Force-roasted via the Bonk Shop by {interaction.user.display_name}")
                await gen_ch.send(embed=embed)
            await interaction.followup.send("✅ Roast deployed.", ephemeral=True)

        elif item == "roast_immunity":
            self._immunity[uid] = datetime.now(UTC).timestamp() + 86400
            await interaction.followup.send("🛡️ Roast immunity active for 24h. Coward.", ephemeral=True)

        elif item == "vip_role":
            vip_role = discord.utils.get(guild.roles, name="👑 VIP")
            if not vip_role:
                vip_role = await guild.create_role(
                    name="👑 VIP", color=GOLD, hoist=True, reason="Bonk Shop VIP role")
                # Position it high
                try:
                    bot_top = max((r.position for r in guild.me.roles), default=1)
                    await vip_role.edit(position=bot_top - 1)
                except Exception:
                    pass
            member = guild.get_member(uid)
            if member:
                await member.add_roles(vip_role, reason="Bonk Shop VIP (48h)")
                if guild.id not in self._vip_roles:
                    self._vip_roles[guild.id] = {}
                self._vip_roles[guild.id][uid] = datetime.now(UTC).timestamp() + 172800
            if gen_ch:
                await gen_ch.send(
                    f"👑 {interaction.user.mention} bought themselves a **VIP role** for 48 hours. "
                    f"Must be nice having that kind of bonk wealth.")
            await interaction.followup.send("✅ VIP role active for 48h.", ephemeral=True)

        elif item == "truth_bomb":
            if not target:
                await interaction.followup.send("Specify a target.", ephemeral=True)
                await self.earn(gid, uid, cost, "refund:truth_bomb"); return
            from __main__ import TOD_TRUTHS
            truth = random.choice(TOD_TRUTHS)
            try:
                dm_embed = discord.Embed(
                    title=f"💣 Truth Bomb — courtesy of the Bonk Shop",
                    description=f"Someone spent their hard-earned bonks to send you this.\n\n**{truth}**\n\nAnswer in the server. Publicly. No backing out.",
                    color=PURPLE)
                await target.send(embed=dm_embed)
            except discord.Forbidden:
                pass
            if gen_ch:
                await gen_ch.send(
                    f"💣 {target.mention} just got hit with a **Truth Bomb**. "
                    f"Check your DMs. The squad is waiting for your answer. "
                    f"*Truth: {truth}*")
            await interaction.followup.send("✅ Truth bomb sent.", ephemeral=True)

        elif item == "nickname_lock":
            if not target:
                await interaction.followup.send("Specify a target.", ephemeral=True)
                await self.earn(gid, uid, cost, "refund:nickname_lock"); return
            import hashlib
            random_nick = random.choice([
                "Just a Little Guy", "Professional Loser", "The Lurker", "Background NPC",
                "Too Broke for Bonks", "Smells Like Grass", "WiFi Dependent", "Sigma Wannabe",
            ])
            old_nick = target.display_name
            try:
                await target.edit(nick=random_nick, reason="Bonk Shop nickname lock (1h)")
                asyncio.create_task(self._restore_nick(target, old_nick, 3600))
                if gen_ch:
                    await gen_ch.send(
                        f"🔒 {target.mention}'s nickname just got locked to **{random_nick}** for 1 hour. "
                        f"The bonk economy claims another victim.")
                await interaction.followup.send("✅ Nickname locked for 1h.", ephemeral=True)
            except discord.Forbidden:
                await interaction.followup.send("Can't edit that member's nickname (hierarchy).", ephemeral=True)
                await self.earn(gid, uid, cost, "refund:nickname_lock")

        elif item == "spotlight":
            member_obj = guild.get_member(uid)
            if gen_ch and member_obj:
                line = random.choice(SPOTLIGHT_LINES).format(user=member_obj.mention)
                embed = discord.Embed(description=f"🔦 {line}", color=GOLD)
                embed.set_thumbnail(url=member_obj.display_avatar.url)
                embed.set_footer(text="🛒 Purchased via the Bonk Shop")
                await gen_ch.send(embed=embed)
            await interaction.followup.send("✅ Spotlight posted.", ephemeral=True)

        elif item == "confession_reveal":
            async with get_db() as db:
                async with db.execute(
                    "SELECT id, user_hash, content FROM confessions WHERE guild_id=? ORDER BY id DESC LIMIT 1",
                    (gid,)) as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.followup.send("No confessions on record.", ephemeral=True)
                await self.earn(gid, uid, cost, "refund:confession_reveal"); return
            conf_id, user_hash, content = row
            if gen_ch:
                await gen_ch.send(
                    f"🕵️ Someone spent **400 🪙** to request a confession reveal.\n"
                    f"Confession #{conf_id}: *\"{content[:100]}\"*\n"
                    f"Author hash: `{user_hash}` — they know who they are.")
            await interaction.followup.send("✅ Reveal triggered.", ephemeral=True)

        async with get_db() as db:
            await db.execute(
                "INSERT INTO bonk_shop_purchases (guild_id, user_id, item_key, target_id)"
                " VALUES (?,?,?,?)",
                (gid, uid, item, target.id if target else 0))
            await db.commit()

    async def _restore_name(self, channel, old_name, delay):
        await asyncio.sleep(delay)
        try:
            await channel.edit(name=old_name, reason="Bonk Shop: name restore")
        except Exception:
            pass

    async def _restore_nick(self, member, old_nick, delay):
        await asyncio.sleep(delay)
        try:
            await member.edit(nick=old_nick if old_nick != member.name else None,
                              reason="Bonk Shop: nickname unlock")
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
# MOOD BOARD
# Daily anonymous mood check-in. Squad emotional radar.
# ─────────────────────────────────────────────────────────────

MOODS = {
    "🔥": ("Fired up",     5, "#FF4500"),
    "😊": ("Good",         4, "#4ECDC4"),
    "😐": ("Meh",          3, "#95A5A6"),
    "😔": ("Down",         2, "#2C3E50"),
    "💀": ("Send help",    1, "#8E44AD"),
}

MOOD_PROMPTS = [
    "one word to describe how you feel",
    "what's the vibe tonight",
    "current status — no filter",
    "rate yourself right now",
    "what's in your head tonight",
]


class MoodBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_mood_prompt.start()

    def cog_unload(self):
        self.daily_mood_prompt.cancel()

    @app_commands.command(name="mood", description="🎭 Log your mood — builds the squad emotional radar")
    async def mood(self, interaction: discord.Interaction):
        today = date.today().isoformat()
        async with get_db() as db:
            async with db.execute(
                "SELECT id FROM mood_checkins WHERE guild_id=? AND user_id=? AND DATE(created_at)=?",
                (interaction.guild_id, interaction.user.id, today)) as cur:
                if await cur.fetchone():
                    await interaction.response.send_message(
                        "Already checked in today. Come back tomorrow.", ephemeral=True); return

        embed = discord.Embed(
            title=f"🎭 How are you actually doing?",
            description=f"Anonymous. Real. No judgment.\n*{random.choice(MOOD_PROMPTS)}*",
            color=PURPLE)
        embed.set_footer(text=bonfire_footer("Mood Board"))

        view = discord.ui.View(timeout=120)
        for emoji, (label, score, _) in MOODS.items():
            async def cb(inter: discord.Interaction, e=emoji, l=label, s=score):
                await inter.response.send_modal(MoodNoteModal(self.bot, inter.guild_id, inter.user.id, e, l, s))
            btn = discord.ui.Button(label=f"{emoji} {label}", style=discord.ButtonStyle.secondary)
            btn.callback = cb
            view.add_item(btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="moodmap", description="📡 See the squad's emotional radar for today")
    async def moodmap(self, interaction: discord.Interaction):
        today = date.today().isoformat()
        async with get_db() as db:
            async with db.execute(
                "SELECT mood, COUNT(*) cnt, AVG(score) avg FROM mood_checkins"
                " WHERE guild_id=? AND DATE(created_at)=?"
                " GROUP BY mood ORDER BY cnt DESC",
                (interaction.guild_id, today)) as cur:
                rows = await cur.fetchall()
            async with db.execute(
                "SELECT AVG(score) FROM mood_checkins WHERE guild_id=? AND DATE(created_at)=?",
                (interaction.guild_id, today)) as cur:
                avg_row = await cur.fetchone()
            async with db.execute(
                "SELECT COUNT(DISTINCT user_id) FROM mood_checkins WHERE guild_id=? AND DATE(created_at)=?",
                (interaction.guild_id, today)) as cur:
                total_row = await cur.fetchone()

        if not rows:
            await interaction.response.send_message(
                "Nobody checked in today. Use `/mood` first.", ephemeral=True); return

        total_people = total_row[0] if total_row else 0
        avg_score    = avg_row[0]   if avg_row  else 0

        overall_vibe = (
            "The squad is locked in 🔥" if avg_score >= 4.5 else
            "Things are good 😊"         if avg_score >= 3.5 else
            "Middle of the road 😐"       if avg_score >= 2.5 else
            "Some people need checking on 😔" if avg_score >= 1.5 else
            "Someone send backup 💀"
        )

        embed = discord.Embed(
            title=f"📡 Squad Mood Radar — {today}",
            description=f"**{total_people}** people checked in · Overall: *{overall_vibe}*",
            color=PURPLE)

        total_count = sum(r[1] for r in rows)
        for mood_emoji, cnt, _ in rows:
            label = MOODS.get(mood_emoji, ("Unknown", 0, ""))[0]
            pct   = cnt / total_count * 100
            bar   = progress_bar(cnt, total_count)
            embed.add_field(
                name=f"{mood_emoji} {label}",
                value=f"{bar} {cnt} ({pct:.0f}%)",
                inline=True)

        score_bar = progress_bar(avg_score, 5)
        embed.add_field(name="📊 Squad Score", value=f"{score_bar} {avg_score:.1f}/5", inline=False)
        embed.set_footer(text=bonfire_footer("Mood Board"))
        await interaction.response.send_message(embed=embed)

    @tasks.loop(hours=24)
    async def daily_mood_prompt(self):
        now = datetime.now(UTC)
        if now.hour != 20:
            return
        for guild in self.bot.guilds:
            ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                  discord.utils.get(guild.text_channels, name="general"))
            if ch:
                embed = discord.Embed(
                    title="🎭 Daily Vibe Check",
                    description=f"How's the squad doing tonight?\n*{random.choice(MOOD_PROMPTS)}*\n\nUse `/mood` to check in. Anonymous.",
                    color=PURPLE)
                embed.set_footer(text=bonfire_footer("Mood Board"))
                await ch.send(embed=embed)

    @daily_mood_prompt.before_loop
    async def before_mood(self):
        await self.bot.wait_until_ready()


class MoodNoteModal(discord.ui.Modal, title="🎭 Add a note (optional)"):
    note = discord.ui.TextInput(
        label="Anything you want to say? (optional)",
        required=False,
        max_length=150,
        style=discord.TextStyle.paragraph,
        placeholder="Nobody sees your name. Just the vibe.")

    def __init__(self, bot, guild_id, user_id, mood_emoji, mood_label, score):
        super().__init__()
        self.bot        = bot
        self.guild_id   = guild_id
        self.user_id    = user_id
        self.mood_emoji = mood_emoji
        self.mood_label = mood_label
        self.score      = score

    async def on_submit(self, interaction: discord.Interaction):
        async with get_db() as db:
            await db.execute(
                "INSERT INTO mood_checkins (guild_id, user_id, mood, note, score) VALUES (?,?,?,?,?)",
                (self.guild_id, self.user_id, self.mood_emoji, self.note.value or "", self.score))
            await db.commit()
        await interaction.response.send_message(
            f"{self.mood_emoji} Mood logged. The squad sees the vibes (not your name).",
            ephemeral=True)


# ─────────────────────────────────────────────────────────────
# SHIP WARS
# Nominate pairs, vote on them, bracket style.
# ─────────────────────────────────────────────────────────────

SHIP_NAME_COMBOS = [
    ("{a}{b}", "classic"),
    ("{b}{a}", "reverse"),
    ("{a} + {b}", "plus"),
]


def _make_ship_name(n1: str, n2: str) -> str:
    half1 = n1[:len(n1)//2]
    half2 = n2[len(n2)//2:]
    return f"{half1}{half2}".title()


class ShipWars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ship", description="💕 Ship two server members and let the squad vote")
    @app_commands.describe(
        action="What to do",
        member1="First person",
        member2="Second person",
        ship_name="Custom ship name (optional)")
    @app_commands.choices(action=[
        app_commands.Choice(name="Nominate a ship", value="nominate"),
        app_commands.Choice(name="Top ships",       value="top"),
        app_commands.Choice(name="Battle (vote)",   value="battle"),
        app_commands.Choice(name="My ships",        value="mine"),
    ])
    async def ship(self, interaction: discord.Interaction,
                   action: str = "top",
                   member1: discord.Member = None,
                   member2: discord.Member = None,
                   ship_name: str = None):
        gid = interaction.guild_id

        if action == "nominate":
            if not member1 or not member2:
                await interaction.response.send_message("Need two members.", ephemeral=True); return
            if member1.id == member2.id:
                await interaction.response.send_message("Can't ship someone with themselves (or can you?)", ephemeral=True); return

            auto_name = ship_name or _make_ship_name(member1.display_name, member2.display_name)
            m1_id, m2_id = min(member1.id, member2.id), max(member1.id, member2.id)

            async with get_db() as db:
                async with db.execute(
                    "SELECT id FROM ships WHERE guild_id=? AND user1_id=? AND user2_id=?",
                    (gid, m1_id, m2_id)) as cur:
                    existing = await cur.fetchone()
                if existing:
                    await interaction.response.send_message(
                        f"**{auto_name}** already exists! Go vote on it.", ephemeral=True); return
                cur = await db.execute(
                    "INSERT INTO ships (guild_id, user1_id, user2_id, nominator_id, ship_name)"
                    " VALUES (?,?,?,?,?)",
                    (gid, m1_id, m2_id, interaction.user.id, auto_name))
                await db.commit()
                ship_id = cur.lastrowid

            embed = discord.Embed(
                title=f"💕 New Ship: {auto_name}",
                description=f"**{member1.mention}** × **{member2.mention}**\n\nVote below if you ship it.",
                color=discord.Color.from_str("#FF69B4"))
            embed.set_author(
                name=f"Nominated by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text=bonfire_footer("Ship Wars"))

            voters  = []
            votes   = [0]
            view    = discord.ui.View(timeout=86400)

            async def vote_cb(inter: discord.Interaction):
                if inter.user.id in voters:
                    await inter.response.send_message("Already voted!", ephemeral=True); return
                if inter.user.id in (m1_id, m2_id):
                    await inter.response.send_message("Can't vote on your own ship 😭", ephemeral=True); return
                voters.append(inter.user.id)
                votes[0] += 1
                async with get_db() as db:
                    await db.execute(
                        "UPDATE ships SET votes=?, voters=? WHERE id=?",
                        (votes[0], json.dumps(voters), ship_id))
                    await db.commit()
                await inter.response.send_message(f"💕 Voted for **{auto_name}**! ({votes[0]} total)", ephemeral=True)

            vote_btn = discord.ui.Button(label=f"💕 Ship it ({votes[0]})", style=discord.ButtonStyle.danger)
            vote_btn.callback = vote_cb
            view.add_item(vote_btn)
            await interaction.response.send_message(embed=embed, view=view)

        elif action == "top":
            async with get_db() as db:
                async with db.execute(
                    "SELECT user1_id, user2_id, ship_name, votes FROM ships"
                    " WHERE guild_id=? ORDER BY votes DESC LIMIT 10", (gid,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message(
                    "No ships yet. Use `/ship nominate` to start.", ephemeral=True); return
            embed = discord.Embed(title="💕 Server Ship Leaderboard", color=discord.Color.from_str("#FF69B4"))
            medals = ["🥇","🥈","🥉"]
            for i, (u1, u2, name, votes) in enumerate(rows, 1):
                m1 = interaction.guild.get_member(u1)
                m2 = interaction.guild.get_member(u2)
                medal = medals[i-1] if i <= 3 else f"#{i}"
                n1 = m1.display_name if m1 else str(u1)
                n2 = m2.display_name if m2 else str(u2)
                embed.add_field(
                    name=f"{medal} {name}",
                    value=f"{n1} × {n2} · {votes} votes",
                    inline=False)
            embed.set_footer(text=bonfire_footer("Ship Wars"))
            await interaction.response.send_message(embed=embed)

        elif action == "battle":
            async with get_db() as db:
                async with db.execute(
                    "SELECT id, user1_id, user2_id, ship_name, votes FROM ships"
                    " WHERE guild_id=? ORDER BY RANDOM() LIMIT 2", (gid,)) as cur:
                    ships_rows = await cur.fetchall()
            if len(ships_rows) < 2:
                await interaction.response.send_message(
                    "Need at least 2 ships for a battle.", ephemeral=True); return

            s1, s2    = ships_rows
            s1_votes  = [0]; s2_votes = [0]; battle_voters = set()

            embed = discord.Embed(
                title="⚔️ Ship Battle",
                description="Vote for which ship you stan more. No going back.",
                color=discord.Color.from_str("#FF69B4"))
            embed.add_field(name=f"1️⃣ {s1[3]}", value=f"Votes so far: {s1[4]}", inline=True)
            embed.add_field(name=f"2️⃣ {s2[3]}", value=f"Votes so far: {s2[4]}", inline=True)
            embed.set_footer(text=bonfire_footer("Ship Wars"))

            view = discord.ui.View(timeout=3600)
            async def vote1(inter: discord.Interaction):
                if inter.user.id in battle_voters:
                    await inter.response.send_message("Already voted!", ephemeral=True); return
                battle_voters.add(inter.user.id); s1_votes[0] += 1
                await inter.response.send_message(f"💕 Voted for **{s1[3]}**!", ephemeral=True)
            async def vote2(inter: discord.Interaction):
                if inter.user.id in battle_voters:
                    await inter.response.send_message("Already voted!", ephemeral=True); return
                battle_voters.add(inter.user.id); s2_votes[0] += 1
                await inter.response.send_message(f"💕 Voted for **{s2[3]}**!", ephemeral=True)

            b1 = discord.ui.Button(label=f"1️⃣ {s1[3][:20]}", style=discord.ButtonStyle.danger)
            b2 = discord.ui.Button(label=f"2️⃣ {s2[3][:20]}", style=discord.ButtonStyle.danger)
            b1.callback = vote1; b2.callback = vote2
            view.add_item(b1); view.add_item(b2)
            await interaction.response.send_message(embed=embed, view=view)

            async def end_battle():
                await asyncio.sleep(3600)
                winner = s1 if s1_votes[0] >= s2_votes[0] else s2
                result_embed = discord.Embed(
                    title=f"💕 Ship Battle Results",
                    description=f"**{winner[3]}** wins! ({s1_votes[0]} vs {s2_votes[0]} votes)",
                    color=discord.Color.from_str("#FF69B4"))
                result_embed.set_footer(text=bonfire_footer("Ship Wars"))
                await interaction.channel.send(embed=result_embed)
            asyncio.create_task(end_battle())

        elif action == "mine":
            uid = interaction.user.id
            async with get_db() as db:
                async with db.execute(
                    "SELECT user1_id, user2_id, ship_name, votes FROM ships"
                    " WHERE guild_id=? AND (user1_id=? OR user2_id=?)"
                    " ORDER BY votes DESC", (gid, uid, uid)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message(
                    "No ships for you yet. The squad hasn't decided.", ephemeral=True); return
            embed = discord.Embed(
                title=f"💕 Ships featuring {interaction.user.display_name}",
                color=discord.Color.from_str("#FF69B4"))
            for u1, u2, name, votes in rows:
                partner_id = u2 if u1 == uid else u1
                partner    = interaction.guild.get_member(partner_id)
                embed.add_field(
                    name=name,
                    value=f"with {partner.display_name if partner else '?'} · {votes} votes",
                    inline=True)
            embed.set_footer(text=bonfire_footer("Ship Wars"))
            await interaction.response.send_message(embed=embed, ephemeral=True)


# ─────────────────────────────────────────────────────────────
# TIME CAPSULE
# Lock a message → auto-reveals after X days
# ─────────────────────────────────────────────────────────────

class TimeCapsule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.capsule_checker.start()

    def cog_unload(self):
        self.capsule_checker.cancel()

    @app_commands.command(name="capsule", description="📦 Seal or open time capsule messages")
    @app_commands.describe(
        action="What to do",
        message="Message to seal",
        days="Days until reveal",
        target="Who to send it to (optional)")
    @app_commands.choices(action=[
        app_commands.Choice(name="Seal a capsule", value="seal"),
        app_commands.Choice(name="My capsules",    value="list"),
    ])
    async def capsule(self, interaction: discord.Interaction,
                      action: str = "list",
                      message: str = None,
                      days: int = 30,
                      target: discord.Member = None):
        if action == "seal":
            if not message:
                await interaction.response.send_message("Write something to seal.", ephemeral=True); return
            if not 1 <= days <= 365:
                await interaction.response.send_message("Days must be 1–365.", ephemeral=True); return
            reveal_at = datetime.now(UTC) + timedelta(days=days)
            async with get_db() as db:
                await db.execute(
                    "INSERT INTO time_capsules (guild_id, author_id, target_id, message, reveal_at, channel_id)"
                    " VALUES (?,?,?,?,?,?)",
                    (interaction.guild_id, interaction.user.id,
                     target.id if target else interaction.user.id,
                     message, reveal_at, interaction.channel_id))
                await db.commit()

            embed = discord.Embed(
                title="📦 Time Capsule Sealed",
                description=f"Your message is locked until **{reveal_at.strftime('%B %d, %Y')}**.",
                color=TEAL)
            embed.add_field(name="📝 Contents", value="*sealed — only revealed on the date*", inline=False)
            embed.add_field(name="📅 Reveal Date", value=f"<t:{int(reveal_at.timestamp())}:D>", inline=True)
            embed.add_field(name="🎯 For", value=(target.mention if target else "yourself"), inline=True)
            embed.set_footer(text=bonfire_footer("Time Capsule"))
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif action == "list":
            async with get_db() as db:
                async with db.execute(
                    "SELECT message, reveal_at, revealed, target_id FROM time_capsules"
                    " WHERE guild_id=? AND author_id=? ORDER BY reveal_at ASC",
                    (interaction.guild_id, interaction.user.id)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message(
                    "No capsules. Use `/capsule seal` to write one.", ephemeral=True); return
            embed = discord.Embed(title="📦 Your Time Capsules", color=TEAL)
            for msg, reveal_at, revealed, target_id in rows:
                status = "✅ Revealed" if revealed else f"🔒 Opens <t:{int(datetime.fromisoformat(str(reveal_at)).timestamp())}:R>"
                snip   = (msg[:40] + "…") if len(msg) > 40 else msg
                embed.add_field(name=f"{'📖' if revealed else '📦'} {snip}", value=status, inline=False)
            embed.set_footer(text=bonfire_footer("Time Capsule"))
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(minutes=10)
    async def capsule_checker(self):
        now = datetime.now(UTC)
        async with get_db() as db:
            async with db.execute(
                "SELECT id, guild_id, author_id, target_id, message, channel_id"
                " FROM time_capsules WHERE revealed=0 AND reveal_at<=?",
                (now,)) as cur:
                rows = await cur.fetchall()
        for cap_id, guild_id, author_id, target_id, message, channel_id in rows:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            ch = guild.get_channel(channel_id) or \
                 discord.utils.get(guild.text_channels, name="🔥・general") or \
                 discord.utils.get(guild.text_channels, name="general")
            if not ch:
                continue
            author = guild.get_member(author_id)
            target = guild.get_member(target_id)

            embed = discord.Embed(
                title="📬 A Time Capsule Just Opened",
                description=f"**{message}**",
                color=TEAL,
                timestamp=now)
            embed.set_author(
                name=f"From: {author.display_name}" if author else "From: Someone",
                icon_url=author.display_avatar.url if author else None)
            if target and target.id != author_id:
                embed.add_field(name="For", value=target.mention)
            embed.set_footer(text=bonfire_footer("Time Capsule"))
            await ch.send(
                content=target.mention if target else None,
                embed=embed)

            async with get_db() as db:
                await db.execute("UPDATE time_capsules SET revealed=1 WHERE id=?", (cap_id,))
                await db.commit()

    @capsule_checker.before_loop
    async def before_capsule(self):
        await self.bot.wait_until_ready()


# ─────────────────────────────────────────────────────────────
# PROPHECY
# Sealed 30-day prophecy for a server member. Reveals automatically.
# ─────────────────────────────────────────────────────────────

PROPHECY_INTROS = [
    "The flame has spoken.",
    "The bonfire does not lie.",
    "It was written in the smoke.",
    "Nobody is surprised.",
    "The fire saw this coming.",
    "The vibe doesn't lie.",
]


class Prophecy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prophecy_checker.start()

    def cog_unload(self):
        self.prophecy_checker.cancel()

    @app_commands.command(name="prophecy", description="🔮 Write a sealed prophecy about someone — reveals in 30 days")
    @app_commands.describe(
        action="What to do",
        target="Who the prophecy is about",
        text="The prophecy (only you can see this until it reveals)")
    @app_commands.choices(action=[
        app_commands.Choice(name="Write a prophecy", value="write"),
        app_commands.Choice(name="Pending for me",   value="mine"),
        app_commands.Choice(name="History",          value="history"),
    ])
    async def prophecy(self, interaction: discord.Interaction,
                       action: str = "mine",
                       target: discord.Member = None,
                       text: str = None):
        if action == "write":
            if not target or not text:
                await interaction.response.send_message("Specify target and prophecy text.", ephemeral=True); return
            if target.id == interaction.user.id:
                await interaction.response.send_message("Can't prophesy yourself (or can you?)", ephemeral=True); return
            reveal_at = datetime.now(UTC) + timedelta(days=30)
            async with get_db() as db:
                await db.execute(
                    "INSERT INTO prophecies (guild_id, author_id, target_id, prophecy, reveal_at, channel_id)"
                    " VALUES (?,?,?,?,?,?)",
                    (interaction.guild_id, interaction.user.id, target.id,
                     text, reveal_at, interaction.channel_id))
                await db.commit()
            embed = discord.Embed(
                title="🔮 Prophecy Sealed",
                description=f"Your prophecy for **{target.display_name}** is locked in.\nThe squad will see it on **{reveal_at.strftime('%B %d, %Y')}**.",
                color=PURPLE)
            embed.set_footer(text=bonfire_footer("Prophecy"))
            await interaction.response.send_message(embed=embed, ephemeral=True)
            # Tease in public without revealing
            gen_ch = discord.utils.get(interaction.guild.text_channels, name="🔥・general") or \
                     discord.utils.get(interaction.guild.text_channels, name="general")
            if gen_ch:
                await gen_ch.send(
                    f"🔮 A prophecy has been written about **{target.display_name}**. "
                    f"It will be revealed in 30 days. Someone knows something.")

        elif action == "mine":
            async with get_db() as db:
                async with db.execute(
                    "SELECT author_id, reveal_at, revealed FROM prophecies"
                    " WHERE guild_id=? AND target_id=? ORDER BY reveal_at ASC",
                    (interaction.guild_id, interaction.user.id)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message(
                    "No prophecies about you. Either nobody cares or they haven't written it yet.",
                    ephemeral=True); return
            embed = discord.Embed(title="🔮 Prophecies About You", color=PURPLE)
            for author_id, reveal_at, revealed in rows:
                a = interaction.guild.get_member(author_id)
                ts = int(datetime.fromisoformat(str(reveal_at)).timestamp())
                if revealed:
                    status = "✅ Revealed"
                else:
                    status = f"🔒 Opens <t:{ts}:R>"
                embed.add_field(
                    name=f"From {a.display_name if a else '???'}",
                    value=status, inline=True)
            embed.set_footer(text=bonfire_footer("Prophecy"))
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif action == "history":
            async with get_db() as db:
                async with db.execute(
                    "SELECT author_id, target_id, prophecy, reveal_at FROM prophecies"
                    " WHERE guild_id=? AND revealed=1 ORDER BY reveal_at DESC LIMIT 10",
                    (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No revealed prophecies yet.", ephemeral=True); return
            embed = discord.Embed(title="🔮 Revealed Prophecies", color=PURPLE)
            for author_id, target_id, proph_text, reveal_at in rows:
                a = interaction.guild.get_member(author_id)
                t = interaction.guild.get_member(target_id)
                embed.add_field(
                    name=f"{a.display_name if a else '?'} → {t.display_name if t else '?'}",
                    value=f"*\"{proph_text[:100]}\"*",
                    inline=False)
            embed.set_footer(text=bonfire_footer("Prophecy"))
            await interaction.response.send_message(embed=embed)

    @tasks.loop(minutes=15)
    async def prophecy_checker(self):
        now = datetime.now(UTC)
        async with get_db() as db:
            async with db.execute(
                "SELECT id, guild_id, author_id, target_id, prophecy, channel_id"
                " FROM prophecies WHERE revealed=0 AND reveal_at<=?",
                (now,)) as cur:
                rows = await cur.fetchall()
        for pid, guild_id, author_id, target_id, text, channel_id in rows:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            ch = guild.get_channel(channel_id) or \
                 discord.utils.get(guild.text_channels, name="🔥・general") or \
                 discord.utils.get(guild.text_channels, name="general")
            if not ch:
                continue
            author = guild.get_member(author_id)
            target = guild.get_member(target_id)
            intro  = random.choice(PROPHECY_INTROS)
            embed  = discord.Embed(
                title=f"🔮 A Prophecy Reveals Itself",
                description=f"*{intro}*\n\n**About {target.mention if target else '?'}:**\n\n*\"{text}\"*",
                color=PURPLE,
                timestamp=now)
            embed.set_author(
                name=f"Prophesied by {author.display_name}" if author else "Prophesied by someone",
                icon_url=author.display_avatar.url if author else None)
            embed.set_footer(text=bonfire_footer("Prophecy"))
            await ch.send(content=target.mention if target else None, embed=embed)
            async with get_db() as db:
                await db.execute("UPDATE prophecies SET revealed=1 WHERE id=?", (pid,))
                await db.commit()
            # Award prophet achievement if they've had 5 prophecies reveal
            if author:
                async with get_db() as db:
                    async with db.execute(
                        "SELECT COUNT(*) FROM prophecies WHERE guild_id=? AND author_id=? AND revealed=1",
                        (guild_id, author_id)) as cur:
                        cnt = (await cur.fetchone())[0]
                if cnt >= 5:
                    await check_achievement(self.bot, guild_id, author_id, "prophet")

    @prophecy_checker.before_loop
    async def before_prophecy(self):
        await self.bot.wait_until_ready()


# ─────────────────────────────────────────────────────────────
# ROLE ROULETTE
# Temporarily swap two members' nicknames for 24h.
# ─────────────────────────────────────────────────────────────

ROULETTE_TAUNTS = [
    "Identity swap activated. Good luck explaining this.",
    "You are now each other for the next 24 hours. Act accordingly.",
    "The bonfire has shuffled the deck. New mains only.",
    "Swapped. Nobody leaves until this timer expires.",
    "Identity crisis speedrun starts now.",
]


class RoleRoulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.restore_checker.start()

    def cog_unload(self):
        self.restore_checker.cancel()

    @app_commands.command(name="rolleroulette", description="🎰 Swap two members' nicknames for 24h")
    @app_commands.describe(
        member1="First victim",
        member2="Second victim (or random if blank)")
    async def rolleroulette(self, interaction: discord.Interaction,
                            member1: discord.Member = None,
                            member2: discord.Member = None):
        if not _is_core(interaction.user):
            await interaction.response.send_message("Core/OG only.", ephemeral=True); return

        guild = interaction.guild
        m1 = member1 or interaction.user
        if not member2:
            candidates = [m for m in guild.members if not m.bot and m.id != m1.id]
            if not candidates:
                await interaction.response.send_message("Not enough members.", ephemeral=True); return
            m2 = random.choice(candidates)
        else:
            m2 = member2

        if m1.id == m2.id:
            await interaction.response.send_message("Need two different members.", ephemeral=True); return

        old1 = m1.display_name
        old2 = m2.display_name
        restore_at = datetime.now(UTC) + timedelta(hours=24)

        try:
            await m1.edit(nick=old2, reason="Role Roulette swap")
            await m2.edit(nick=old1, reason="Role Roulette swap")
        except discord.Forbidden:
            await interaction.response.send_message(
                "Can't edit one or both nicknames (hierarchy issue).", ephemeral=True); return

        async with get_db() as db:
            await db.execute(
                "INSERT INTO role_roulette (guild_id, user1_id, user2_id, old_nick1, old_nick2, restore_at)"
                " VALUES (?,?,?,?,?,?)",
                (guild.id, m1.id, m2.id, old1, old2, restore_at))
            await db.commit()

        embed = discord.Embed(
            title="🎰 Role Roulette",
            description=random.choice(ROULETTE_TAUNTS),
            color=ORANGE)
        embed.add_field(name=f"{old1} → {m1.mention}",  value=f"now goes by **{old2}**", inline=True)
        embed.add_field(name=f"{old2} → {m2.mention}",  value=f"now goes by **{old1}**", inline=True)
        embed.add_field(name="⏰ Restores in", value=f"<t:{int(restore_at.timestamp())}:R>", inline=False)
        embed.set_footer(text=bonfire_footer("Role Roulette"))
        await interaction.response.send_message(embed=embed)
        await log_timeline(guild.id, "🎰", f"Role Roulette: {old1} ↔ {old2}", [m1.id, m2.id])

    @tasks.loop(minutes=15)
    async def restore_checker(self):
        now = datetime.now(UTC)
        async with get_db() as db:
            async with db.execute(
                "SELECT id, guild_id, user1_id, user2_id, old_nick1, old_nick2"
                " FROM role_roulette WHERE restored=0 AND restore_at<=?",
                (now,)) as cur:
                rows = await cur.fetchall()
        for rid, guild_id, u1, u2, n1, n2 in rows:
            guild = self.bot.get_guild(guild_id)
            if guild:
                m1 = guild.get_member(u1)
                m2 = guild.get_member(u2)
                try:
                    if m1: await m1.edit(nick=n1 if n1 != m1.name else None, reason="Role Roulette restore")
                    if m2: await m2.edit(nick=n2 if n2 != m2.name else None, reason="Role Roulette restore")
                except Exception:
                    pass
            async with get_db() as db:
                await db.execute("UPDATE role_roulette SET restored=1 WHERE id=?", (rid,))
                await db.commit()

    @restore_checker.before_loop
    async def before_restore(self):
        await self.bot.wait_until_ready()


# ─────────────────────────────────────────────────────────────
# ACTIVITY HEATMAP
# Tracks message activity by day-of-week + hour.
# Posts a visual ASCII heatmap weekly.
# ─────────────────────────────────────────────────────────────

DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
HEAT_CHARS = [" ", "░", "▒", "▓", "█"]


class ActivityHeatmap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_heatmap.start()

    def cog_unload(self):
        self.weekly_heatmap.cancel()

    async def record(self, guild_id: int):
        now = datetime.now(UTC)
        dow = now.weekday()
        hr  = now.hour
        async with get_db() as db:
            await db.execute(
                "INSERT INTO activity_heatmap (guild_id, dow, hour, count) VALUES (?,?,?,1)"
                " ON CONFLICT(guild_id, dow, hour) DO UPDATE SET count=count+1",
                (guild_id, dow, hr))
            await db.commit()

    @app_commands.command(name="heatmap", description="🔥 View the server's activity heatmap by hour/day")
    async def heatmap_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer()
        gid = interaction.guild_id
        async with get_db() as db:
            async with db.execute(
                "SELECT dow, hour, count FROM activity_heatmap WHERE guild_id=?", (gid,)) as cur:
                rows = await cur.fetchall()

        grid: dict[tuple, int] = defaultdict(int)
        for dow, hr, cnt in rows:
            grid[(dow, hr)] = cnt

        if not grid:
            await interaction.followup.send("No activity data yet.", ephemeral=True); return

        max_val = max(grid.values()) or 1
        lines   = ["```"]
        header  = "     " + "".join(f"{h:02d}" for h in range(0, 24, 2))
        lines.append(header)
        for d in range(7):
            row = f"{DAYS[d]:3s} "
            for h in range(24):
                val  = grid.get((d, h), 0)
                norm = val / max_val
                idx  = int(norm * (len(HEAT_CHARS) - 1))
                char = HEAT_CHARS[idx]
                if h % 2 == 0:
                    row += char * 2
            lines.append(row)
        lines.append("```")
        heatmap_str = "\n".join(lines)

        # Most active hour/day
        if grid:
            peak_dow, peak_hr = max(grid, key=grid.get)
            peak_day  = DAYS[peak_dow]
            peak_time = f"{peak_hr:02d}:00–{peak_hr+1:02d}:00 UTC"
        else:
            peak_day = peak_time = "N/A"

        embed = discord.Embed(
            title="🔥 Server Activity Heatmap",
            description=heatmap_str,
            color=PRIMARY)
        embed.add_field(name="📈 Peak Day",  value=peak_day,  inline=True)
        embed.add_field(name="⏰ Peak Time", value=peak_time, inline=True)
        embed.set_footer(text=bonfire_footer("Heatmap") + " · darker = more active")
        await interaction.followup.send(embed=embed)

    @tasks.loop(hours=168)
    async def weekly_heatmap(self):
        for guild in self.bot.guilds:
            gid = guild.id
            async with get_db() as db:
                async with db.execute(
                    "SELECT dow, hour, count FROM activity_heatmap WHERE guild_id=?", (gid,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                continue
            grid    = defaultdict(int)
            for dow, hr, cnt in rows:
                grid[(dow, hr)] = cnt
            max_val  = max(grid.values()) or 1
            if grid:
                peak_dow, peak_hr = max(grid, key=grid.get)
                peak_label = f"{DAYS[peak_dow]} {peak_hr:02d}:00 UTC"
            else:
                peak_label = "N/A"

            ch = (discord.utils.get(guild.text_channels, name="📊・status") or
                  discord.utils.get(guild.text_channels, name="status") or
                  discord.utils.get(guild.text_channels, name="general"))
            if not ch:
                continue

            lines = ["```"]
            lines.append("     " + "".join(f"{h:02d}" for h in range(0, 24, 2)))
            for d in range(7):
                row = f"{DAYS[d]:3s} "
                for h in range(24):
                    val  = grid.get((d, h), 0)
                    norm = val / max_val
                    idx  = int(norm * (len(HEAT_CHARS) - 1))
                    char = HEAT_CHARS[idx]
                    if h % 2 == 0:
                        row += char * 2
                lines.append(row)
            lines.append("```")

            embed = discord.Embed(
                title="📊 Weekly Activity Heatmap",
                description="\n".join(lines),
                color=PRIMARY)
            embed.add_field(name="🔥 Peak Time", value=peak_label, inline=True)
            embed.set_footer(text=bonfire_footer("Heatmap"))
            await ch.send(embed=embed)

    @weekly_heatmap.before_loop
    async def before_heatmap(self):
        await self.bot.wait_until_ready()
        now = datetime.now(UTC)
        days_until_sunday = (6 - now.weekday()) % 7
        if days_until_sunday == 0 and now.hour >= 20:
            days_until_sunday = 7
        target = (now + timedelta(days=days_until_sunday)).replace(
            hour=20, minute=0, second=0, microsecond=0)
        await asyncio.sleep((target - now).total_seconds())


# ─────────────────────────────────────────────────────────────
# COMBO STREAK / SQUAD MULTIPLIER
# Detects when 3+ people are active simultaneously.
# Announces it and awards bonus bonks.
# ─────────────────────────────────────────────────────────────

class ComboStreak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._recent: dict[int, dict[int, datetime]] = defaultdict(dict)  # guild→{user→last_msg}
        self._last_combo: dict[int, datetime] = {}  # guild→last combo announcement

    COMBO_THRESHOLD = 3
    COMBO_WINDOW    = 120   # seconds — "active" = messaged in last 2 min
    COOLDOWN        = 600   # 10 min between announcements

    def register_message(self, guild_id: int, user_id: int):
        self._recent[guild_id][user_id] = datetime.now(UTC)

    def get_active(self, guild_id: int) -> list:
        now    = datetime.now(UTC)
        cutoff = now - timedelta(seconds=self.COMBO_WINDOW)
        return [uid for uid, t in self._recent[guild_id].items() if t > cutoff]

    async def check_combo(self, guild: discord.Guild):
        active = self.get_active(guild.id)
        if len(active) < self.COMBO_THRESHOLD:
            return
        last = self._last_combo.get(guild.id)
        if last and (datetime.now(UTC) - last).total_seconds() < self.COOLDOWN:
            return
        self._last_combo[guild.id] = datetime.now(UTC)

        # Award bonus bonks
        bonk_cog = self.bot.get_cog("BonkEconomy")
        if bonk_cog:
            for uid in active:
                await bonk_cog.earn(guild.id, uid, 10 * len(active), "combo_streak_bonus")

        ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
              discord.utils.get(guild.text_channels, name="general"))
        if ch:
            mentions = " ".join(f"<@{uid}>" for uid in active[:8])
            embed    = discord.Embed(
                title=f"⚡ SQUAD COMBO x{len(active)}",
                description=(
                    f"{mentions}\n\n"
                    f"**{len(active)} people active simultaneously!** "
                    f"Everyone just got +{10 * len(active)} 🪙 combo bonus."
                ),
                color=PRIMARY)
            embed.set_footer(text=bonfire_footer("Combo Streak"))
            await ch.send(embed=embed)

        async with get_db() as db:
            await db.execute(
                "INSERT INTO combo_streaks (guild_id, members, count) VALUES (?,?,?)",
                (guild.id, json.dumps(active), len(active)))
            await db.commit()

    @app_commands.command(name="combostats", description="⚡ View squad combo streak records")
    async def combostats(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT members, count, peak_at FROM combo_streaks WHERE guild_id=?"
                " ORDER BY count DESC LIMIT 10", (interaction.guild_id,)) as cur:
                rows = await cur.fetchall()
            async with db.execute(
                "SELECT MAX(count) FROM combo_streaks WHERE guild_id=?",
                (interaction.guild_id,)) as cur:
                peak_row = await cur.fetchone()

        if not rows:
            await interaction.response.send_message(
                "No combo streaks yet. Get more people chatting at the same time.", ephemeral=True); return

        peak = peak_row[0] if peak_row else 0
        embed = discord.Embed(
            title="⚡ Squad Combo Records",
            description=f"Peak simultaneous activity: **{peak} people**",
            color=PRIMARY)
        for members_str, count, peak_at in rows[:5]:
            member_ids = json.loads(members_str)
            names = [
                (interaction.guild.get_member(uid).display_name
                 if interaction.guild.get_member(uid) else str(uid))
                for uid in member_ids[:5]
            ]
            bar = progress_bar(count, peak or 1)
            embed.add_field(
                name=f"⚡ x{count} — {str(peak_at)[:10]}",
                value=f"{bar}\n{', '.join(names)}",
                inline=False)
        embed.set_footer(text=bonfire_footer("Combo Streak"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────────
# UNHINGED TRACKER / ROAST LEADERBOARD
# Tracks who's been roasted and who roasts the most.
# Weekly "Most Unhinged" award.
# ─────────────────────────────────────────────────────────────

UNHINGED_TITLES = [
    "Certified Unhinged",
    "The Main Character",
    "Chaos Incarnate",
    "The One Who Started It",
    "The Server's Problem",
    "Legally Unwell",
    "The Chaos Agent",
    "Most Likely to Get Cancelled",
]


class UnhingedTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_unhinged.start()

    def cog_unload(self):
        self.weekly_unhinged.cancel()

    async def log_roast(self, guild_id: int, user_id: int, target_id: int):
        async with get_db() as db:
            await db.execute(
                "INSERT INTO roast_log (guild_id, user_id, target_id) VALUES (?,?,?)",
                (guild_id, user_id, target_id))
            await db.commit()

    @app_commands.command(name="unhinged", description="💀 See who's been the most unhinged this week")
    async def unhinged(self, interaction: discord.Interaction):
        week_ago = (datetime.now(UTC) - timedelta(days=7)).isoformat()
        async with get_db() as db:
            async with db.execute(
                "SELECT user_id, COUNT(*) cnt FROM roast_log"
                " WHERE guild_id=? AND created_at>=?"
                " GROUP BY user_id ORDER BY cnt DESC LIMIT 10",
                (interaction.guild_id, week_ago)) as cur:
                roasters = await cur.fetchall()
            async with db.execute(
                "SELECT target_id, COUNT(*) cnt FROM roast_log"
                " WHERE guild_id=? AND created_at>=?"
                " GROUP BY target_id ORDER BY cnt DESC LIMIT 10",
                (interaction.guild_id, week_ago)) as cur:
                roasted = await cur.fetchall()

        if not roasters:
            await interaction.response.send_message("No roasts logged this week.", ephemeral=True); return

        embed = discord.Embed(title="💀 Unhinged Leaderboard — This Week", color=ORANGE)
        medals = ["🥇","🥈","🥉"]

        if roasters:
            lines = []
            for i, (uid, cnt) in enumerate(roasters[:5], 1):
                m = interaction.guild.get_member(uid)
                medal = medals[i-1] if i <= 3 else f"#{i}"
                lines.append(f"{medal} {m.display_name if m else uid} — {cnt} roasts thrown")
            embed.add_field(name="🔥 Roast Machines", value="\n".join(lines), inline=False)

        if roasted:
            lines2 = []
            for i, (uid, cnt) in enumerate(roasted[:5], 1):
                m = interaction.guild.get_member(uid)
                medal = medals[i-1] if i <= 3 else f"#{i}"
                lines2.append(f"{medal} {m.display_name if m else uid} — {cnt} times cooked")
            embed.add_field(name="😭 Most Cooked", value="\n".join(lines2), inline=False)

        embed.set_footer(text=bonfire_footer("Unhinged Tracker"))
        await interaction.response.send_message(embed=embed)

    @tasks.loop(hours=168)
    async def weekly_unhinged(self):
        for guild in self.bot.guilds:
            week_ago = (datetime.now(UTC) - timedelta(days=7)).isoformat()
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, COUNT(*) cnt FROM roast_log"
                    " WHERE guild_id=? AND created_at>=?"
                    " GROUP BY user_id ORDER BY cnt DESC LIMIT 1",
                    (guild.id, week_ago)) as cur:
                    row = await cur.fetchone()
            if not row:
                continue
            uid   = row[0]
            count = row[1]
            m     = guild.get_member(uid)
            if not m:
                continue
            title = random.choice(UNHINGED_TITLES)
            ch    = (discord.utils.get(guild.text_channels, name="🔥・general") or
                     discord.utils.get(guild.text_channels, name="general"))
            if ch:
                embed = discord.Embed(
                    title=f"💀 Weekly Most Unhinged Award",
                    description=(
                        f"{m.mention} threw **{count} roasts** this week and earns the title:\n\n"
                        f"## {title}\n\n"
                        f"Congratulations. Seek help."
                    ),
                    color=ORANGE)
                embed.set_thumbnail(url=m.display_avatar.url)
                embed.set_footer(text=bonfire_footer("Unhinged Tracker"))
                await ch.send(embed=embed)
            # Award bonus bonks
            bonk_cog = self.bot.get_cog("BonkEconomy")
            if bonk_cog:
                await bonk_cog.earn(guild.id, uid, 200, "weekly_most_unhinged")

    @weekly_unhinged.before_loop
    async def before_unhinged(self):
        await self.bot.wait_until_ready()
        now = datetime.now(UTC)
        days_until_sunday = (6 - now.weekday()) % 7
        if days_until_sunday == 0 and now.hour >= 21:
            days_until_sunday = 7
        target = (now + timedelta(days=days_until_sunday)).replace(
            hour=21, minute=0, second=0, microsecond=0)
        await asyncio.sleep((target - now).total_seconds())


# ─────────────────────────────────────────────────────────────
# SNAPSHOT STORY
# Auto-collage of 5 random notable messages from this week.
# ─────────────────────────────────────────────────────────────

SNAPSHOT_INTROS = [
    "This week at the bonfire — nobody's getting out of this unscathed.",
    "The algorithm has selected. These are the moments that defined the week.",
    "Weekly digest but make it unfiltered.",
    "Nobody asked for this recap. Nobody needed to.",
    "This week in the server. Archivists have been summoned.",
]


class SnapshotStory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_snapshot.start()

    def cog_unload(self):
        self.weekly_snapshot.cancel()

    @app_commands.command(name="snapshotstory", description="📸 Post this week's snapshot story")
    async def snapshotstory_cmd(self, interaction: discord.Interaction):
        if not _is_core(interaction.user):
            await interaction.response.send_message("Core/OG only.", ephemeral=True); return
        await interaction.response.defer()
        await self._post_snapshot(interaction.guild, interaction.channel)
        await interaction.followup.send("✅ Snapshot posted.", ephemeral=True)

    async def _post_snapshot(self, guild: discord.Guild, fallback_ch=None):
        week_ago = (datetime.now(UTC) - timedelta(days=7)).isoformat()

        async with get_db() as db:
            async with db.execute(
                "SELECT content, author_id, jump_url FROM quotes WHERE guild_id=? AND created_at>=?"
                " ORDER BY RANDOM() LIMIT 3", (guild.id, week_ago)) as cur:
                quotes = await cur.fetchall()
            async with db.execute(
                "SELECT content, author_id FROM lore WHERE guild_id=? AND created_at>=?"
                " ORDER BY RANDOM() LIMIT 2", (guild.id, week_ago)) as cur:
                lore_items = await cur.fetchall()
            async with db.execute(
                "SELECT initiator_id, target_id, reason FROM beef WHERE guild_id=? AND created_at>=?",
                (guild.id, week_ago)) as cur:
                beefs = await cur.fetchall()
            async with db.execute(
                "SELECT current_streak FROM streaks WHERE guild_id=?", (guild.id,)) as cur:
                streak_row = await cur.fetchone()

        ch = (discord.utils.get(guild.text_channels, name="📊・status") or
              discord.utils.get(guild.text_channels, name="status") or
              fallback_ch or
              discord.utils.get(guild.text_channels, name="general"))
        if not ch:
            return

        intro = random.choice(SNAPSHOT_INTROS)
        embed = discord.Embed(
            title=f"📸 This Week at the Bonfire",
            description=f"*{intro}*",
            color=PRIMARY)

        if quotes:
            q_lines = []
            for content, author_id, jump_url in quotes:
                m = guild.get_member(author_id)
                snip = (content[:60] + "…") if len(content) > 60 else content
                name = m.display_name if m else "Unknown"
                q_lines.append(f'"{snip}" — {name}')
            embed.add_field(name="💬 Quotes of the Week", value="\n".join(q_lines), inline=False)

        if lore_items:
            l_lines = []
            for content, author_id in lore_items:
                m = guild.get_member(author_id)
                snip = (content[:60] + "…") if len(content) > 60 else content
                l_lines.append(f"• {snip}")
            embed.add_field(name="📖 Lore Logged", value="\n".join(l_lines), inline=False)

        if beefs:
            b_lines = []
            for init_id, tgt_id, reason in beefs[:3]:
                m1 = guild.get_member(init_id)
                m2 = guild.get_member(tgt_id)
                n1 = m1.display_name if m1 else str(init_id)
                n2 = m2.display_name if m2 else str(tgt_id)
                snip = (reason[:40] + "…") if reason and len(reason) > 40 else (reason or "no reason given")
                b_lines.append(f"🥩 {n1} vs {n2}: {snip}")
            embed.add_field(name=f"🥩 Drama ({len(beefs)} beef(s))", value="\n".join(b_lines), inline=False)

        if streak_row and streak_row[0]:
            embed.add_field(name="🔥 Streak", value=f"{streak_row[0]} days active", inline=True)

        embed.set_footer(text=bonfire_footer("Snapshot Story"))
        await ch.send(embed=embed)

        async with get_db() as db:
            await db.execute(
                "INSERT INTO snapshot_stories (guild_id) VALUES (?)", (guild.id,))
            await db.commit()

    @tasks.loop(hours=168)
    async def weekly_snapshot(self):
        for guild in self.bot.guilds:
            await self._post_snapshot(guild)

    @weekly_snapshot.before_loop
    async def before_snapshot(self):
        await self.bot.wait_until_ready()
        now = datetime.now(UTC)
        days_until_friday = (4 - now.weekday()) % 7
        if days_until_friday == 0 and now.hour >= 19:
            days_until_friday = 7
        target = (now + timedelta(days=days_until_friday)).replace(
            hour=19, minute=0, second=0, microsecond=0)
        await asyncio.sleep((target - now).total_seconds())


# ─────────────────────────────────────────────────────────────
# ADDITIONS EVENT HUB
# Hooks into EventHub to feed bonks, heatmap, combos, etc.
# Add this cog AFTER EventHub in ALL_COGS.
# ─────────────────────────────────────────────────────────────

class AdditionsEventHub(commands.Cog):
    """Listens to Discord events and routes them to the new feature cogs."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        bonk_cog    = self.bot.get_cog("BonkEconomy")
        heatmap_cog = self.bot.get_cog("ActivityHeatmap")
        combo_cog   = self.bot.get_cog("ComboStreak")

        if bonk_cog:
            await bonk_cog.on_message_earn(message.guild.id, message.author.id)
        if heatmap_cog:
            await heatmap_cog.record(message.guild.id)
        if combo_cog:
            combo_cog.register_message(message.guild.id, message.author.id)
            await combo_cog.check_combo(message.guild)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        bonk_cog    = self.bot.get_cog("BonkEconomy")
        unhinged_cog = self.bot.get_cog("UnhingedTracker")
        emoji        = str(payload.emoji)

        if emoji == "⭐" and bonk_cog:
            # Author of message earns bonks when highlighted
            ch = guild.get_channel(payload.channel_id)
            if ch:
                try:
                    msg = await ch.fetch_message(payload.message_id)
                    if not msg.author.bot:
                        await bonk_cog.on_event_earn(guild.id, msg.author.id, "highlight")
                except Exception:
                    pass

        elif emoji == "💬" and bonk_cog:
            ch = guild.get_channel(payload.channel_id)
            if ch:
                try:
                    msg = await ch.fetch_message(payload.message_id)
                    if not msg.author.bot:
                        await bonk_cog.on_event_earn(guild.id, msg.author.id, "quoted")
                except Exception:
                    pass


# ─────────────────────────────────────────────────────────────
# NEW COGS LIST
# Add all of these to ALL_COGS in main.py (before EventHub)
# ─────────────────────────────────────────────────────────────

NEW_COGS = [
    BonkEconomy,
    MoodBoard,
    ShipWars,
    TimeCapsule,
    Prophecy,
    RoleRoulette,
    ActivityHeatmap,
    ComboStreak,
    UnhingedTracker,
    SnapshotStory,
    AdditionsEventHub,  # must be last in this list
]
