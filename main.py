"""
╔══════════════════════════════════════════════════════════════╗
║                  🔥 BONFIRE BOT · main.py                    ║
║         Built for real friend groups. Not corporations.      ║
╠══════════════════════════════════════════════════════════════╣
║  SECTIONS:                                                   ║
║  [CONFIG]      — tokens, thresholds, message pools           ║
║  [DATABASE]    — SQLite schema                               ║
║  [SETUP]       — /setup  full server scaffold                ║
║  [ONBOARDING]  — join event, pfp embed, intro form           ║
║  [UTILITY]     — /decide  /vibe  /say  /np                   ║
║  [VOICE]       — /lockvc  /unlockvc  /limitvc                ║
║  [FUN]         — /start  /roast  /tod  /hottake              ║
║  [LFG]         — /lfg  lobby system                          ║
║  [REMINDERS]   — /remind  /plan  /event                      ║
║  [HIGHLIGHTS]  — ⭐ reaction → #highlights                   ║
║  [LORE]        — /lore  📖 reaction                          ║
║  [QUOTES]      — /quote  /quotes  💬 reaction                ║
║  [BEEF]        — /beef  leaderboard                          ║
║  [VIBE]        — /vibecheck  /vibereport                     ║
║  [STREAK]      — daily activity tracking                     ║
║  [WRAPPED]     — /wrapped  monthly recap                     ║
║  [CLUTCH]      — Clutch Mode VC watcher                      ║
║  [ROLES]       — auto role assignment by behavior            ║
║  [STORY]       — /story  campfire collaborative story        ║
║  [VOUCH]       — /vouch  new member approval                 ║
║  [WEATHER]     — daily vibe forecast                         ║
║  [CHALLENGE]   — weekly challenge system                     ║
║  [MODERATION]  — spam detection                              ║
║  [REACTIONS]   — raw reaction router                         ║
║  [BOT]         — bot class + entry point                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import os
import random
import re
import sys
from collections import defaultdict, deque
from datetime import date, datetime, timedelta

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────
# [CONFIG]
# ─────────────────────────────────────────────────────────

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

HIGHLIGHT_STAR_THRESHOLD  = 2
ROAST_COOLDOWN_SECONDS    = 30
DECIDE_COOLDOWN_SECONDS   = 10
SPAM_MESSAGE_THRESHOLD    = 6
SPAM_TIME_WINDOW_SECONDS  = 5
CLUTCH_COOLDOWN_MINUTES   = 15
LFG_EXPIRY_MINUTES        = 30

# Auto-role thresholds
REGULAR_MESSAGE_THRESHOLD   = 50
NIGHT_OWL_LATE_VC_THRESHOLD = 5      # times in VC after midnight
GAMER_VC_HOURS_THRESHOLD    = 10     # hours in game VC

VIBE_MESSAGES = [
    "we eating good tonight 🔥",
    "crazie hours activated",
    "the vibe is immaculate rn",
    "locked in, no cap",
    "we different fr fr",
    "running it up as always",
    "the squad is undefeated",
    "built different, can't relate",
    "W server, W people, W vibes",
    "no bad days at the bonfire",
    "the fire is burning bright tonight",
    "campfire szn never ends here",
    "this squad is something else fr",
    "another day, another W",
]

ROAST_MESSAGES = [
    "{target} really said 'I have good opinions' then opened their mouth 💀",
    "{target} is the reason they put instructions on shampoo bottles",
    "bro {target} googles how to google things",
    "{target}'s WiFi password is probably 'password123'",
    "{target} brings a spoon to a knife fight",
    "{target} thinks WiFi is spelled 'wyfy'",
    "when {target} was born the doctor slapped them and they asked 'why'",
    "{target} is 30% decisions, 70% regret",
    "{target}'s search history is a cry for help",
    "{target} has a participation trophy collection fr",
    "bro {target} still uses Internet Explorer unironically",
    "{target} is the human version of a lag spike",
    "if being chronically online was a job, {target} would finally have one",
    "{target} replied 'k' to a 3-paragraph message and slept fine",
]

CLUTCH_MESSAGES = [
    "bro {lonely} is alone in VC… who's gonna pull up? {pinged}",
    "{lonely} is holding down the VC solo rn, someone roll through {pinged}",
    "{lonely} is just vibing alone in VC, don't leave them hanging {pinged}",
    "VC check: {lonely} is in there all by themselves 💀 {pinged} pull up",
    "{lonely} deployed solo mode in VC, someone rescue them {pinged}",
]

WEATHER_FORECASTS = [
    ("🌤️ Partly Cloudy with a chance of Vibes", "Low energy start but the squad picks it up by evening. Perfect night for VC."),
    ("🔥 Scorching Hot Chaos", "Pure unhinged energy today. Someone's starting beef before lunch."),
    ("⛈️ Thunderstorms of Banter", "Roasts incoming. Stay hydrated. Bring your A-game."),
    ("🌈 Beautiful Day for the Bonfire", "Everything's crispy. Activity is high. Good vibes only."),
    ("🌫️ Foggy with Low Visibility", "Quiet today. Someone needs to /start something."),
    ("❄️ Cold Front Moving In", "Dead hours. Who's gonna light the fire? Don't make the bot do everything."),
    ("🌪️ Vibe Tornado Warning", "Unpredictable. Could go 0 to 100 real quick. Buckle up."),
    ("☀️ Peak Sunshine Energy", "The most powerful the squad has looked all week. Today is the day."),
]

WEEKLY_CHALLENGES = [
    "🎮 Win 3 ranked games and screenshot the W",
    "🎬 Recommend a movie nobody's heard of in #movie-picks",
    "🎵 Drop your current #1 most played song in #music-now",
    "📸 Post a throwback photo in #general (no cringe immunity)",
    "💬 Start a conversation that lasts 50+ messages",
    "🔥 Get a message highlighted in #highlights this week",
    "🎯 Settle a debate using /decide and actually stick to it",
    "🌙 Be in VC past 2am at least once this week",
    "🤣 Get someone to add you to the /quotes archive",
    "📖 Add a lore entry that makes everyone laugh",
    "🥩 Start AND resolve a /beef in the same week",
    "🎲 Use /decide for something actually important",
]

STORY_STARTERS = [
    "It was 3am and nobody was sleeping when suddenly…",
    "The group chat had been silent for 6 hours. Then…",
    "Nobody expected the server to become this legendary, but it started when…",
    "There were four of us, one shared screen, and zero idea what we were doing…",
    "The bet was simple: whoever lost had to…",
]

TOD_TRUTHS = [
    "What's the most embarrassing thing you've Googled in the last week?",
    "What's a song you pretend to hate but secretly love?",
    "What game do you rage quit the most?",
    "Who in this server do you think would survive a zombie apocalypse and why?",
    "What's the most L take you've ever had that you still believe?",
    "What's the last lie you told someone in this server?",
    "What's your most used emoji and what does that say about you?",
    "If you had to delete one person from this server for a week, who and why?",
    "What's the most unhinged thing you've done at 3am?",
    "Describe your sleep schedule without lying.",
]

TOD_DARES = [
    "Change your nickname to whatever the next person in chat says for 24 hours",
    "Post your phone's most recent screenshot in chat",
    "Send a voice message doing your best impression of someone in this server",
    "Share your current Spotify Wrapped top artist",
    "Write a one-sentence roast of yourself and post it",
    "Type the next 3 messages with your eyes closed",
    "React to the last 10 messages in #general with only 🥩",
    "Post your most recent search history item (screenshot)",
    "DM the last person you roasted an apology (screenshot proof required)",
    "Go offline for 30 minutes (punishment for being too online)",
]


# ─────────────────────────────────────────────────────────
# [DATABASE]
# ─────────────────────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(__file__), "storage", "bonfire.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS highlights (
                message_id INTEGER PRIMARY KEY,
                guild_id   INTEGER,
                channel_id INTEGER,
                author_id  INTEGER,
                content    TEXT,
                jump_url   TEXT,
                posted_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                channel_id INTEGER,
                user_id    INTEGER,
                message    TEXT,
                trigger_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                channel_id  INTEGER,
                creator_id  INTEGER,
                title       TEXT,
                description TEXT,
                location    TEXT,
                event_time  TIMESTAMP,
                rsvp_yes    TEXT DEFAULT '[]',
                rsvp_no     TEXT DEFAULT '[]',
                message_id  INTEGER,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS lore (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                author_id  INTEGER,
                target_id  INTEGER,
                content    TEXT,
                tags       TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS quotes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                message_id INTEGER UNIQUE,
                author_id  INTEGER,
                content    TEXT,
                jump_url   TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS beef (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id     INTEGER,
                initiator_id INTEGER,
                target_id    INTEGER,
                reason       TEXT,
                resolved     INTEGER DEFAULT 0,
                winner_id    INTEGER,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS vibe_checks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                user_id    INTEGER,
                score      INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS streaks (
                guild_id         INTEGER PRIMARY KEY,
                current_streak   INTEGER DEFAULT 0,
                last_active_date TEXT,
                longest_streak   INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS activity_log (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id      INTEGER,
                user_id       INTEGER,
                activity_type TEXT,
                detail        TEXT,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS lfg_lobbies (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                channel_id INTEGER,
                message_id INTEGER,
                creator_id INTEGER,
                game       TEXT,
                size       INTEGER,
                members    TEXT DEFAULT '[]',
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS clutch_opt_in (
                guild_id INTEGER,
                user_id  INTEGER,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS clutch_cooldown (
                guild_id   INTEGER,
                channel_id INTEGER,
                last_ping  TIMESTAMP,
                PRIMARY KEY (guild_id, channel_id)
            );
            CREATE TABLE IF NOT EXISTS decide_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                options    TEXT,
                result     TEXT,
                decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS member_intros (
                guild_id    INTEGER,
                user_id     INTEGER PRIMARY KEY,
                name        TEXT,
                age         TEXT,
                location    TEXT,
                games       TEXT,
                bio         TEXT,
                card_msg_id INTEGER,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS vouches (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                target_id   INTEGER,
                voucher_id  INTEGER,
                note        TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS story (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                author_id  INTEGER,
                line       TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS hot_takes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                user_id    INTEGER,
                take       TEXT,
                agrees     TEXT DEFAULT '[]',
                disagrees  TEXT DEFAULT '[]',
                message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS role_tracking (
                guild_id         INTEGER,
                user_id          INTEGER,
                message_count    INTEGER DEFAULT 0,
                late_vc_count    INTEGER DEFAULT 0,
                game_vc_minutes  INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS weekly_challenge (
                guild_id     INTEGER PRIMARY KEY,
                challenge    TEXT,
                posted_at    TIMESTAMP,
                completions  TEXT DEFAULT '[]'
            );
        """)
        await db.commit()


def get_db():
    return aiosqlite.connect(DB_PATH)


# ─────────────────────────────────────────────────────────
# [SETUP]
# ─────────────────────────────────────────────────────────

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="🔥 Initialize the full Bonfire server structure")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        await interaction.followup.send("🔥 Lighting the bonfire… setting up your server.", ephemeral=True)

        # Create roles
        role_defs = [
            ("👑 OG",        discord.Color.from_str("#FF6B35"),  True),
            ("🔥 Core",      discord.Color.from_str("#FF4500"),  True),
            ("💬 Regular",   discord.Color.from_str("#4ECDC4"),  False),
            ("🎮 Gamer",     discord.Color.from_str("#9B59B6"),  False),
            ("🌙 Night Owl", discord.Color.from_str("#2C3E50"),  False),
            ("👤 Lurker",    discord.Color.from_str("#95A5A6"),  False),
        ]
        created_roles = {}
        for rname, rcolor, hoist in role_defs:
            r = discord.utils.get(guild.roles, name=rname)
            if not r:
                r = await guild.create_role(name=rname, color=rcolor, hoist=hoist, reason="Bonfire Setup")
            created_roles[rname] = r

        core_role = created_roles["🔥 Core"]
        og_role   = created_roles["👑 OG"]

        default_ow = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True,  send_messages=True),
            core_role:          discord.PermissionOverwrite(read_messages=True,  send_messages=True),
        }
        readonly_ow = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True,  send_messages=False),
            core_role:          discord.PermissionOverwrite(read_messages=True,  send_messages=True),
        }
        core_only_ow = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            core_role:          discord.PermissionOverwrite(read_messages=True,  send_messages=True),
        }
        voice_ow = {
            guild.default_role: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
            core_role:          discord.PermissionOverwrite(connect=True, speak=True, view_channel=True, move_members=True),
        }

        existing_cats = [c.name for c in guild.categories]

        # 🔥 The Bonfire
        if "🔥 The Bonfire" not in existing_cats:
            cat = await guild.create_category("🔥 The Bonfire")
            for ch_name in ["general", "random", "feels-board", "homiez-cards"]:
                await guild.create_text_channel(ch_name, category=cat, overwrites=default_ow)
            await guild.create_text_channel("announcements", category=cat, overwrites=readonly_ow)

        # 🎮 Game Camp
        if "🎮 Game Camp" not in existing_cats:
            cat = await guild.create_category("🎮 Game Camp")
            for ch_name in ["lfg", "clips", "loadouts", "hot-takes"]:
                await guild.create_text_channel(ch_name, category=cat, overwrites=default_ow)
            await guild.create_voice_channel("Game VC",   category=cat, overwrites=voice_ow)
            await guild.create_voice_channel("Game VC 2", category=cat, overwrites=voice_ow)

        # 🎬 Chill Zone
        if "🎬 Chill Zone" not in existing_cats:
            cat = await guild.create_category("🎬 Chill Zone")
            for ch_name in ["movie-picks", "music-now", "memes"]:
                await guild.create_text_channel(ch_name, category=cat, overwrites=default_ow)
            await guild.create_voice_channel("Chill VC",    category=cat, overwrites=voice_ow)
            await guild.create_voice_channel("Watch Party", category=cat, overwrites=voice_ow)

        # 📖 The Lore Cave
        if "📖 The Lore Cave" not in existing_cats:
            cat = await guild.create_category("📖 The Lore Cave")
            for ch_name in ["highlights", "quotes-wall", "beef-log", "lore-archive", "campfire-story"]:
                await guild.create_text_channel(ch_name, category=cat, overwrites=default_ow)

        # 🌙 Inner Circle
        if "🌙 Inner Circle" not in existing_cats:
            cat = await guild.create_category("🌙 Inner Circle")
            await guild.create_text_channel("core-chat", category=cat, overwrites=core_only_ow)
            await guild.create_text_channel("plans",     category=cat, overwrites=core_only_ow)
            await guild.create_voice_channel("Core VC",  category=cat, overwrites={
                guild.default_role: discord.PermissionOverwrite(connect=False),
                core_role:          discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
            })

        # 📡 System
        if "📡 System" not in existing_cats:
            cat = await guild.create_category("📡 System")
            await guild.create_text_channel("status",       category=cat, overwrites=readonly_ow)
            await guild.create_text_channel("wrapped-hall", category=cat, overwrites=readonly_ow)
            await guild.create_text_channel("bot-logs",     category=cat, overwrites=core_only_ow)

        # Assign OG role to the person who ran /setup
        try:
            await interaction.user.add_roles(og_role, reason="Server founder")
            await interaction.user.add_roles(core_role, reason="Server founder")
        except Exception:
            pass

        embed = discord.Embed(
            title="🔥 Bonfire Server Ready",
            description="Your server is set up and the fire is lit.",
            color=discord.Color.from_str("#FF4500"))
        embed.add_field(name="Categories Created", value="🔥 The Bonfire · 🎮 Game Camp · 🎬 Chill Zone\n📖 The Lore Cave · 🌙 Inner Circle · 📡 System", inline=False)
        embed.add_field(name="Roles Created", value="👑 OG · 🔥 Core · 💬 Regular · 🎮 Gamer · 🌙 Night Owl · 👤 Lurker", inline=False)
        embed.add_field(name="Your Role", value="👑 OG + 🔥 Core assigned to you", inline=False)
        embed.add_field(name="Next Steps", value="1. Assign 🔥 Core to your inner circle\n2. Invite your squad\n3. Run `/challenge` to kick off the first weekly challenge", inline=False)
        embed.set_footer(text="Run /setup again to add any missing channels. Existing ones stay untouched.")
        await interaction.followup.send(embed=embed, ephemeral=True)


# ─────────────────────────────────────────────────────────
# [ONBOARDING]  — join event + intro form + homiez card
# ─────────────────────────────────────────────────────────

class IntroModal(discord.ui.Modal, title="🔥 Intro — Join the Squad"):
    name     = discord.ui.TextInput(label="Your name (or what we call you)", max_length=32,  required=True)
    age      = discord.ui.TextInput(label="Age",                              max_length=4,   required=False, placeholder="Optional")
    location = discord.ui.TextInput(label="Where you're from / based",        max_length=64,  required=False, placeholder="City, Country — optional")
    games    = discord.ui.TextInput(label="Games / interests you're into",    max_length=120, required=False, placeholder="e.g. Valorant, CS2, FIFA, vibing...")
    bio      = discord.ui.TextInput(label="One line about you (make it real)", max_length=180, required=True,
                                    style=discord.TextStyle.paragraph,
                                    placeholder="Don't be boring. Who are you?")

    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot      = bot
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild  = interaction.guild
        member = interaction.user

        # Save to DB
        async with get_db() as db:
            await db.execute("""
                INSERT OR REPLACE INTO member_intros
                  (guild_id, user_id, name, age, location, games, bio, created_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (guild.id, member.id,
                 self.name.value, self.age.value or "—",
                 self.location.value or "—", self.games.value or "—",
                 self.bio.value, datetime.utcnow()))
            await db.commit()

        # Build the homiez card
        card_ch = discord.utils.get(guild.text_channels, name="homiez-cards")
        if card_ch:
            embed = discord.Embed(
                title=f"🔥 {self.name.value}",
                description=f'*"{self.bio.value}"*',
                color=discord.Color.from_str("#FF4500"),
                timestamp=datetime.utcnow())
            embed.set_thumbnail(url=member.display_avatar.url)
            if self.age.value:
                embed.add_field(name="🎂 Age",         value=self.age.value,      inline=True)
            if self.location.value:
                embed.add_field(name="📍 Based",       value=self.location.value, inline=True)
            if self.games.value:
                embed.add_field(name="🎮 Into",        value=self.games.value,    inline=False)
            embed.add_field(name="🗓️ Joined", value=f"<t:{int(member.joined_at.timestamp())}:D>" if member.joined_at else "Today", inline=True)
            embed.set_footer(text=f"@{member.name} · {guild.name}")
            card_msg = await card_ch.send(embed=embed)

            # Save card msg id
            async with get_db() as db:
                await db.execute("UPDATE member_intros SET card_msg_id=? WHERE user_id=?",
                                 (card_msg.id, member.id))
                await db.commit()

        await interaction.followup.send(
            "✅ Your card is up in **#homiez-cards**. Welcome to the bonfire.", ephemeral=True)


class IntroView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=None)
        self.bot      = bot
        self.guild_id = guild_id

    @discord.ui.button(label="📝 Drop Your Intro", style=discord.ButtonStyle.danger, custom_id="intro_btn")
    async def intro_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = IntroModal(self.bot, interaction.guild_id)
        await interaction.response.send_modal(modal)


class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # Auto-assign Lurker role
        lurker = discord.utils.get(guild.roles, name="👤 Lurker")
        if lurker:
            try:
                await member.add_roles(lurker, reason="Auto Lurker on join")
            except discord.Forbidden:
                pass

        # Welcome DM
        try:
            embed = discord.Embed(
                title=f"🔥 Welcome to {guild.name}",
                description=(
                    f"Hey **{member.display_name}** — glad you pulled up.\n\n"
                    f"Head to **#general** and say what's good.\n"
                    f"Drop your intro with the button in **#general** so the squad knows who you are.\n\n"
                    f"Commands to try: `/vibe` `/start` `/decide`\n"
                    f"React ⭐ to highlight messages, 💬 to save quotes, 📖 to log lore.\n\n"
                    f"The fire's lit. Come get warm."
                ),
                color=discord.Color.from_str("#FF4500"))
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            embed.set_footer(text="Bonfire Bot · powered by good vibes")
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

        # Welcome card in #general
        general = discord.utils.get(guild.text_channels, name="general")
        if general:
            join_embed = discord.Embed(
                description=f"**{member.mention}** just pulled up to the bonfire 🔥\nWho are you? Drop your intro below 👇",
                color=discord.Color.from_str("#FF4500"),
                timestamp=datetime.utcnow())
            join_embed.set_thumbnail(url=member.display_avatar.url)
            join_embed.set_footer(text=f"Member #{guild.member_count}")

            view = IntroView(self.bot, guild.id)
            await general.send(embed=join_embed, view=view)

        # Log to bot-logs
        logs = discord.utils.get(guild.text_channels, name="bot-logs")
        if logs:
            log_embed = discord.Embed(
                title="📥 New Member",
                description=f"{member.mention} joined",
                color=discord.Color.green(),
                timestamp=datetime.utcnow())
            log_embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>")
            log_embed.set_thumbnail(url=member.display_avatar.url)
            await logs.send(embed=log_embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild  = member.guild
        general = discord.utils.get(guild.text_channels, name="general")
        if general:
            embed = discord.Embed(
                description=f"**{member.display_name}** left the bonfire. 👋\nKeep the fire lit.",
                color=discord.Color.greyple())
            await general.send(embed=embed)

    @app_commands.command(name="intro", description="Drop your intro card in #homiez-cards")
    async def intro_cmd(self, interaction: discord.Interaction):
        modal = IntroModal(self.bot, interaction.guild_id)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="card", description="View someone's homiez card")
    @app_commands.describe(member="Who's card to view (leave blank for yours)")
    async def card_cmd(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        async with get_db() as db:
            async with db.execute(
                "SELECT name, age, location, games, bio FROM member_intros WHERE guild_id=? AND user_id=?",
                (interaction.guild_id, target.id)) as cur:
                row = await cur.fetchone()
        if not row:
            msg = "No card yet." if member else "You haven't dropped your intro yet. Use `/intro` to do it."
            await interaction.response.send_message(msg, ephemeral=True); return

        name, age, location, games, bio = row
        embed = discord.Embed(
            title=f"🔥 {name}",
            description=f'*"{bio}"*',
            color=discord.Color.from_str("#FF4500"))
        embed.set_thumbnail(url=target.display_avatar.url)
        if age and age != "—":
            embed.add_field(name="🎂 Age",   value=age,      inline=True)
        if location and location != "—":
            embed.add_field(name="📍 Based", value=location, inline=True)
        if games and games != "—":
            embed.add_field(name="🎮 Into",  value=games,    inline=False)
        embed.set_footer(text=f"@{target.name}")
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [UTILITY]
# ─────────────────────────────────────────────────────────

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.decide_cooldowns = {}

    @app_commands.command(name="decide", description="Pick randomly from 2–10 options")
    @app_commands.describe(
        option1="First option", option2="Second option",
        option3="3rd", option4="4th", option5="5th",
        option6="6th", option7="7th", option8="8th",
        option9="9th", option10="10th")
    async def decide(self, interaction: discord.Interaction,
                     option1: str, option2: str,
                     option3: str = None, option4: str = None,
                     option5: str = None, option6: str = None,
                     option7: str = None, option8: str = None,
                     option9: str = None, option10: str = None):
        uid = interaction.user.id
        now = datetime.utcnow().timestamp()
        if uid in self.decide_cooldowns and now - self.decide_cooldowns[uid] < DECIDE_COOLDOWN_SECONDS:
            left = int(DECIDE_COOLDOWN_SECONDS - (now - self.decide_cooldowns[uid]))
            await interaction.response.send_message(f"⏳ Chill — {left}s left.", ephemeral=True); return

        options = [o for o in [option1, option2, option3, option4, option5,
                                option6, option7, option8, option9, option10] if o]
        result = random.choice(options)
        self.decide_cooldowns[uid] = now

        async with get_db() as db:
            await db.execute(
                "INSERT INTO decide_log (guild_id, options, result, decided_at) VALUES (?,?,?,?)",
                (interaction.guild_id, json.dumps(options), result, datetime.utcnow()))
            await db.commit()

        embed = discord.Embed(title="🎲 The Bonfire Has Spoken", color=discord.Color.from_str("#FF4500"))
        embed.add_field(name="Options",  value=" · ".join(options), inline=False)
        embed.add_field(name="Decision", value=f"**{result}**",    inline=False)
        embed.set_footer(text=f"Decided for {interaction.user.display_name} · No take-backs.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vibe", description="Get a random bonfire vibe check")
    async def vibe(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description=f"**{random.choice(VIBE_MESSAGES)}**",
            color=discord.Color.from_str("#FF4500"))
        embed.set_footer(text="Bonfire Bot · vibe certified 🔥")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(message="What to say")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message("✅", ephemeral=True)
        await interaction.channel.send(message)

    @app_commands.command(name="np", description="Share what you're currently listening to in #music-now")
    @app_commands.describe(song="Song / artist / album", mood="Optional mood tag")
    async def np(self, interaction: discord.Interaction, song: str, mood: str = None):
        music_ch = discord.utils.get(interaction.guild.text_channels, name="music-now")
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{song}**",
            color=discord.Color.from_str("#9B59B6"))
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        if mood:
            embed.add_field(name="Mood", value=mood)
        embed.set_footer(text="React 🔥 if you're on this rn")

        if music_ch and music_ch.id != interaction.channel_id:
            await music_ch.send(embed=embed)
            await interaction.response.send_message(f"✅ Posted to {music_ch.mention}", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        try:
            await msg.add_reaction("🔥")
        except Exception:
            pass

    @app_commands.command(name="members", description="Show all homiez cards — who's in the squad")
    async def members_cmd(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT user_id, name, bio FROM member_intros WHERE guild_id=? ORDER BY created_at ASC",
                (interaction.guild_id,)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message("No intros yet. Use `/intro` to start.", ephemeral=True); return

        embed = discord.Embed(title="🔥 The Squad", color=discord.Color.from_str("#FF4500"))
        for uid, name, bio in rows:
            m = interaction.guild.get_member(uid)
            handle = f"@{m.name}" if m else "left the server"
            snip   = (bio[:60] + "…") if len(bio) > 60 else bio
            embed.add_field(name=f"{name} ({handle})", value=f'*"{snip}"*', inline=False)
        embed.set_footer(text=f"{len(rows)} homiez at the bonfire")
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [VOICE]
# ─────────────────────────────────────────────────────────

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_core_or_owner(self, interaction):
        core = discord.utils.get(interaction.guild.roles, name="🔥 Core")
        og   = discord.utils.get(interaction.guild.roles, name="👑 OG")
        return (interaction.user == interaction.guild.owner or
                (core and core in interaction.user.roles) or
                (og and og in interaction.user.roles))

    @app_commands.command(name="lockvc", description="Lock all VCs — Core/OG only")
    async def lockvc(self, interaction: discord.Interaction):
        if not self._is_core_or_owner(interaction):
            await interaction.response.send_message("🔒 Core/OG only.", ephemeral=True); return
        locked = []
        for ch in interaction.guild.voice_channels:
            await ch.set_permissions(interaction.guild.default_role, connect=False)
            locked.append(ch.name)
        embed = discord.Embed(title="🔒 VCs Locked",
                              description=", ".join(locked), color=discord.Color.red())
        embed.set_footer(text=f"Locked by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unlockvc", description="Unlock all VCs — Core/OG only")
    async def unlockvc(self, interaction: discord.Interaction):
        if not self._is_core_or_owner(interaction):
            await interaction.response.send_message("🔓 Core/OG only.", ephemeral=True); return
        unlocked = []
        for ch in interaction.guild.voice_channels:
            await ch.set_permissions(interaction.guild.default_role, connect=True)
            unlocked.append(ch.name)
        embed = discord.Embed(title="🔓 VCs Unlocked",
                              description=", ".join(unlocked), color=discord.Color.green())
        embed.set_footer(text=f"Unlocked by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="limitvc", description="Set member limit on a VC")
    @app_commands.describe(limit="0–99 (0 = no limit)", channel="Target VC")
    async def limitvc(self, interaction: discord.Interaction, limit: int, channel: discord.VoiceChannel = None):
        if not self._is_core_or_owner(interaction):
            await interaction.response.send_message("Core/OG only.", ephemeral=True); return
        target = channel or (interaction.user.voice.channel if interaction.user.voice else None)
        if not target:
            await interaction.response.send_message("Join a VC or specify one.", ephemeral=True); return
        if not 0 <= limit <= 99:
            await interaction.response.send_message("Limit must be 0–99.", ephemeral=True); return
        await target.edit(user_limit=limit)
        desc = "No limit" if limit == 0 else f"{limit} members max"
        embed = discord.Embed(title="🎚️ VC Limit Set",
                              description=f"**{target.name}** → {desc}", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [FUN]
# ─────────────────────────────────────────────────────────

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roast_cooldowns = {}

    @app_commands.command(name="start", description="Kick off a session — kills the 'who's gonna initiate' paralysis")
    @app_commands.describe(activity="Type of hang", ping="Ping @here?", custom="Custom activity name")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Game Night 🎮",  value="game night"),
        app_commands.Choice(name="Movie Night 🎬", value="movie night"),
        app_commands.Choice(name="Chill 😌",       value="chill"),
        app_commands.Choice(name="Custom",         value="custom"),
    ])
    async def start(self, interaction: discord.Interaction,
                    activity: str, ping: bool = False, custom: str = None):
        label = custom if (activity == "custom" and custom) else activity
        emoji = {"game night": "🎮", "movie night": "🎬", "chill": "😌"}.get(activity, "🔥")
        vc = next((v for v in interaction.guild.voice_channels
                   if "main" in v.name.lower() or "chill" in v.name.lower() or "game" in v.name.lower()),
                  None)
        embed = discord.Embed(
            title=f"{emoji} {label.title()} — THE BONFIRE IS CALLING",
            description=f"**{interaction.user.display_name}** is starting something. Who's pulling up?",
            color=discord.Color.from_str("#FF4500"))
        if vc:
            embed.add_field(name="VC", value=vc.mention, inline=True)
        embed.add_field(name="Activity", value=label.title(), inline=True)
        embed.set_footer(text="React ✅ to show you're in")
        await interaction.response.send_message(content="@here" if ping else "", embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")

    @app_commands.command(name="roast", description="Roast a homie — opt-in fun only")
    @app_commands.describe(target="Who's getting cooked?")
    async def roast(self, interaction: discord.Interaction, target: discord.Member):
        uid = interaction.user.id
        now = datetime.utcnow().timestamp()
        if uid in self.roast_cooldowns and now - self.roast_cooldowns[uid] < ROAST_COOLDOWN_SECONDS:
            left = int(ROAST_COOLDOWN_SECONDS - (now - self.roast_cooldowns[uid]))
            await interaction.response.send_message(f"⏳ Cool it — {left}s left.", ephemeral=True); return
        if target.id == self.bot.user.id:
            await interaction.response.send_message("I roast. I don't get roasted. 😤", ephemeral=True); return
        self.roast_cooldowns[uid] = now
        embed = discord.Embed(
            description=f"🔥 {random.choice(ROAST_MESSAGES).format(target=target.display_name)}",
            color=discord.Color.red())
        embed.set_footer(text=f"Requested by {interaction.user.display_name} · opt-in fun only")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tod", description="Truth or Dare — server edition")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Truth 🤔", value="truth"),
        app_commands.Choice(name="Dare 😈",  value="dare"),
    ])
    async def tod(self, interaction: discord.Interaction, choice: str):
        if choice == "truth":
            text  = random.choice(TOD_TRUTHS)
            color = discord.Color.blue()
            title = "🤔 TRUTH"
        else:
            text  = random.choice(TOD_DARES)
            color = discord.Color.red()
            title = "😈 DARE"
        embed = discord.Embed(title=title, description=text, color=color)
        embed.set_footer(text=f"Asked by {interaction.user.display_name} · no chickening out")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hottake", description="Post a hot take — squad votes agree/disagree")
    @app_commands.describe(take="Drop the take. Make it spicy.")
    async def hottake(self, interaction: discord.Interaction, take: str):
        embed = discord.Embed(
            title="🌶️ HOT TAKE",
            description=f'**"{take}"**',
            color=discord.Color.from_str("#FF4500"))
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="✅ Agree", value="0", inline=True)
        embed.add_field(name="❌ Disagree", value="0", inline=True)
        embed.set_footer(text="React ✅ or ❌ to vote")
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        async with get_db() as db:
            await db.execute(
                "INSERT INTO hot_takes (guild_id, user_id, take, message_id) VALUES (?,?,?,?)",
                (interaction.guild_id, interaction.user.id, take, msg.id))
            await db.commit()

        # Mirror to hot-takes channel if posted elsewhere
        hot_ch = discord.utils.get(interaction.guild.text_channels, name="hot-takes")
        if hot_ch and hot_ch.id != interaction.channel_id:
            mirror = await hot_ch.send(embed=embed)
            await mirror.add_reaction("✅")
            await mirror.add_reaction("❌")


# ─────────────────────────────────────────────────────────
# [LFG]
# ─────────────────────────────────────────────────────────

class LFG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lfg", description="Looking for group — no more 'who's down?' threads that die")
    @app_commands.describe(game="What game?", size="How many needed? (2–20)")
    async def lfg(self, interaction: discord.Interaction, game: str, size: int):
        if not 2 <= size <= 20:
            await interaction.response.send_message("Size must be 2–20.", ephemeral=True); return
        expires_at = datetime.utcnow() + timedelta(minutes=LFG_EXPIRY_MINUTES)
        members    = [interaction.user.id]

        embed = discord.Embed(title=f"🎮 LFG — {game}", color=discord.Color.from_str("#9B59B6"))
        embed.add_field(name="Game",    value=game, inline=True)
        embed.add_field(name="Spots",   value=f"1/{size}", inline=True)
        embed.add_field(name="Players", value=interaction.user.mention, inline=False)
        embed.add_field(name="Expires", value=f"<t:{int(expires_at.timestamp())}:R>", inline=False)
        embed.set_footer(text="React ✅ to join")

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")

        async with get_db() as db:
            await db.execute(
                "INSERT INTO lfg_lobbies (guild_id,channel_id,message_id,creator_id,game,size,members,expires_at)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (interaction.guild_id, interaction.channel_id, msg.id,
                 interaction.user.id, game, size, json.dumps(members), expires_at))
            await db.commit()

        async def expire():
            await asyncio.sleep(LFG_EXPIRY_MINUTES * 60)
            async with get_db() as db:
                async with db.execute("SELECT id FROM lfg_lobbies WHERE message_id=?", (msg.id,)) as cur:
                    row = await cur.fetchone()
                if row:
                    await db.execute("DELETE FROM lfg_lobbies WHERE message_id=?", (msg.id,))
                    await db.commit()
                    try:
                        await msg.edit(embed=discord.Embed(
                            title=f"⏰ LFG Expired — {game}",
                            description="Lobby didn't fill in time.",
                            color=discord.Color.greyple()))
                    except Exception:
                        pass
        asyncio.create_task(expire())


# ─────────────────────────────────────────────────────────
# [REMINDERS]
# ─────────────────────────────────────────────────────────

def _parse_time(time_str: str):
    m = re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?', time_str.strip().lower())
    if not m or not any(m.groups()):
        return None
    total = int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60
    return total if total > 0 else None


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _fire(self, channel_id, user_id, message, reminder_id, delay):
        await asyncio.sleep(delay)
        ch = self.bot.get_channel(channel_id)
        if ch:
            u = self.bot.get_user(user_id)
            embed = discord.Embed(title="⏰ Reminder", description=message, color=discord.Color.yellow())
            embed.set_footer(text="Set via /remind")
            await ch.send(content=u.mention if u else f"<@{user_id}>", embed=embed)
        async with get_db() as db:
            await db.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
            await db.commit()

    @app_commands.command(name="remind", description="Set a reminder (30m / 2h / 1h30m)")
    @app_commands.describe(time="When", message="What to remind you about")
    async def remind(self, interaction: discord.Interaction, time: str, message: str):
        secs = _parse_time(time)
        if not secs:
            await interaction.response.send_message("Use `30m`, `2h`, or `1h30m`.", ephemeral=True); return
        trigger = datetime.utcnow() + timedelta(seconds=secs)
        async with get_db() as db:
            cur = await db.execute(
                "INSERT INTO reminders (guild_id,channel_id,user_id,message,trigger_at) VALUES (?,?,?,?,?)",
                (interaction.guild_id, interaction.channel_id, interaction.user.id, message, trigger))
            await db.commit()
            rid = cur.lastrowid
        asyncio.create_task(self._fire(interaction.channel_id, interaction.user.id, message, rid, secs))
        embed = discord.Embed(title="✅ Reminder Set", color=discord.Color.green())
        embed.add_field(name="Message", value=message)
        embed.add_field(name="When",    value=f"<t:{int(trigger.timestamp())}:R>")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="plan", description="Plan a group activity with a shared reminder")
    @app_commands.describe(time="When (e.g. 30m, 2h)", activity="What's happening?")
    async def plan(self, interaction: discord.Interaction, time: str, activity: str):
        secs = _parse_time(time)
        if not secs:
            await interaction.response.send_message("Use `30m`, `2h`, or `1h30m`.", ephemeral=True); return
        trigger = datetime.utcnow() + timedelta(seconds=secs)
        async with get_db() as db:
            cur = await db.execute(
                "INSERT INTO reminders (guild_id,channel_id,user_id,message,trigger_at) VALUES (?,?,?,?,?)",
                (interaction.guild_id, interaction.channel_id, interaction.user.id, activity, trigger))
            await db.commit()
            rid = cur.lastrowid
        embed = discord.Embed(title="📅 Activity Planned",
                              description=f"**{activity}** starts in **{time}**",
                              color=discord.Color.blue())
        embed.add_field(name="Scheduled by", value=interaction.user.mention)
        embed.add_field(name="When",         value=f"<t:{int(trigger.timestamp())}:R>")
        embed.set_footer(text="I'll ping here when it's time.")
        await interaction.response.send_message(embed=embed)
        asyncio.create_task(
            self._fire(interaction.channel_id, interaction.user.id, f"🔔 Time for **{activity}**!", rid, secs))

    @app_commands.command(name="event", description="Plan a real IRL or online event with RSVP")
    @app_commands.describe(
        title="Event name",
        when="When (e.g. 2h or date like 'Saturday 8pm')",
        description="What's the plan?",
        location="IRL location or 'Online'")
    async def event(self, interaction: discord.Interaction,
                    title: str, when: str, description: str = None, location: str = "Online"):
        secs = _parse_time(when)
        trigger = datetime.utcnow() + timedelta(seconds=secs) if secs else None

        embed = discord.Embed(
            title=f"📅 {title}",
            description=description or "No description yet.",
            color=discord.Color.from_str("#4ECDC4"))
        embed.add_field(name="📍 Location", value=location,   inline=True)
        if trigger:
            embed.add_field(name="⏰ When", value=f"<t:{int(trigger.timestamp())}:R>", inline=True)
        else:
            embed.add_field(name="⏰ When", value=when, inline=True)
        embed.add_field(name="✅ Going",    value="0", inline=True)
        embed.add_field(name="❌ Not Going", value="0", inline=True)
        embed.set_author(name=f"Organized by {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="React ✅ to RSVP · ❌ if you can't make it")

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        if secs and trigger:
            async with get_db() as db:
                cur = await db.execute(
                    "INSERT INTO events (guild_id,channel_id,creator_id,title,description,location,event_time,message_id)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (interaction.guild_id, interaction.channel_id, interaction.user.id,
                     title, description, location, trigger, msg.id))
                await db.commit()
            async def remind_event():
                await asyncio.sleep(max(0, secs - 300))  # ping 5 min before
                ch = self.bot.get_channel(interaction.channel_id)
                if ch:
                    await ch.send(f"@here 🔔 **{title}** is starting in 5 minutes!")
                await asyncio.sleep(300)
                if ch:
                    await ch.send(f"@here 🎉 **{title}** is happening NOW!")
            asyncio.create_task(remind_event())


# ─────────────────────────────────────────────────────────
# [HIGHLIGHTS]
# ─────────────────────────────────────────────────────────

class Highlights(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def post_highlight(self, message: discord.Message):
        async with get_db() as db:
            async with db.execute("SELECT message_id FROM highlights WHERE message_id=?",
                                  (message.id,)) as cur:
                if await cur.fetchone():
                    return
        ch = discord.utils.get(message.guild.text_channels, name="highlights")
        if not ch:
            return
        embed = discord.Embed(description=message.content or "*[media]*",
                              color=discord.Color.gold(), timestamp=message.created_at)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="Source",  value=f"[Jump]({message.jump_url})", inline=True)
        embed.add_field(name="Channel", value=message.channel.mention,       inline=True)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        embed.set_footer(text="⭐ Bonfire Highlight")
        await ch.send(embed=embed)
        async with get_db() as db:
            await db.execute(
                "INSERT OR IGNORE INTO highlights (message_id,guild_id,channel_id,author_id,content,jump_url)"
                " VALUES (?,?,?,?,?,?)",
                (message.id, message.guild.id, message.channel.id,
                 message.author.id, message.content, message.jump_url))
            await db.commit()

    @app_commands.command(name="highlights", description="See recent bonfire highlights")
    async def highlights_cmd(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT content,jump_url,posted_at FROM highlights WHERE guild_id=?"
                " ORDER BY posted_at DESC LIMIT 5", (interaction.guild_id,)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message("No highlights yet. React ⭐ to start!", ephemeral=True); return
        embed = discord.Embed(title="⭐ Bonfire Highlights", color=discord.Color.gold())
        for content, url, _ in rows:
            snip = (content[:80] + "…") if content and len(content) > 80 else (content or "[media]")
            embed.add_field(name=snip, value=f"[Jump]({url})", inline=False)
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [LORE]
# ─────────────────────────────────────────────────────────

class Lore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lore", description="The lore archive — inside jokes, bits, legendary moments")
    @app_commands.describe(action="What to do", text="Lore text (for add)", member="Filter by member")
    @app_commands.choices(action=[
        app_commands.Choice(name="Random entry",   value="random"),
        app_commands.Choice(name="Add lore entry", value="add"),
        app_commands.Choice(name="List recent",    value="list"),
    ])
    async def lore(self, interaction: discord.Interaction,
                   action: str = "random", text: str = None, member: discord.Member = None):
        if action == "add":
            if not text:
                await interaction.response.send_message("Provide text with the `text` option.", ephemeral=True); return
            async with get_db() as db:
                await db.execute("INSERT INTO lore (guild_id,author_id,target_id,content) VALUES (?,?,?,?)",
                                 (interaction.guild_id, interaction.user.id,
                                  member.id if member else None, text))
                await db.commit()
            embed = discord.Embed(title="📖 Lore Added", description=text, color=discord.Color.purple())
            embed.set_footer(text=f"Logged by {interaction.user.display_name}")
            await interaction.response.send_message(embed=embed)

        elif action == "random":
            async with get_db() as db:
                q = ("SELECT content,author_id,created_at FROM lore WHERE guild_id=?"
                     + (" AND target_id=?" if member else "") + " ORDER BY RANDOM() LIMIT 1")
                args = (interaction.guild_id, member.id) if member else (interaction.guild_id,)
                async with db.execute(q, args) as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.response.send_message(
                    "No lore yet. React 📖 on any message or use `/lore add`.", ephemeral=True); return
            content, author_id, created_at = row
            author = interaction.guild.get_member(author_id)
            embed  = discord.Embed(title="📖 Bonfire Lore", description=content, color=discord.Color.purple())
            embed.set_footer(text=f"Logged by {author.display_name if author else 'Unknown'} · {str(created_at)[:10]}")
            await interaction.response.send_message(embed=embed)

        elif action == "list":
            async with get_db() as db:
                async with db.execute(
                    "SELECT content,author_id,created_at FROM lore WHERE guild_id=?"
                    " ORDER BY created_at DESC LIMIT 8", (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No lore entries yet.", ephemeral=True); return
            embed = discord.Embed(title="📖 Recent Lore", color=discord.Color.purple())
            for content, author_id, created_at in rows:
                author = interaction.guild.get_member(author_id)
                snip   = (content[:60] + "…") if len(content) > 60 else content
                embed.add_field(name=snip,
                                value=f"by {author.display_name if author else 'Unknown'} · {str(created_at)[:10]}",
                                inline=False)
            await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [QUOTES]
# ─────────────────────────────────────────────────────────

class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quote", description="Pull a saved quote from the archive")
    @app_commands.describe(member="Get a quote from a specific person")
    async def quote(self, interaction: discord.Interaction, member: discord.Member = None):
        async with get_db() as db:
            q = ("SELECT content,author_id,jump_url,created_at FROM quotes WHERE guild_id=?"
                 + (" AND author_id=?" if member else "") + " ORDER BY RANDOM() LIMIT 1")
            args = (interaction.guild_id, member.id) if member else (interaction.guild_id,)
            async with db.execute(q, args) as cur:
                row = await cur.fetchone()
        if not row:
            await interaction.response.send_message(
                f"No quotes for {member.display_name} yet." if member
                else "No quotes saved yet. React 💬 on a message.", ephemeral=True); return
        content, author_id, jump_url, created_at = row
        author = interaction.guild.get_member(author_id)
        embed  = discord.Embed(description=f'"{content}"', color=discord.Color.teal())
        embed.set_author(name=author.display_name if author else "Unknown",
                         icon_url=author.display_avatar.url if author else None)
        if jump_url:
            embed.add_field(name="Source", value=f"[Jump]({jump_url})")
        embed.set_footer(text=f"Saved · {str(created_at)[:10]}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quotes", description="List recent saved quotes")
    async def quotes_list(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT content,author_id,created_at FROM quotes WHERE guild_id=?"
                " ORDER BY created_at DESC LIMIT 8", (interaction.guild_id,)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message("No quotes yet. React 💬 to start.", ephemeral=True); return
        embed = discord.Embed(title="💬 Quotes Wall", color=discord.Color.teal())
        for content, author_id, _ in rows:
            author = interaction.guild.get_member(author_id)
            snip   = (content[:60] + "…") if len(content) > 60 else content
            embed.add_field(name=f'"{snip}"',
                            value=f"— {author.display_name if author else 'Unknown'}", inline=False)
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [BEEF]
# ─────────────────────────────────────────────────────────

class Beef(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="beef", description="Start, resolve, or view the beef leaderboard")
    @app_commands.describe(action="Action", member="Who's the beef with?", reason="What's it about?")
    @app_commands.choices(action=[
        app_commands.Choice(name="Start beef",   value="start"),
        app_commands.Choice(name="Resolve beef", value="resolve"),
        app_commands.Choice(name="Leaderboard",  value="leaderboard"),
    ])
    async def beef(self, interaction: discord.Interaction,
                   action: str, member: discord.Member = None, reason: str = None):
        if action == "start":
            if not member:
                await interaction.response.send_message("Pick someone.", ephemeral=True); return
            if member.id == interaction.user.id:
                await interaction.response.send_message("Can't beef yourself 💀", ephemeral=True); return
            async with get_db() as db:
                async with db.execute(
                    "SELECT id FROM beef WHERE guild_id=? AND initiator_id=? AND target_id=? AND resolved=0",
                    (interaction.guild_id, interaction.user.id, member.id)) as cur:
                    if await cur.fetchone():
                        await interaction.response.send_message(
                            f"Already beefing {member.display_name}.", ephemeral=True); return
                cur = await db.execute(
                    "INSERT INTO beef (guild_id,initiator_id,target_id,reason) VALUES (?,?,?,?)",
                    (interaction.guild_id, interaction.user.id, member.id, reason or "no reason given"))
                await db.commit()
                beef_id = cur.lastrowid
            embed = discord.Embed(title="🥩 BEEF INCOMING", color=discord.Color.red())
            embed.add_field(name="From",   value=interaction.user.mention, inline=True)
            embed.add_field(name="With",   value=member.mention,            inline=True)
            embed.add_field(name="Reason", value=reason or "no reason given", inline=False)
            embed.add_field(name="ID",     value=f"#{beef_id}",             inline=True)
            embed.set_footer(text="React 🏆 to vote winner · 🤝 to call truce")
            await interaction.response.send_message(embed=embed)
            msg = await interaction.original_response()
            await msg.add_reaction("🏆")
            await msg.add_reaction("🤝")
            log_ch = discord.utils.get(interaction.guild.text_channels, name="beef-log")
            if log_ch and log_ch.id != interaction.channel_id:
                await log_ch.send(embed=embed)

        elif action == "resolve":
            if not member:
                await interaction.response.send_message("Specify who.", ephemeral=True); return
            async with get_db() as db:
                async with db.execute(
                    "SELECT id FROM beef WHERE guild_id=? AND resolved=0 AND"
                    " ((initiator_id=? AND target_id=?) OR (initiator_id=? AND target_id=?))",
                    (interaction.guild_id, interaction.user.id, member.id, member.id, interaction.user.id)) as cur:
                    row = await cur.fetchone()
                if not row:
                    await interaction.response.send_message(f"No active beef with {member.display_name}.", ephemeral=True); return
                await db.execute("UPDATE beef SET resolved=1 WHERE id=?", (row[0],))
                await db.commit()
            embed = discord.Embed(title="🤝 Beef Squashed",
                                  description=f"{interaction.user.mention} and {member.mention} called it.",
                                  color=discord.Color.green())
            await interaction.response.send_message(embed=embed)

        elif action == "leaderboard":
            async with get_db() as db:
                async with db.execute(
                    "SELECT initiator_id, COUNT(*) cnt FROM beef WHERE guild_id=?"
                    " GROUP BY initiator_id ORDER BY cnt DESC LIMIT 10", (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No beefs yet.", ephemeral=True); return
            embed = discord.Embed(title="🥩 Beef Leaderboard", color=discord.Color.red())
            for i, (uid, cnt) in enumerate(rows, 1):
                m = interaction.guild.get_member(uid)
                embed.add_field(name=f"#{i} {m.display_name if m else uid}",
                                value=f"{cnt} beef(s) started", inline=False)
            await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [VIBE]
# ─────────────────────────────────────────────────────────

class VibeCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vibecheck", description="Rate the group energy — anonymous 1–5")
    @app_commands.describe(score="1 (dead) to 5 (peak)")
    async def vibecheck(self, interaction: discord.Interaction, score: int):
        if not 1 <= score <= 5:
            await interaction.response.send_message("Score must be 1–5.", ephemeral=True); return
        today = datetime.utcnow().date().isoformat()
        async with get_db() as db:
            async with db.execute(
                "SELECT id FROM vibe_checks WHERE guild_id=? AND user_id=? AND DATE(created_at)=?",
                (interaction.guild_id, interaction.user.id, today)) as cur:
                if await cur.fetchone():
                    await interaction.response.send_message("Already submitted today.", ephemeral=True); return
            await db.execute("INSERT INTO vibe_checks (guild_id,user_id,score) VALUES (?,?,?)",
                             (interaction.guild_id, interaction.user.id, score))
            await db.commit()
            async with db.execute(
                "SELECT AVG(score), COUNT(*) FROM vibe_checks WHERE guild_id=? AND DATE(created_at)=?",
                (interaction.guild_id, today)) as cur:
                avg, count = await cur.fetchone()
        bars = "█" * score + "░" * (5 - score)
        embed = discord.Embed(title="📊 Vibe Check", color=discord.Color.purple())
        embed.add_field(name="Your Score",           value=f"{bars} ({score}/5)", inline=False)
        embed.add_field(name="Server Average Today", value=f"{avg:.1f}/5 ({count} votes)", inline=False)
        embed.set_footer(text="Anonymous · aggregate only")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="vibereport", description="See this week's vibe report")
    async def vibereport(self, interaction: discord.Interaction):
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        async with get_db() as db:
            async with db.execute(
                "SELECT DATE(created_at) day, AVG(score) avg, COUNT(*) cnt"
                " FROM vibe_checks WHERE guild_id=? AND created_at>=?"
                " GROUP BY day ORDER BY day", (interaction.guild_id, week_ago)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message("No vibe data this week.", ephemeral=True); return
        embed = discord.Embed(title="📈 Weekly Vibe Report", color=discord.Color.purple())
        for day, avg, cnt in rows:
            bars = "█" * round(avg) + "░" * (5 - round(avg))
            embed.add_field(name=day, value=f"{bars} {avg:.1f}/5 ({cnt} votes)", inline=False)
        overall = sum(r[1] for r in rows) / len(rows)
        embed.set_footer(text=f"7-day average: {overall:.1f}/5")
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [STREAK]
# ─────────────────────────────────────────────────────────

class Streak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def record_activity(self, guild_id: int):
        today     = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        async with get_db() as db:
            async with db.execute(
                "SELECT current_streak,last_active_date,longest_streak FROM streaks WHERE guild_id=?",
                (guild_id,)) as cur:
                row = await cur.fetchone()
            if not row:
                await db.execute(
                    "INSERT INTO streaks (guild_id,current_streak,last_active_date,longest_streak) VALUES (?,1,?,1)",
                    (guild_id, today))
                await db.commit()
                return
            current, last, longest = row
            if last == today:
                return
            new_streak  = (current + 1) if last == yesterday else 1
            new_longest = max(longest, new_streak)
            await db.execute(
                "UPDATE streaks SET current_streak=?,last_active_date=?,longest_streak=? WHERE guild_id=?",
                (new_streak, today, new_longest, guild_id))
            await db.commit()
            if last not in (today, yesterday) and last and current > 1:
                guild = self.bot.get_guild(guild_id)
                if guild:
                    ch = (discord.utils.get(guild.text_channels, name="general") or
                          discord.utils.get(guild.text_channels, name="status"))
                    if ch:
                        await ch.send(embed=discord.Embed(
                            title="💔 STREAK BROKEN",
                            description=f"The {current}-day bonfire streak just ended. Restart it today.",
                            color=discord.Color.red()))

    @app_commands.command(name="streak", description="Check the server's daily activity streak")
    async def streak(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT current_streak,last_active_date,longest_streak FROM streaks WHERE guild_id=?",
                (interaction.guild_id,)) as cur:
                row = await cur.fetchone()
        if not row or row[0] == 0:
            await interaction.response.send_message("No streak yet. Chat to start one!", ephemeral=True); return
        current, last, longest = row
        alive = last == date.today().isoformat()
        fire  = "🔥" * min(current, 10)
        embed = discord.Embed(title="🔥 Bonfire Streak",
                              color=discord.Color.orange() if alive else discord.Color.greyple())
        embed.add_field(name="Current", value=f"{current} day(s) {fire}", inline=True)
        embed.add_field(name="Best",    value=f"{longest} day(s)",         inline=True)
        embed.add_field(name="Last Active", value=last or "Never",         inline=True)
        embed.set_footer(text="Keep the fire burning." if alive else "⚠️ Streak at risk — someone talk!")
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [WRAPPED]
# ─────────────────────────────────────────────────────────

class Wrapped(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wrapped", description="Monthly Bonfire Wrapped — your squad's recap")
    async def wrapped(self, interaction: discord.Interaction):
        await interaction.response.defer()
        gid       = interaction.guild_id
        month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()

        async with get_db() as db:
            async with db.execute(
                "SELECT user_id, COUNT(*) cnt FROM activity_log"
                " WHERE guild_id=? AND created_at>=? AND activity_type='message'"
                " GROUP BY user_id ORDER BY cnt DESC LIMIT 5", (gid, month_ago)) as cur:
                top_talkers = await cur.fetchall()
            async with db.execute(
                "SELECT COUNT(*) FROM lore WHERE guild_id=? AND created_at>=?", (gid, month_ago)) as cur:
                lore_count = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM highlights WHERE guild_id=? AND posted_at>=?", (gid, month_ago)) as cur:
                highlight_count = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT author_id, COUNT(*) cnt FROM quotes WHERE guild_id=? AND created_at>=?"
                " GROUP BY author_id ORDER BY cnt DESC LIMIT 1", (gid, month_ago)) as cur:
                top_quoted = await cur.fetchone()
            async with db.execute(
                "SELECT initiator_id, COUNT(*) cnt FROM beef WHERE guild_id=? AND created_at>=?"
                " GROUP BY initiator_id ORDER BY cnt DESC LIMIT 1", (gid, month_ago)) as cur:
                top_beef = await cur.fetchone()
            async with db.execute(
                "SELECT result, COUNT(*) cnt FROM decide_log WHERE guild_id=? AND decided_at>=?"
                " GROUP BY result ORDER BY cnt DESC LIMIT 1", (gid, month_ago)) as cur:
                top_decide = await cur.fetchone()
            async with db.execute(
                "SELECT COUNT(*) FROM member_intros WHERE guild_id=? AND created_at>=?", (gid, month_ago)) as cur:
                new_homiez = (await cur.fetchone())[0]

        now = datetime.utcnow()
        embed = discord.Embed(
            title=f"🔥 Bonfire Wrapped — {now.strftime('%B %Y')}",
            description="Spotify Wrapped but make it the squad.",
            color=discord.Color.from_str("#FF4500"))

        if top_talkers:
            lines = []
            for i, (uid, cnt) in enumerate(top_talkers, 1):
                m = interaction.guild.get_member(uid)
                lines.append(f"**#{i}** {m.display_name if m else uid} — {cnt} messages")
            embed.add_field(name="💬 Most Active", value="\n".join(lines), inline=False)
        embed.add_field(name="📖 Lore Added",      value=str(lore_count),      inline=True)
        embed.add_field(name="⭐ Highlights",       value=str(highlight_count), inline=True)
        embed.add_field(name="🆕 New Homiez",       value=str(new_homiez),      inline=True)
        if top_quoted:
            m = interaction.guild.get_member(top_quoted[0])
            embed.add_field(name="💬 Most Quoted", value=f"{m.display_name if m else top_quoted[0]} ({top_quoted[1]}x)", inline=True)
        if top_beef:
            m = interaction.guild.get_member(top_beef[0])
            embed.add_field(name="🥩 Beef King",   value=f"{m.display_name if m else top_beef[0]} ({top_beef[1]})", inline=True)
        if top_decide:
            embed.add_field(name="🎲 Most Decided", value=top_decide[0], inline=True)
        embed.set_footer(text=f"Generated {now.strftime('%B %d, %Y')} · Bonfire Bot")
        await interaction.followup.send(embed=embed)


# ─────────────────────────────────────────────────────────
# [CLUTCH]
# ─────────────────────────────────────────────────────────

class Clutch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clutch", description="Opt in/out of Clutch Mode pings when someone's alone in VC")
    @app_commands.choices(action=[
        app_commands.Choice(name="Opt in",  value="in"),
        app_commands.Choice(name="Opt out", value="out"),
        app_commands.Choice(name="Status",  value="status"),
    ])
    async def clutch(self, interaction: discord.Interaction, action: str = "status"):
        if action == "in":
            async with get_db() as db:
                await db.execute("INSERT OR IGNORE INTO clutch_opt_in (guild_id,user_id) VALUES (?,?)",
                                 (interaction.guild_id, interaction.user.id))
                await db.commit()
            await interaction.response.send_message("✅ You're in the Clutch pool.", ephemeral=True)
        elif action == "out":
            async with get_db() as db:
                await db.execute("DELETE FROM clutch_opt_in WHERE guild_id=? AND user_id=?",
                                 (interaction.guild_id, interaction.user.id))
                await db.commit()
            await interaction.response.send_message("👋 Opted out.", ephemeral=True)
        elif action == "status":
            async with get_db() as db:
                async with db.execute("SELECT user_id FROM clutch_opt_in WHERE guild_id=?",
                                      (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            opted = [m for r in rows if (m := interaction.guild.get_member(r[0]))]
            if not opted:
                await interaction.response.send_message("Nobody opted in. Use `/clutch in`.", ephemeral=True); return
            await interaction.response.send_message(
                f"🔔 Clutch pool ({len(opted)}): {', '.join(m.display_name for m in opted)}", ephemeral=True)

    async def check_clutch(self, guild, channel, lone):
        now = datetime.utcnow()
        async with get_db() as db:
            async with db.execute(
                "SELECT last_ping FROM clutch_cooldown WHERE guild_id=? AND channel_id=?",
                (guild.id, channel.id)) as cur:
                row = await cur.fetchone()
        if row and (now - datetime.fromisoformat(row[0])).total_seconds() < CLUTCH_COOLDOWN_MINUTES * 60:
            return
        async with get_db() as db:
            async with db.execute("SELECT user_id FROM clutch_opt_in WHERE guild_id=?", (guild.id,)) as cur:
                opt_ids = {r[0] for r in await cur.fetchall()}
        eligible = [m for m in guild.members
                    if m.id in opt_ids and m.id != lone.id and not m.bot
                    and m.status != discord.Status.offline
                    and (not m.voice or not m.voice.channel)]
        if not eligible:
            return
        pinged = random.choice(eligible)
        msg    = random.choice(CLUTCH_MESSAGES).format(lonely=lone.display_name, pinged=pinged.mention)
        ch = discord.utils.get(guild.text_channels, name="general")
        if ch:
            await ch.send(msg)
        async with get_db() as db:
            await db.execute(
                "INSERT INTO clutch_cooldown (guild_id,channel_id,last_ping) VALUES (?,?,?)"
                " ON CONFLICT(guild_id,channel_id) DO UPDATE SET last_ping=excluded.last_ping",
                (guild.id, channel.id, now.isoformat()))
            await db.commit()


# ─────────────────────────────────────────────────────────
# [ROLES]  — auto role assignment by behavior
# ─────────────────────────────────────────────────────────

class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _ensure_tracking(self, guild_id: int, user_id: int):
        async with get_db() as db:
            await db.execute(
                "INSERT OR IGNORE INTO role_tracking (guild_id, user_id) VALUES (?,?)",
                (guild_id, user_id))
            await db.commit()

    async def increment_messages(self, guild_id: int, user_id: int):
        await self._ensure_tracking(guild_id, user_id)
        async with get_db() as db:
            await db.execute(
                "UPDATE role_tracking SET message_count = message_count + 1 WHERE guild_id=? AND user_id=?",
                (guild_id, user_id))
            await db.commit()
            async with db.execute(
                "SELECT message_count FROM role_tracking WHERE guild_id=? AND user_id=?",
                (guild_id, user_id)) as cur:
                row = await cur.fetchone()
        if row and row[0] >= REGULAR_MESSAGE_THRESHOLD:
            guild  = self.bot.get_guild(guild_id)
            member = guild.get_member(user_id) if guild else None
            if member:
                regular_role = discord.utils.get(guild.roles, name="💬 Regular")
                lurker_role  = discord.utils.get(guild.roles, name="👤 Lurker")
                if regular_role and regular_role not in member.roles:
                    await member.add_roles(regular_role, reason="Earned Regular via 50 messages")
                    if lurker_role and lurker_role in member.roles:
                        await member.remove_roles(lurker_role, reason="Upgraded to Regular")
                    ch = discord.utils.get(guild.text_channels, name="general")
                    if ch:
                        await ch.send(
                            embed=discord.Embed(
                                description=f"🎉 {member.mention} earned the **💬 Regular** role. They're a real one now.",
                                color=discord.Color.from_str("#4ECDC4")))

    async def log_late_vc(self, guild_id: int, user_id: int):
        hour = datetime.utcnow().hour
        if not (0 <= hour < 4 or 22 <= hour <= 23):
            return
        await self._ensure_tracking(guild_id, user_id)
        async with get_db() as db:
            await db.execute(
                "UPDATE role_tracking SET late_vc_count = late_vc_count + 1 WHERE guild_id=? AND user_id=?",
                (guild_id, user_id))
            await db.commit()
            async with db.execute(
                "SELECT late_vc_count FROM role_tracking WHERE guild_id=? AND user_id=?",
                (guild_id, user_id)) as cur:
                row = await cur.fetchone()
        if row and row[0] >= NIGHT_OWL_LATE_VC_THRESHOLD:
            guild  = self.bot.get_guild(guild_id)
            member = guild.get_member(user_id) if guild else None
            if member:
                owl_role = discord.utils.get(guild.roles, name="🌙 Night Owl")
                if owl_role and owl_role not in member.roles:
                    await member.add_roles(owl_role, reason="Earned Night Owl — 5 late VC sessions")
                    ch = discord.utils.get(guild.text_channels, name="general")
                    if ch:
                        await ch.send(
                            embed=discord.Embed(
                                description=f"🌙 {member.mention} earned **🌙 Night Owl**. Never sleeps, always there.",
                                color=discord.Color.from_str("#2C3E50")))


# ─────────────────────────────────────────────────────────
# [STORY]  — campfire collaborative story
# ─────────────────────────────────────────────────────────

class Story(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="story", description="Add to the campfire story — one line at a time")
    @app_commands.describe(line="Your line (max 200 chars)")
    async def story(self, interaction: discord.Interaction, line: str):
        if len(line) > 200:
            await interaction.response.send_message("Keep it under 200 chars.", ephemeral=True); return
        async with get_db() as db:
            # Check if previous line was by same user
            async with db.execute(
                "SELECT author_id FROM story WHERE guild_id=? ORDER BY id DESC LIMIT 1",
                (interaction.guild_id,)) as cur:
                last = await cur.fetchone()
            if last and last[0] == interaction.user.id:
                await interaction.response.send_message(
                    "You wrote the last line. Let someone else add one first.", ephemeral=True); return

            # Start a new story if none exists or if it's been > 7 days
            async with db.execute(
                "SELECT COUNT(*), MAX(created_at) FROM story WHERE guild_id=?", (interaction.guild_id,)) as cur:
                count, last_at = await cur.fetchone()

            if count == 0:
                starter = random.choice(STORY_STARTERS)
                await db.execute("INSERT INTO story (guild_id, author_id, line) VALUES (?,?,?)",
                                 (interaction.guild_id, self.bot.user.id, starter))

            await db.execute("INSERT INTO story (guild_id, author_id, line) VALUES (?,?,?)",
                             (interaction.guild_id, interaction.user.id, line))
            await db.commit()

            # Fetch last 5 lines for context
            async with db.execute(
                "SELECT author_id, line FROM story WHERE guild_id=? ORDER BY id DESC LIMIT 5",
                (interaction.guild_id,)) as cur:
                recent = list(reversed(await cur.fetchall()))

            async with db.execute(
                "SELECT COUNT(*) FROM story WHERE guild_id=?", (interaction.guild_id,)) as cur:
                total_lines = (await cur.fetchone())[0]

        embed = discord.Embed(title="🏕️ Campfire Story", color=discord.Color.orange())
        story_text = ""
        for aid, l in recent:
            author = interaction.guild.get_member(aid)
            name   = author.display_name if author else ("Bot" if aid == self.bot.user.id else "Unknown")
            story_text += f"*{l}*  — {name}\n"
        embed.description = story_text
        embed.set_footer(text=f"Line {total_lines} · Add yours with /story")
        await interaction.response.send_message(embed=embed)

        # Also post to campfire-story channel
        story_ch = discord.utils.get(interaction.guild.text_channels, name="campfire-story")
        if story_ch and story_ch.id != interaction.channel_id:
            await story_ch.send(embed=embed)

    @app_commands.command(name="fullstory", description="Read the full campfire story so far")
    async def fullstory(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT author_id, line FROM story WHERE guild_id=? ORDER BY id ASC",
                (interaction.guild_id,)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message("No story yet. Use `/story` to start one.", ephemeral=True); return
        chunks = []
        current = ""
        for aid, l in rows:
            author = interaction.guild.get_member(aid)
            name   = author.display_name if author else "Bot"
            part   = f"*{l}*  — {name}\n"
            if len(current) + len(part) > 3900:
                chunks.append(current)
                current = part
            else:
                current += part
        if current:
            chunks.append(current)

        for i, chunk in enumerate(chunks):
            title = "🏕️ The Campfire Story" if i == 0 else "🏕️ (continued)"
            embed = discord.Embed(title=title, description=chunk, color=discord.Color.orange())
            if i == len(chunks) - 1:
                embed.set_footer(text=f"{len(rows)} lines written · Keep going with /story")
            await interaction.response.send_message(embed=embed) if i == 0 else await interaction.followup.send(embed=embed)


# ─────────────────────────────────────────────────────────
# [VOUCH]  — new member approval system
# ─────────────────────────────────────────────────────────

class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_core(self, member: discord.Member) -> bool:
        return any(r.name in ("🔥 Core", "👑 OG") for r in member.roles)

    @app_commands.command(name="vouch", description="Vouch for a new member — Core/OG only")
    @app_commands.describe(member="Who are you vouching for?", note="Why should they be here?")
    async def vouch(self, interaction: discord.Interaction, member: discord.Member, note: str = None):
        if not self._is_core(interaction.user):
            await interaction.response.send_message("Only Core/OG can vouch.", ephemeral=True); return
        async with get_db() as db:
            async with db.execute(
                "SELECT id FROM vouches WHERE guild_id=? AND target_id=? AND voucher_id=?",
                (interaction.guild_id, member.id, interaction.user.id)) as cur:
                if await cur.fetchone():
                    await interaction.response.send_message(
                        f"Already vouched for {member.display_name}.", ephemeral=True); return
            await db.execute(
                "INSERT INTO vouches (guild_id, target_id, voucher_id, note) VALUES (?,?,?,?)",
                (interaction.guild_id, member.id, interaction.user.id, note or "No note"))
            await db.commit()
            async with db.execute(
                "SELECT COUNT(*) FROM vouches WHERE guild_id=? AND target_id=?",
                (interaction.guild_id, member.id)) as cur:
                vouch_count = (await cur.fetchone())[0]

        embed = discord.Embed(
            title=f"✅ Vouch — {member.display_name}",
            description=f"{interaction.user.mention} vouched for {member.mention}",
            color=discord.Color.green())
        if note:
            embed.add_field(name="Note", value=note)
        embed.add_field(name="Total Vouches", value=str(vouch_count))
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vouches", description="See vouches for a member")
    async def vouches_list(self, interaction: discord.Interaction, member: discord.Member):
        async with get_db() as db:
            async with db.execute(
                "SELECT voucher_id, note, created_at FROM vouches WHERE guild_id=? AND target_id=?",
                (interaction.guild_id, member.id)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message(f"No vouches for {member.display_name}.", ephemeral=True); return
        embed = discord.Embed(title=f"✅ Vouches for {member.display_name}", color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        for vid, note, created_at in rows:
            voucher = interaction.guild.get_member(vid)
            embed.add_field(name=voucher.display_name if voucher else "Unknown",
                            value=note or "No note", inline=False)
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [WEATHER]  — daily vibe forecast
# ─────────────────────────────────────────────────────────

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_forecast.start()

    def cog_unload(self):
        self.daily_forecast.cancel()

    @tasks.loop(hours=24)
    async def daily_forecast(self):
        for guild in self.bot.guilds:
            ch = discord.utils.get(guild.text_channels, name="status")
            if not ch:
                ch = discord.utils.get(guild.text_channels, name="general")
            if ch:
                title, desc = random.choice(WEATHER_FORECASTS)
                embed = discord.Embed(
                    title=f"🌤️ Daily Forecast — {datetime.utcnow().strftime('%A %b %d')}",
                    description=f"**{title}**\n{desc}",
                    color=discord.Color.from_str("#FF4500"))
                embed.set_footer(text="Bonfire Bot · weather service")
                await ch.send(embed=embed)

    @daily_forecast.before_loop
    async def before_forecast(self):
        await self.bot.wait_until_ready()
        # Wait until next 9am UTC
        now    = datetime.utcnow()
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

    @app_commands.command(name="forecast", description="Get today's server vibe forecast")
    async def forecast(self, interaction: discord.Interaction):
        title, desc = random.choice(WEATHER_FORECASTS)
        embed = discord.Embed(
            title=f"🌤️ Today's Forecast",
            description=f"**{title}**\n{desc}",
            color=discord.Color.from_str("#FF4500"))
        embed.set_footer(text="Bonfire Bot · forecast may vary")
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [CHALLENGE]  — weekly challenge system
# ─────────────────────────────────────────────────────────

class Challenge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_post.start()

    def cog_unload(self):
        self.weekly_post.cancel()

    @tasks.loop(hours=168)  # weekly
    async def weekly_post(self):
        for guild in self.bot.guilds:
            ch = discord.utils.get(guild.text_channels, name="general")
            if not ch:
                continue
            challenge = random.choice(WEEKLY_CHALLENGES)
            async with get_db() as db:
                await db.execute(
                    "INSERT OR REPLACE INTO weekly_challenge (guild_id, challenge, posted_at, completions)"
                    " VALUES (?,?,?,?)",
                    (guild.id, challenge, datetime.utcnow().isoformat(), "[]"))
                await db.commit()
            embed = discord.Embed(
                title="🎯 Weekly Challenge",
                description=f"**{challenge}**",
                color=discord.Color.from_str("#4ECDC4"),
                timestamp=datetime.utcnow())
            embed.add_field(name="Duration", value="7 days")
            embed.add_field(name="Complete it?", value="React ✅ to mark it done")
            embed.set_footer(text="New challenge every Monday · Bonfire Bot")
            msg = await ch.send(embed=embed)
            await msg.add_reaction("✅")

    @weekly_post.before_loop
    async def before_weekly(self):
        await self.bot.wait_until_ready()
        # Wait until next Monday 10am UTC
        now  = datetime.utcnow()
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0 and now.hour >= 10:
            days_until_monday = 7
        target = (now + timedelta(days=days_until_monday)).replace(hour=10, minute=0, second=0, microsecond=0)
        await asyncio.sleep((target - now).total_seconds())

    @app_commands.command(name="challenge", description="See the current weekly challenge")
    async def challenge(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT challenge, posted_at, completions FROM weekly_challenge WHERE guild_id=?",
                (interaction.guild_id,)) as cur:
                row = await cur.fetchone()
        if not row:
            challenge = random.choice(WEEKLY_CHALLENGES)
            async with get_db() as db:
                await db.execute(
                    "INSERT OR REPLACE INTO weekly_challenge (guild_id, challenge, posted_at, completions)"
                    " VALUES (?,?,?,?)",
                    (interaction.guild_id, challenge, datetime.utcnow().isoformat(), "[]"))
                await db.commit()
            completions_list = []
        else:
            challenge, _, completions_str = row
            completions_list = json.loads(completions_str)

        embed = discord.Embed(title="🎯 This Week's Challenge", description=f"**{challenge}**",
                              color=discord.Color.from_str("#4ECDC4"))
        done  = [interaction.guild.get_member(uid) for uid in completions_list]
        done  = [m for m in done if m]
        if done:
            embed.add_field(name="Completed by", value=", ".join(m.display_name for m in done), inline=False)
        embed.set_footer(text="React ✅ on the challenge post to mark complete")
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [MODERATION]
# ─────────────────────────────────────────────────────────

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot     = bot
        self.history = defaultdict(deque)
        self.warned  = set()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        key = (message.guild.id, message.author.id)
        now = datetime.utcnow().timestamp()
        q   = self.history[key]
        q.append(now)
        while q and now - q[0] > SPAM_TIME_WINDOW_SECONDS:
            q.popleft()
        if len(q) >= SPAM_MESSAGE_THRESHOLD:
            if key not in self.warned:
                self.warned.add(key)
                try:
                    await message.channel.send(
                        f"{message.author.mention} ease up — that looks like spam. 🐢", delete_after=5)
                except Exception:
                    pass
        else:
            self.warned.discard(key)


# ─────────────────────────────────────────────────────────
# [EVENTS]
# ─────────────────────────────────────────────────────────

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        async with get_db() as db:
            await db.execute(
                "INSERT INTO activity_log (guild_id,user_id,activity_type) VALUES (?,?,'message')",
                (message.guild.id, message.author.id))
            await db.commit()

        streak_cog = self.bot.get_cog("Streak")
        if streak_cog:
            await streak_cog.record_activity(message.guild.id)

        roles_cog = self.bot.get_cog("AutoRoles")
        if roles_cog:
            await roles_cog.increment_messages(message.guild.id, message.author.id)


# ─────────────────────────────────────────────────────────
# [REACTIONS]
# ─────────────────────────────────────────────────────────

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id or not payload.guild_id:
            return
        emoji = str(payload.emoji)
        if   emoji == "⭐": await self._star(payload)
        elif emoji == "📖": await self._lore(payload)
        elif emoji == "💬": await self._quote(payload)
        elif emoji == "✅": await self._lfg_join(payload)

    async def _fetch_msg(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        ch    = guild.get_channel(payload.channel_id)
        try:
            return await ch.fetch_message(payload.message_id), ch
        except Exception:
            return None, None

    async def _star(self, payload):
        msg, _ = await self._fetch_msg(payload)
        if not msg:
            return
        for r in msg.reactions:
            if str(r.emoji) == "⭐" and r.count >= HIGHLIGHT_STAR_THRESHOLD:
                h = self.bot.get_cog("Highlights")
                if h:
                    await h.post_highlight(msg)
                break

    async def _lore(self, payload):
        msg, ch = await self._fetch_msg(payload)
        if not msg or not msg.content:
            return
        async with get_db() as db:
            async with db.execute(
                "SELECT id FROM lore WHERE guild_id=? AND content=? AND author_id=?",
                (payload.guild_id, msg.content, msg.author.id)) as cur:
                if not await cur.fetchone():
                    await db.execute("INSERT INTO lore (guild_id,author_id,content) VALUES (?,?,?)",
                                     (payload.guild_id, msg.author.id, msg.content))
                    await db.commit()
                    snip = msg.content[:80] + ("..." if len(msg.content) > 80 else "")
                    try:
                        await ch.send(f"📖 Lore captured: *\"{snip}\"*", delete_after=5)
                    except Exception:
                        pass

    async def _quote(self, payload):
        msg, ch = await self._fetch_msg(payload)
        if not msg or not msg.content:
            return
        async with get_db() as db:
            await db.execute(
                "INSERT OR IGNORE INTO quotes (guild_id,message_id,author_id,content,jump_url)"
                " VALUES (?,?,?,?,?)",
                (payload.guild_id, payload.message_id, msg.author.id, msg.content, msg.jump_url))
            await db.commit()
        try:
            await ch.send(f"💬 Quote saved from **{msg.author.display_name}**.", delete_after=4)
        except Exception:
            pass

    async def _lfg_join(self, payload):
        async with get_db() as db:
            async with db.execute(
                "SELECT id,members,size,game,channel_id FROM lfg_lobbies WHERE message_id=?",
                (payload.message_id,)) as cur:
                row = await cur.fetchone()
        if not row:
            return
        lobby_id, members_str, size, game, channel_id = row
        members = json.loads(members_str)
        if payload.user_id in members:
            return
        members.append(payload.user_id)
        guild = self.bot.get_guild(payload.guild_id)
        ch    = guild.get_channel(channel_id)

        if len(members) >= size:
            mentions = " ".join(f"<@{u}>" for u in members)
            embed = discord.Embed(title=f"🎮 Lobby Full — {game}",
                                  description=f"All {size} in. LET'S GO\n{mentions}",
                                  color=discord.Color.green())
            try:
                await ch.send(embed=embed)
            except Exception:
                pass
            async with get_db() as db:
                await db.execute("DELETE FROM lfg_lobbies WHERE id=?", (lobby_id,))
                await db.commit()
        else:
            async with get_db() as db:
                await db.execute("UPDATE lfg_lobbies SET members=? WHERE id=?",
                                 (json.dumps(members), lobby_id))
                await db.commit()
            try:
                msg_ch = guild.get_channel(payload.channel_id)
                msg    = await msg_ch.fetch_message(payload.message_id)
                new_embed = discord.Embed(title=f"🎮 LFG — {game}", color=discord.Color.from_str("#9B59B6"))
                new_embed.add_field(name="Spots",   value=f"{len(members)}/{size}", inline=True)
                new_embed.add_field(name="Players", value=" ".join(f"<@{u}>" for u in members), inline=False)
                new_embed.set_footer(text="React ✅ to join")
                await msg.edit(embed=new_embed)
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                    before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return

        # Clutch Mode
        if after.channel:
            real = [m for m in after.channel.members if not m.bot]
            if len(real) == 1:
                clutch = self.bot.get_cog("Clutch")
                if clutch:
                    await clutch.check_clutch(member.guild, after.channel, real[0])

        # Streak + Night Owl tracking
        if after.channel and not before.channel:
            streak = self.bot.get_cog("Streak")
            if streak:
                await streak.record_activity(member.guild.id)
            roles_cog = self.bot.get_cog("AutoRoles")
            if roles_cog:
                await roles_cog.log_late_vc(member.guild.id, member.id)

        # Gamer role — tracked by game VC time (simplified: joining game VC counts)
        if after.channel and "game" in (after.channel.name or "").lower():
            guild  = member.guild
            gamer_role = discord.utils.get(guild.roles, name="🎮 Gamer")
            if gamer_role and gamer_role not in member.roles:
                async with get_db() as db:
                    await db.execute(
                        "UPDATE role_tracking SET game_vc_minutes = game_vc_minutes + 1"
                        " WHERE guild_id=? AND user_id=?",
                        (guild.id, member.id))
                    await db.commit()
                    async with db.execute(
                        "SELECT game_vc_minutes FROM role_tracking WHERE guild_id=? AND user_id=?",
                        (guild.id, member.id)) as cur:
                        row = await cur.fetchone()
                if row and row[0] >= (GAMER_VC_HOURS_THRESHOLD * 60):
                    try:
                        await member.add_roles(gamer_role, reason="Earned Gamer role")
                        ch = discord.utils.get(guild.text_channels, name="general")
                        if ch:
                            await ch.send(embed=discord.Embed(
                                description=f"🎮 {member.mention} earned **🎮 Gamer**. It's official.",
                                color=discord.Color.from_str("#9B59B6")))
                    except Exception:
                        pass


# ─────────────────────────────────────────────────────────
# [BOT]
# ─────────────────────────────────────────────────────────

ALL_COGS = [
    Setup, Onboarding, Utility, Voice, Fun, LFG,
    Reminders, Highlights, Lore, Quotes, Beef,
    VibeCheck, Streak, Wrapped, Clutch, AutoRoles,
    Story, Vouch, Weather, Challenge,
    Moderation, Events, Reactions,
]


class BonfireBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members          = True
        intents.presences        = True
        intents.reactions        = True
        intents.voice_states     = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        await init_db()
        # Re-register persistent intro view so buttons survive restarts
        self.add_view(IntroView(self, None))
        for cog_cls in ALL_COGS:
            await self.add_cog(cog_cls(self))
            print(f"  ✓ {cog_cls.__name__}")
        await self.tree.sync()
        print("Slash commands synced.")

    async def on_ready(self):
        print(f"\n{'='*50}")
        print(f"  🔥 Bonfire Bot — online")
        print(f"  {self.user}  ({self.user.id})")
        print(f"  Guilds: {len(self.guilds)}")
        print(f"{'='*50}\n")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="the bonfire 🔥"))

    async def on_app_command_error(self, interaction: discord.Interaction, error):
        msg = "Something went wrong. Try again."
        if isinstance(error, app_commands.MissingPermissions):
            msg = "You don't have permission to use this."
        elif isinstance(error, app_commands.CommandOnCooldown):
            msg = f"Slow down — try again in {error.retry_after:.0f}s."
        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception:
            pass


async def main():
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN not set in .env")
        sys.exit(1)
    bot = BonfireBot()
    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
