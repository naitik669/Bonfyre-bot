"""
╔══════════════════════════════════════════════════════════════╗
║                  🔥 BONFIRE BOT · main.py                    ║
║         Built for real friend groups. Not corporations.      ║
╠══════════════════════════════════════════════════════════════╣
║  v2.0 — The Real One Update                                  ║
║  25 features · proper emoji channels · full UI/UX rules      ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio
import hashlib
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
CHECKIN_QUIET_DAYS        = 7
DEAD_CHAT_HOURS           = 4
DEAD_CHAT_COOLDOWN_HOURS  = 6

REGULAR_MESSAGE_THRESHOLD   = 50
NIGHT_OWL_LATE_VC_THRESHOLD = 5
GAMER_VC_HOURS_THRESHOLD    = 10

PRIMARY   = discord.Color.from_str("#FF4500")
TEAL      = discord.Color.from_str("#4ECDC4")
PURPLE    = discord.Color.from_str("#9B59B6")
GOLD      = discord.Color.from_str("#F1C40F")
DARK_GREY = discord.Color.from_str("#2C2F33")
ORANGE    = discord.Color.from_str("#E67E22")

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
    "🎬 Recommend a movie nobody's heard of in #🎬・movie-picks",
    "🎵 Drop your current #1 most played song in #🎵・music-now",
    "📸 Post a throwback photo in #🔥・general (no cringe immunity)",
    "💬 Start a conversation that lasts 50+ messages",
    "🔥 Get a message highlighted in #⭐・highlights this week",
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

ICEBREAKER_QUESTIONS = [
    ("getting to know you", "If you could only eat one meal for the rest of your life, what is it?"),
    ("getting to know you", "What's a skill you have that would surprise everyone here?"),
    ("getting to know you", "What's the most niche thing you're an expert on?"),
    ("would you rather", "Would you rather have no internet for a month or no music for a year?"),
    ("would you rather", "Would you rather be able to fly but only at walking speed, or teleport but only to places you've already been?"),
    ("would you rather", "Would you rather always have to whisper or always have to shout?"),
    ("hot take", "Unpopular opinion time: what's a game/movie/show everyone loves that you think is mid?"),
    ("hot take", "What's a hill you will die on that most people disagree with?"),
    ("hot take", "What's an opinion you have that could get you cancelled in this server?"),
    ("confess something", "Confess: what's a guilty pleasure you've never told anyone here?"),
    ("confess something", "Confess: what's something embarrassing that happened to you online that you never talked about?"),
    ("confess something", "Confess: who in this server have you been most wrong about?"),
]

DEAD_CHAT_PROMPTS = [
    "🔥 The fire's dying… someone say something",
    "💀 General has been silent for too long. What's everyone actually doing rn?",
    "🏕️ Ayo bonfire's getting cold. Someone throw a log on it.",
    "👀 Nobody's said anything in a while. Suspicious.",
    "🔕 Dead hours detected. Initiating emergency vibe protocol.",
]

BONFIRE_SPARKS = [
    "Settle this: tabs or spaces?",
    "Settle this: pineapple on pizza — yes or no?",
    "Early bird or night owl? Be honest.",
    "Spicy food or mild food?",
    "Hot shower or cold shower?",
    "Team iOS or Team Android?",
    "PC or console?",
    "Movies or series?",
    "Coffee or tea?",
    "Would you rather be famous or rich?",
]

SEASON_NAMES = [
    "Season of the Night Owls",
    "The Beef Era",
    "Summer of Chaos",
    "The Lore Age",
    "Season of the Unhinged",
    "The Great Vibe Drought",
    "Season of the Grinders",
    "The Clutch Chronicles",
    "Era of the Yappers",
    "The Bonfire Renaissance",
]

STAT_TITLES = {
    "messages": "The Yapper",
    "lore": "The Lore Machine",
    "highlights": "The Star Collector",
    "quotes": "The Quotable One",
    "beef": "The Instigator",
    "vc": "The VC Enjoyer",
    "vibes": "The Vibe Check",
    "default": "Silent But Deadly",
}

def progress_bar(value, max_val, length=10):
    if max_val == 0:
        return "░" * length
    filled = round((value / max_val) * length)
    return "█" * filled + "░" * (length - filled)

def bonfire_footer(feature: str) -> str:
    return f"🔥 Bonfire · {feature} · {datetime.utcnow().strftime('%b %d %H:%M')} UTC"


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
                rsvp_maybe  TEXT DEFAULT '[]',
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
            CREATE TABLE IF NOT EXISTS late_night_checkins (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                user_id    INTEGER,
                mood       TEXT,
                note       TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS meetups (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                creator_id  INTEGER,
                title       TEXT,
                description TEXT,
                location    TEXT,
                meetup_time TIMESTAMP,
                rsvp_yes    TEXT DEFAULT '[]',
                rsvp_no     TEXT DEFAULT '[]',
                rsvp_maybe  TEXT DEFAULT '[]',
                message_id  INTEGER,
                completed   INTEGER DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS meetup_memories (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                meetup_id  INTEGER,
                user_id    INTEGER,
                memory     TEXT,
                rating     INTEGER,
                photo_url  TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS icebreakers (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                question   TEXT,
                category   TEXT,
                used       INTEGER DEFAULT 0,
                posted_at  TIMESTAMP,
                message_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS icebreaker_answers (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id      INTEGER,
                user_id       INTEGER,
                icebreaker_id INTEGER,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS vibe_pulse_optout (
                guild_id INTEGER,
                user_id  INTEGER,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS achievements (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                user_id     INTEGER,
                badge_key   TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, user_id, badge_key)
            );
            CREATE TABLE IF NOT EXISTS polls (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                creator_id INTEGER,
                question   TEXT,
                options    TEXT,
                votes      TEXT DEFAULT '{}',
                anonymous  INTEGER DEFAULT 0,
                deadline   TIMESTAMP,
                closed     INTEGER DEFAULT 0,
                message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS pairchat_members (
                guild_id INTEGER,
                user_id  INTEGER,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS pairchat_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                user1_id   INTEGER,
                user2_id   INTEGER,
                paired_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS memories (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                user_id    INTEGER,
                text       TEXT,
                image_url  TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS checkin_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                target_id  INTEGER,
                sender_id  INTEGER,
                anonymous  INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS vc_sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                channel_id INTEGER,
                members    TEXT,
                started_at TIMESTAMP,
                ended_at   TIMESTAMP,
                duration_minutes INTEGER,
                vibe_emoji TEXT,
                message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS vc_active (
                guild_id   INTEGER,
                channel_id INTEGER,
                members    TEXT DEFAULT '[]',
                started_at TIMESTAMP,
                PRIMARY KEY (guild_id, channel_id)
            );
            CREATE TABLE IF NOT EXISTS drama (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                logger_id  INTEGER,
                user1_id   INTEGER,
                user2_id   INTEGER,
                description TEXT,
                beef_id    INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS bets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                creator_id  INTEGER,
                question    TEXT,
                option1     TEXT,
                option2     TEXT,
                votes1      TEXT DEFAULT '[]',
                votes2      TEXT DEFAULT '[]',
                deadline    TIMESTAMP,
                winner      INTEGER,
                closed      INTEGER DEFAULT 0,
                void        INTEGER DEFAULT 0,
                message_id  INTEGER,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS server_temp (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                score      INTEGER,
                label      TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS confessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                user_hash  TEXT,
                content    TEXT,
                message_id INTEGER,
                revealed   INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS availability (
                guild_id   INTEGER,
                user_id    INTEGER,
                schedule   TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS hotseat (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                target_id   INTEGER,
                starter_id  INTEGER,
                questions   TEXT DEFAULT '[]',
                active      INTEGER DEFAULT 1,
                started_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at    TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS friendship_milestones (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                user1_id   INTEGER,
                user2_id   INTEGER,
                milestone  TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS timeline_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    INTEGER,
                category    TEXT,
                description TEXT,
                members     TEXT DEFAULT '[]',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS notify_prefs (
                guild_id  INTEGER,
                user_id   INTEGER,
                prefs     TEXT DEFAULT '{}',
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS alter_egos (
                guild_id    INTEGER,
                user_id     INTEGER,
                name        TEXT,
                description TEXT,
                vibe        TEXT,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS dead_chat_log (
                guild_id   INTEGER PRIMARY KEY,
                last_post  TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS seasons (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                name       TEXT,
                started_at TIMESTAMP,
                ended_at   TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS weekly_vote (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   INTEGER,
                gaming     INTEGER DEFAULT 0,
                movie      INTEGER DEFAULT 0,
                meetup     INTEGER DEFAULT 0,
                nothing    INTEGER DEFAULT 0,
                voters     TEXT DEFAULT '[]',
                posted_at  TIMESTAMP
            );
        """)
        await db.commit()

        # Seed icebreaker questions
        async with db.execute("SELECT COUNT(*) FROM icebreakers") as cur:
            count = (await cur.fetchone())[0]
        if count == 0:
            for category, question in ICEBREAKER_QUESTIONS:
                await db.execute(
                    "INSERT INTO icebreakers (guild_id, question, category) VALUES (0, ?, ?)",
                    (question, category))
            await db.commit()


def get_db():
    return aiosqlite.connect(DB_PATH)


# ─────────────────────────────────────────────────────────
# [HELPERS]
# ─────────────────────────────────────────────────────────

async def log_timeline(guild_id: int, category: str, description: str, members: list = None):
    async with get_db() as db:
        await db.execute(
            "INSERT INTO timeline_events (guild_id, category, description, members) VALUES (?,?,?,?)",
            (guild_id, category, description, json.dumps(members or [])))
        await db.commit()


async def check_achievement(bot, guild_id: int, user_id: int, badge_key: str):
    """Unlock an achievement and announce it."""
    BADGES = {
        "fire_starter":   ("🔥", "Fire Starter",   "First to /start a session"),
        "yapper":         ("💬", "Yapper",          "500 messages sent"),
        "beefcake":       ("🥩", "Certified Beefcake", "Started 5 beefs"),
        "3am_club":       ("🌙", "3AM Club",        "In VC after 3am five times"),
        "lore_master":    ("📖", "Lore Master",     "Added 10 lore entries"),
        "never_miss":     ("🎯", "Never Miss",      "Completed 3 weekly challenges"),
        "peacemaker":     ("🤝", "Peacemaker",      "Resolved 3 beefs"),
        "welcome_wagon":  ("🆕", "Welcome Wagon",   "Vouched for 3 new members"),
        "night_owl_badge":("🦉", "Night Owl",       "Checked in 5 nights in a row"),
        "prophet":        ("🔮", "Prophet",         "Won 5 bets"),
        "storyteller":    ("🏕️", "Storyteller",     "Added 20 story lines"),
        "icebreaker_king":("🧊", "Icebreaker King", "Answered 10 icebreakers"),
    }
    if badge_key not in BADGES:
        return
    async with get_db() as db:
        try:
            await db.execute(
                "INSERT INTO achievements (guild_id, user_id, badge_key) VALUES (?,?,?)",
                (guild_id, user_id, badge_key))
            await db.commit()
        except Exception:
            return  # already unlocked

    emoji, name, desc = BADGES[badge_key]
    guild  = bot.get_guild(guild_id)
    member = guild.get_member(user_id) if guild else None
    if not guild or not member:
        return
    ch = discord.utils.get(guild.text_channels, name="🔥・general") or \
         discord.utils.get(guild.text_channels, name="general")
    if ch:
        embed = discord.Embed(
            title=f"{emoji} Achievement Unlocked!",
            description=f"**{member.mention}** just earned **{name}**\n*{desc}*",
            color=PURPLE)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=bonfire_footer("Achievements"))
        await ch.send(embed=embed)


def _is_core(member: discord.Member) -> bool:
    return any(r.name in ("🔥 Core", "👑 OG") for r in member.roles)


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

        role_defs = [
            ("👑 OG",        discord.Color.from_str("#FF6B35"), True),
            ("🔥 Core",      discord.Color.from_str("#FF4500"), True),
            ("💬 Regular",   discord.Color.from_str("#4ECDC4"), False),
            ("🎮 Gamer",     discord.Color.from_str("#9B59B6"), False),
            ("🌙 Night Owl", discord.Color.from_str("#2C3E50"), False),
            ("👤 Lurker",    discord.Color.from_str("#95A5A6"), False),
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
            guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            core_role:          discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        readonly_ow = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            core_role:          discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        core_only_ow = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            core_role:          discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        voice_ow = {
            guild.default_role: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
            core_role:          discord.PermissionOverwrite(connect=True, speak=True, view_channel=True, move_members=True),
        }

        existing_cats = [c.name for c in guild.categories]

        # 🔥 The Bonfire
        if "🔥 The Bonfire" not in existing_cats:
            cat = await guild.create_category("🔥 The Bonfire")
            for ch_name in ["🔥・general", "💬・random", "🫀・feels-board", "🪪・homiez-cards", "🎤・hot-seat"]:
                await guild.create_text_channel(ch_name, category=cat, overwrites=default_ow)
            await guild.create_text_channel("📢・announcements", category=cat, overwrites=readonly_ow)

        # 🎮 Game Camp
        if "🎮 Game Camp" not in existing_cats:
            cat = await guild.create_category("🎮 Game Camp")
            for ch_name in ["🎮・lfg", "🎬・clips", "⚙️・loadouts", "🌶️・hot-takes"]:
                await guild.create_text_channel(ch_name, category=cat, overwrites=default_ow)
            await guild.create_voice_channel("🎮 Game VC",   category=cat, overwrites=voice_ow)
            await guild.create_voice_channel("🎮 Game VC 2", category=cat, overwrites=voice_ow)

        # 🎬 Chill Zone
        if "🎬 Chill Zone" not in existing_cats:
            cat = await guild.create_category("🎬 Chill Zone")
            for ch_name in ["🎬・movie-picks", "🎵・music-now", "😂・memes", "📸・memories"]:
                await guild.create_text_channel(ch_name, category=cat, overwrites=default_ow)
            await guild.create_voice_channel("😌 Chill VC",    category=cat, overwrites=voice_ow)
            await guild.create_voice_channel("🎬 Watch Party", category=cat, overwrites=voice_ow)

        # 📖 The Lore Cave
        if "📖 The Lore Cave" not in existing_cats:
            cat = await guild.create_category("📖 The Lore Cave")
            for ch_name in ["⭐・highlights", "💬・quotes-wall", "🥩・beef-log",
                            "📖・lore-archive", "🏕️・campfire-story", "💌・confessions",
                            "🗺️・meetups", "🏆・achievements"]:
                await guild.create_text_channel(ch_name, category=cat, overwrites=default_ow)

        # 🌙 Inner Circle
        if "🌙 Inner Circle" not in existing_cats:
            cat = await guild.create_category("🌙 Inner Circle")
            await guild.create_text_channel("🔥・core-chat", category=cat, overwrites=core_only_ow)
            await guild.create_text_channel("📋・plans",     category=cat, overwrites=core_only_ow)
            await guild.create_voice_channel("👑 Core VC",  category=cat, overwrites={
                guild.default_role: discord.PermissionOverwrite(connect=False),
                core_role:          discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
            })

        # 📡 System
        if "📡 System" not in existing_cats:
            cat = await guild.create_category("📡 System")
            await guild.create_text_channel("📊・status",       category=cat, overwrites=readonly_ow)
            await guild.create_text_channel("🏆・wrapped-hall", category=cat, overwrites=readonly_ow)
            await guild.create_text_channel("🤖・bot-logs",     category=cat, overwrites=core_only_ow)

        try:
            await interaction.user.add_roles(og_role, reason="Server founder")
            await interaction.user.add_roles(core_role, reason="Server founder")
        except Exception:
            pass

        embed = discord.Embed(
            title="🔥 Bonfire Server Ready",
            description="Your server is set up and the fire is lit. All channels have their proper emojis.",
            color=PRIMARY)
        embed.add_field(name="📁 Categories", value="🔥 The Bonfire · 🎮 Game Camp · 🎬 Chill Zone\n📖 The Lore Cave · 🌙 Inner Circle · 📡 System", inline=False)
        embed.add_field(name="👥 Roles", value="👑 OG · 🔥 Core · 💬 Regular · 🎮 Gamer · 🌙 Night Owl · 👤 Lurker", inline=False)
        embed.add_field(name="✅ Your Role", value="👑 OG + 🔥 Core assigned to you", inline=False)
        embed.add_field(name="🚀 Next Steps", value="1. Assign 🔥 Core to your inner circle\n2. Invite your squad\n3. Run `/challenge` for first weekly challenge", inline=False)
        embed.set_footer(text=bonfire_footer("Setup"))
        await interaction.followup.send(embed=embed, ephemeral=True)

        await log_timeline(guild.id, "📅", f"Server founded by {interaction.user.display_name}", [interaction.user.id])


# ─────────────────────────────────────────────────────────
# [ONBOARDING]
# ─────────────────────────────────────────────────────────

class IntroModal(discord.ui.Modal, title="🔥 Intro — Join the Squad"):
    name     = discord.ui.TextInput(label="Your name (or what we call you)", max_length=32, required=True)
    age      = discord.ui.TextInput(label="Age", max_length=4, required=False, placeholder="Optional")
    location = discord.ui.TextInput(label="Where you're from / based", max_length=64, required=False, placeholder="City, Country — optional")
    games    = discord.ui.TextInput(label="Games / interests you're into", max_length=120, required=False, placeholder="e.g. Valorant, CS2, FIFA, vibing...")
    bio      = discord.ui.TextInput(label="One line about you (make it real)", max_length=180, required=True,
                                    style=discord.TextStyle.paragraph, placeholder="Don't be boring. Who are you?")

    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot      = bot
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild  = interaction.guild
        member = interaction.user

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

        card_ch = (discord.utils.get(guild.text_channels, name="🪪・homiez-cards") or
                   discord.utils.get(guild.text_channels, name="homiez-cards"))
        if card_ch:
            embed = discord.Embed(
                title=f"🔥 {self.name.value}",
                description=f'*"{self.bio.value}"*',
                color=PRIMARY,
                timestamp=datetime.utcnow())
            embed.set_thumbnail(url=member.display_avatar.url)
            if self.age.value:
                embed.add_field(name="🎂 Age",   value=self.age.value,      inline=True)
            if self.location.value:
                embed.add_field(name="📍 Based", value=self.location.value, inline=True)
            if self.games.value:
                embed.add_field(name="🎮 Into",  value=self.games.value,    inline=False)
            embed.add_field(name="🗓️ Joined",
                            value=f"<t:{int(member.joined_at.timestamp())}:D>" if member.joined_at else "Today",
                            inline=True)
            embed.set_footer(text=bonfire_footer("Onboarding"))
            card_msg = await card_ch.send(embed=embed)
            async with get_db() as db:
                await db.execute("UPDATE member_intros SET card_msg_id=? WHERE user_id=?", (card_msg.id, member.id))
                await db.commit()

        await log_timeline(guild.id, "👤", f"{member.display_name} dropped their intro card", [member.id])
        await interaction.followup.send("✅ Your card is up in homiez-cards. Welcome to the bonfire.", ephemeral=True)


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

        lurker = discord.utils.get(guild.roles, name="👤 Lurker")
        if lurker:
            try:
                await member.add_roles(lurker, reason="Auto Lurker on join")
            except discord.Forbidden:
                pass

        try:
            embed = discord.Embed(
                title=f"🔥 Welcome to {guild.name}",
                description=(
                    f"Hey **{member.display_name}** — glad you pulled up.\n\n"
                    f"Head to **#🔥・general** and say what's good.\n"
                    f"Drop your intro with the button so the squad knows who you are.\n\n"
                    f"Commands to try: `/vibe` `/start` `/decide`\n"
                    f"React ⭐ to highlight messages, 💬 to save quotes, 📖 to log lore.\n\n"
                    f"The fire's lit. Come get warm."
                ),
                color=PRIMARY)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            embed.set_footer(text=bonfire_footer("Onboarding"))
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

        general = (discord.utils.get(guild.text_channels, name="🔥・general") or
                   discord.utils.get(guild.text_channels, name="general"))
        if general:
            join_embed = discord.Embed(
                description=f"**{member.mention}** just pulled up to the bonfire 🔥\nWho are you? Drop your intro below 👇",
                color=PRIMARY,
                timestamp=datetime.utcnow())
            join_embed.set_thumbnail(url=member.display_avatar.url)
            join_embed.set_footer(text=f"Member #{guild.member_count}")
            view = IntroView(self.bot, guild.id)
            await general.send(embed=join_embed, view=view)

        logs = (discord.utils.get(guild.text_channels, name="🤖・bot-logs") or
                discord.utils.get(guild.text_channels, name="bot-logs"))
        if logs:
            log_embed = discord.Embed(
                title="📥 New Member",
                description=f"{member.mention} joined",
                color=discord.Color.green(),
                timestamp=datetime.utcnow())
            log_embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>")
            log_embed.set_thumbnail(url=member.display_avatar.url)
            await logs.send(embed=log_embed)

        await log_timeline(guild.id, "👤", f"{member.display_name} joined the server", [member.id])

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild   = member.guild
        general = (discord.utils.get(guild.text_channels, name="🔥・general") or
                   discord.utils.get(guild.text_channels, name="general"))
        if general:
            embed = discord.Embed(
                description=f"**{member.display_name}** left the bonfire. 👋\nKeep the fire lit.",
                color=discord.Color.greyple())
            await general.send(embed=embed)
        await log_timeline(guild.id, "👋", f"{member.display_name} left the server", [member.id])

    @app_commands.command(name="intro", description="📝 Drop your intro card in homiez-cards")
    async def intro_cmd(self, interaction: discord.Interaction):
        modal = IntroModal(self.bot, interaction.guild_id)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="card", description="🪪 View someone's homiez card")
    @app_commands.describe(member="Who's card to view (leave blank for yours)")
    async def card_cmd(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        async with get_db() as db:
            async with db.execute(
                "SELECT name, age, location, games, bio FROM member_intros WHERE guild_id=? AND user_id=?",
                (interaction.guild_id, target.id)) as cur:
                row = await cur.fetchone()
        if not row:
            msg = "No card yet." if member else "You haven't dropped your intro yet. Use `/intro`."
            await interaction.response.send_message(msg, ephemeral=True); return

        name, age, location, games, bio = row
        embed = discord.Embed(title=f"🔥 {name}", description=f'*"{bio}"*', color=PRIMARY)
        embed.set_thumbnail(url=target.display_avatar.url)
        if age and age != "—":
            embed.add_field(name="🎂 Age",   value=age,      inline=True)
        if location and location != "—":
            embed.add_field(name="📍 Based", value=location, inline=True)
        if games and games != "—":
            embed.add_field(name="🎮 Into",  value=games,    inline=False)
        embed.set_footer(text=bonfire_footer("Homiez Cards"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [UTILITY]
# ─────────────────────────────────────────────────────────

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.decide_cooldowns = {}

    @app_commands.command(name="decide", description="🎲 Pick randomly from 2–10 options")
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

        embed = discord.Embed(title="🎲 The Bonfire Has Spoken", color=PRIMARY)
        embed.add_field(name="🗳️ Options",  value=" · ".join(options), inline=False)
        embed.add_field(name="✅ Decision", value=f"**{result}**",      inline=False)
        embed.set_footer(text=bonfire_footer("Decide"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vibe", description="🔥 Get a random bonfire vibe check")
    async def vibe(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description=f"**{random.choice(VIBE_MESSAGES)}**",
            color=PRIMARY)
        embed.set_footer(text=bonfire_footer("Vibe"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="say", description="📢 Make the bot say something")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(message="What to say")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message("✅", ephemeral=True)
        await interaction.channel.send(message)

    @app_commands.command(name="np", description="🎵 Share what you're currently listening to")
    @app_commands.describe(song="Song / artist / album", mood="Optional mood tag")
    async def np(self, interaction: discord.Interaction, song: str, mood: str = None):
        music_ch = (discord.utils.get(interaction.guild.text_channels, name="🎵・music-now") or
                    discord.utils.get(interaction.guild.text_channels, name="music-now"))
        embed = discord.Embed(title="🎵 Now Playing", description=f"**{song}**", color=PURPLE)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        if mood:
            embed.add_field(name="🎭 Mood", value=mood)
        embed.set_footer(text=bonfire_footer("Now Playing"))
        if music_ch and music_ch.id != interaction.channel_id:
            await music_ch.send(embed=embed)
            await interaction.response.send_message(f"✅ Posted to {music_ch.mention}", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="members", description="👥 Show all homiez cards — who's in the squad")
    async def members_cmd(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT user_id, name, bio FROM member_intros WHERE guild_id=? ORDER BY created_at ASC",
                (interaction.guild_id,)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message("No intros yet. Use `/intro` to start.", ephemeral=True); return

        embed = discord.Embed(title="🔥 The Squad", color=PRIMARY)
        for uid, name, bio in rows:
            m    = interaction.guild.get_member(uid)
            handle = f"@{m.name}" if m else "left the server"
            snip   = (bio[:60] + "…") if len(bio) > 60 else bio
            embed.add_field(name=f"{name} ({handle})", value=f'*"{snip}"*', inline=False)
        embed.set_footer(text=bonfire_footer("Members"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [VOICE]
# ─────────────────────────────────────────────────────────

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lockvc", description="🔒 Lock all VCs — Core/OG only")
    async def lockvc(self, interaction: discord.Interaction):
        if not _is_core(interaction.user):
            await interaction.response.send_message("🔒 Core/OG only.", ephemeral=True); return
        locked = []
        for ch in interaction.guild.voice_channels:
            await ch.set_permissions(interaction.guild.default_role, connect=False)
            locked.append(ch.name)
        embed = discord.Embed(title="🔒 VCs Locked", description=", ".join(locked), color=discord.Color.red())
        embed.set_footer(text=bonfire_footer("Voice"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unlockvc", description="🔓 Unlock all VCs — Core/OG only")
    async def unlockvc(self, interaction: discord.Interaction):
        if not _is_core(interaction.user):
            await interaction.response.send_message("🔓 Core/OG only.", ephemeral=True); return
        unlocked = []
        for ch in interaction.guild.voice_channels:
            await ch.set_permissions(interaction.guild.default_role, connect=True)
            unlocked.append(ch.name)
        embed = discord.Embed(title="🔓 VCs Unlocked", description=", ".join(unlocked), color=discord.Color.green())
        embed.set_footer(text=bonfire_footer("Voice"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="limitvc", description="🎚️ Set member limit on a VC")
    @app_commands.describe(limit="0–99 (0 = no limit)", channel="Target VC")
    async def limitvc(self, interaction: discord.Interaction, limit: int, channel: discord.VoiceChannel = None):
        if not _is_core(interaction.user):
            await interaction.response.send_message("Core/OG only.", ephemeral=True); return
        target = channel or (interaction.user.voice.channel if interaction.user.voice else None)
        if not target:
            await interaction.response.send_message("Join a VC or specify one.", ephemeral=True); return
        if not 0 <= limit <= 99:
            await interaction.response.send_message("Limit must be 0–99.", ephemeral=True); return
        await target.edit(user_limit=limit)
        desc = "No limit" if limit == 0 else f"{limit} members max"
        embed = discord.Embed(title="🎚️ VC Limit Set", description=f"**{target.name}** → {desc}", color=discord.Color.blue())
        embed.set_footer(text=bonfire_footer("Voice"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [FUN]
# ─────────────────────────────────────────────────────────

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roast_cooldowns = {}

    @app_commands.command(name="start", description="🔥 Kick off a session")
    @app_commands.describe(activity="Type of hang", ping="Ping @here?", custom="Custom activity name")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Game Night 🎮",  value="game night"),
        app_commands.Choice(name="Movie Night 🎬", value="movie night"),
        app_commands.Choice(name="Chill 😌",       value="chill"),
        app_commands.Choice(name="Custom",         value="custom"),
    ])
    async def start(self, interaction: discord.Interaction, activity: str, ping: bool = False, custom: str = None):
        label = custom if (activity == "custom" and custom) else activity
        emoji = {"game night": "🎮", "movie night": "🎬", "chill": "😌"}.get(activity, "🔥")
        vc = next((v for v in interaction.guild.voice_channels
                   if any(x in v.name.lower() for x in ["main", "chill", "game"])), None)
        embed = discord.Embed(
            title=f"{emoji} {label.title()} — THE BONFIRE IS CALLING",
            description=f"**{interaction.user.display_name}** is starting something. Who's pulling up?",
            color=PRIMARY)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        if vc:
            embed.add_field(name="📍 VC", value=vc.mention, inline=True)
        embed.add_field(name="🎭 Activity", value=label.title(), inline=True)
        embed.set_footer(text=bonfire_footer("Start"))

        view = discord.ui.View(timeout=3600)
        count = {"yes": 0}

        async def join_cb(inter: discord.Interaction):
            count["yes"] += 1
            await inter.response.send_message(f"✅ You're in! ({count['yes']} total)", ephemeral=True)

        btn = discord.ui.Button(label="✅ I'm in", style=discord.ButtonStyle.success)
        btn.callback = join_cb
        view.add_item(btn)

        await interaction.response.send_message(content="@here" if ping else "", embed=embed, view=view)

        await check_achievement(self.bot, interaction.guild_id, interaction.user.id, "fire_starter")
        await log_timeline(interaction.guild_id, "🔥", f"{interaction.user.display_name} started {label}", [interaction.user.id])

    @app_commands.command(name="roast", description="🔥 Roast a homie — opt-in fun only")
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
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=bonfire_footer("Roast"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tod", description="🤔 Truth or Dare — server edition")
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
        embed.set_footer(text=bonfire_footer("ToD"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hottake", description="🌶️ Post a hot take — squad votes agree/disagree")
    @app_commands.describe(take="Drop the take. Make it spicy.")
    async def hottake(self, interaction: discord.Interaction, take: str):
        embed = discord.Embed(
            title="🌶️ HOT TAKE",
            description=f'**"{take}"**',
            color=PRIMARY)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=bonfire_footer("Hot Takes"))

        agree_count    = {"n": 0}
        disagree_count = {"n": 0}
        voters         = set()

        view = discord.ui.View(timeout=86400)

        async def agree_cb(inter: discord.Interaction):
            if inter.user.id in voters:
                await inter.response.send_message("Already voted.", ephemeral=True); return
            voters.add(inter.user.id)
            agree_count["n"] += 1
            await inter.response.send_message("✅ Agree logged.", ephemeral=True)

        async def dis_cb(inter: discord.Interaction):
            if inter.user.id in voters:
                await inter.response.send_message("Already voted.", ephemeral=True); return
            voters.add(inter.user.id)
            disagree_count["n"] += 1
            await inter.response.send_message("❌ Disagree logged.", ephemeral=True)

        ab = discord.ui.Button(label="✅ Agree", style=discord.ButtonStyle.success)
        db_btn = discord.ui.Button(label="❌ Nah", style=discord.ButtonStyle.danger)
        ab.callback  = agree_cb
        db_btn.callback = dis_cb
        view.add_item(ab)
        view.add_item(db_btn)

        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()

        async with get_db() as db:
            await db.execute(
                "INSERT INTO hot_takes (guild_id, user_id, take, message_id) VALUES (?,?,?,?)",
                (interaction.guild_id, interaction.user.id, take, msg.id))
            await db.commit()

        hot_ch = (discord.utils.get(interaction.guild.text_channels, name="🌶️・hot-takes") or
                  discord.utils.get(interaction.guild.text_channels, name="hot-takes"))
        if hot_ch and hot_ch.id != interaction.channel_id:
            await hot_ch.send(embed=embed)


# ─────────────────────────────────────────────────────────
# [LFG]
# ─────────────────────────────────────────────────────────

class LFG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lfg", description="🎮 Looking for group")
    @app_commands.describe(game="What game?", size="How many needed? (2–20)")
    async def lfg(self, interaction: discord.Interaction, game: str, size: int):
        if not 2 <= size <= 20:
            await interaction.response.send_message("Size must be 2–20.", ephemeral=True); return
        expires_at = datetime.utcnow() + timedelta(minutes=LFG_EXPIRY_MINUTES)
        members    = [interaction.user.id]

        embed = discord.Embed(title=f"🎮 LFG — {game}", color=PURPLE)
        embed.add_field(name="🎮 Game",    value=game, inline=True)
        embed.add_field(name="👥 Spots",   value=f"1/{size}", inline=True)
        embed.add_field(name="✅ Players", value=interaction.user.mention, inline=False)
        embed.add_field(name="⏰ Expires", value=f"<t:{int(expires_at.timestamp())}:R>", inline=False)
        embed.set_footer(text=bonfire_footer("LFG"))

        join_view = discord.ui.View(timeout=LFG_EXPIRY_MINUTES * 60)
        async def join_cb(inter: discord.Interaction):
            if inter.user.id in members:
                await inter.response.send_message("You're already in!", ephemeral=True); return
            members.append(inter.user.id)
            await inter.response.send_message(f"✅ Joined! ({len(members)}/{size})", ephemeral=True)
        join_btn = discord.ui.Button(label="✅ Join", style=discord.ButtonStyle.success)
        join_btn.callback = join_cb
        join_view.add_item(join_btn)

        await interaction.response.send_message(embed=embed, view=join_view)
        msg = await interaction.original_response()

        async with get_db() as db:
            await db.execute(
                "INSERT INTO lfg_lobbies (guild_id,channel_id,message_id,creator_id,game,size,members,expires_at)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (interaction.guild_id, interaction.channel_id, msg.id,
                 interaction.user.id, game, size, json.dumps(members), expires_at))
            await db.commit()


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
            embed.set_footer(text=bonfire_footer("Reminders"))
            await ch.send(content=u.mention if u else f"<@{user_id}>", embed=embed)
        async with get_db() as db:
            await db.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
            await db.commit()

    @app_commands.command(name="remind", description="⏰ Set a reminder (30m / 2h / 1h30m)")
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
        embed.add_field(name="📝 Message", value=message)
        embed.add_field(name="⏰ When",    value=f"<t:{int(trigger.timestamp())}:R>")
        embed.set_footer(text=bonfire_footer("Reminders"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="plan", description="📅 Plan a group activity with a shared reminder")
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
        embed = discord.Embed(
            title="📅 Activity Planned",
            description=f"**{activity}** starts in **{time}**",
            color=discord.Color.blue())
        embed.add_field(name="🧑 Scheduled by", value=interaction.user.mention)
        embed.add_field(name="⏰ When",         value=f"<t:{int(trigger.timestamp())}:R>")
        embed.set_footer(text=bonfire_footer("Plan"))
        await interaction.response.send_message(embed=embed)
        asyncio.create_task(
            self._fire(interaction.channel_id, interaction.user.id, f"🔔 Time for **{activity}**!", rid, secs))

    @app_commands.command(name="event", description="📅 Plan a real IRL or online event with RSVP")
    @app_commands.describe(title="Event name", when="When (e.g. 2h)", description="What's the plan?", location="IRL or Online")
    async def event(self, interaction: discord.Interaction,
                    title: str, when: str, description: str = None, location: str = "Online"):
        secs    = _parse_time(when)
        trigger = datetime.utcnow() + timedelta(seconds=secs) if secs else None

        embed = discord.Embed(title=f"📅 {title}", description=description or "No description yet.", color=TEAL)
        embed.add_field(name="📍 Location", value=location, inline=True)
        if trigger:
            embed.add_field(name="⏰ When", value=f"<t:{int(trigger.timestamp())}:R>", inline=True)
        else:
            embed.add_field(name="⏰ When", value=when, inline=True)
        embed.add_field(name="✅ Going", value="0", inline=True)
        embed.add_field(name="❌ Can't", value="0", inline=True)
        embed.set_author(name=f"Organized by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=bonfire_footer("Events"))

        yes_list = []; no_list = []
        view = discord.ui.View(timeout=None)

        async def yes_cb(inter: discord.Interaction):
            if inter.user.id not in yes_list:
                yes_list.append(inter.user.id)
                no_list[:] = [x for x in no_list if x != inter.user.id]
            await inter.response.send_message("✅ You're going!", ephemeral=True)

        async def no_cb(inter: discord.Interaction):
            if inter.user.id not in no_list:
                no_list.append(inter.user.id)
                yes_list[:] = [x for x in yes_list if x != inter.user.id]
            await inter.response.send_message("❌ Can't make it noted.", ephemeral=True)

        yb = discord.ui.Button(label="✅ Going", style=discord.ButtonStyle.success)
        nb = discord.ui.Button(label="❌ Can't", style=discord.ButtonStyle.danger)
        yb.callback = yes_cb
        nb.callback = no_cb
        view.add_item(yb); view.add_item(nb)

        await interaction.response.send_message(embed=embed, view=view)
        await log_timeline(interaction.guild_id, "📅", f"Event: {title}", [interaction.user.id])


# ─────────────────────────────────────────────────────────
# [HIGHLIGHTS]
# ─────────────────────────────────────────────────────────

class Highlights(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def post_highlight(self, message: discord.Message):
        async with get_db() as db:
            async with db.execute("SELECT message_id FROM highlights WHERE message_id=?", (message.id,)) as cur:
                if await cur.fetchone():
                    return
        ch = (discord.utils.get(message.guild.text_channels, name="⭐・highlights") or
              discord.utils.get(message.guild.text_channels, name="highlights"))
        if not ch:
            return
        embed = discord.Embed(description=message.content or "*[media]*",
                              color=discord.Color.gold(), timestamp=message.created_at)
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.add_field(name="🔗 Source",  value=f"[Jump]({message.jump_url})", inline=True)
        embed.add_field(name="📍 Channel", value=message.channel.mention,       inline=True)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        embed.set_footer(text=bonfire_footer("Highlights"))
        await ch.send(embed=embed)
        async with get_db() as db:
            await db.execute(
                "INSERT OR IGNORE INTO highlights (message_id,guild_id,channel_id,author_id,content,jump_url)"
                " VALUES (?,?,?,?,?,?)",
                (message.id, message.guild.id, message.channel.id,
                 message.author.id, message.content, message.jump_url))
            await db.commit()
        await log_timeline(message.guild.id, "⭐", f"{message.author.display_name}'s message was highlighted", [message.author.id])

    @app_commands.command(name="highlights", description="⭐ See recent bonfire highlights")
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
        embed.set_footer(text=bonfire_footer("Highlights"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [LORE]
# ─────────────────────────────────────────────────────────

class Lore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lore", description="📖 The lore archive — inside jokes, legendary moments")
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
                async with db.execute(
                    "SELECT COUNT(*) FROM lore WHERE guild_id=? AND author_id=?",
                    (interaction.guild_id, interaction.user.id)) as cur:
                    count = (await cur.fetchone())[0]
            embed = discord.Embed(title="📖 Lore Added", description=text, color=PURPLE)
            embed.set_footer(text=bonfire_footer("Lore"))
            await interaction.response.send_message(embed=embed)
            if count >= 10:
                await check_achievement(self.bot, interaction.guild_id, interaction.user.id, "lore_master")
            await log_timeline(interaction.guild_id, "📖", f"Lore added: {text[:60]}", [interaction.user.id])

        elif action == "random":
            async with get_db() as db:
                q = ("SELECT content,author_id,created_at FROM lore WHERE guild_id=?"
                     + (" AND target_id=?" if member else "") + " ORDER BY RANDOM() LIMIT 1")
                args = (interaction.guild_id, member.id) if member else (interaction.guild_id,)
                async with db.execute(q, args) as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.response.send_message("No lore yet. React 📖 on any message or `/lore add`.", ephemeral=True); return
            content, author_id, created_at = row
            author = interaction.guild.get_member(author_id)
            embed  = discord.Embed(title="📖 Bonfire Lore", description=content, color=PURPLE)
            embed.set_footer(text=bonfire_footer("Lore"))
            await interaction.response.send_message(embed=embed)

        elif action == "list":
            async with get_db() as db:
                async with db.execute(
                    "SELECT content,author_id,created_at FROM lore WHERE guild_id=?"
                    " ORDER BY created_at DESC LIMIT 8", (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No lore entries yet.", ephemeral=True); return
            embed = discord.Embed(title="📖 Recent Lore", color=PURPLE)
            for content, author_id, created_at in rows:
                author = interaction.guild.get_member(author_id)
                snip   = (content[:60] + "…") if len(content) > 60 else content
                embed.add_field(name=snip,
                                value=f"by {author.display_name if author else 'Unknown'} · {str(created_at)[:10]}",
                                inline=False)
            embed.set_footer(text=bonfire_footer("Lore"))
            await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [QUOTES]
# ─────────────────────────────────────────────────────────

class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quote", description="💬 Pull a saved quote from the archive")
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
        embed  = discord.Embed(description=f'"{content}"', color=TEAL)
        embed.set_author(name=author.display_name if author else "Unknown",
                         icon_url=author.display_avatar.url if author else None)
        embed.set_thumbnail(url=author.display_avatar.url if author else None)
        if jump_url:
            embed.add_field(name="🔗 Source", value=f"[Jump]({jump_url})")
        embed.set_footer(text=bonfire_footer("Quotes"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quotes", description="💬 List recent saved quotes")
    async def quotes_list(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT content,author_id,created_at FROM quotes WHERE guild_id=?"
                " ORDER BY created_at DESC LIMIT 8", (interaction.guild_id,)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message("No quotes yet. React 💬 to start.", ephemeral=True); return
        embed = discord.Embed(title="💬 Quotes Wall", color=TEAL)
        for content, author_id, _ in rows:
            author = interaction.guild.get_member(author_id)
            snip   = (content[:60] + "…") if len(content) > 60 else content
            embed.add_field(name=f'"{snip}"',
                            value=f"— {author.display_name if author else 'Unknown'}", inline=False)
        embed.set_footer(text=bonfire_footer("Quotes"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [BEEF]
# ─────────────────────────────────────────────────────────

class Beef(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="beef", description="🥩 Start, resolve, or view the beef leaderboard")
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
                        await interaction.response.send_message(f"Already beefing {member.display_name}.", ephemeral=True); return
                cur = await db.execute(
                    "INSERT INTO beef (guild_id,initiator_id,target_id,reason) VALUES (?,?,?,?)",
                    (interaction.guild_id, interaction.user.id, member.id, reason or "no reason given"))
                await db.commit()
                beef_id = cur.lastrowid
                async with db.execute(
                    "SELECT COUNT(*) FROM beef WHERE guild_id=? AND initiator_id=?",
                    (interaction.guild_id, interaction.user.id)) as cur:
                    beef_count = (await cur.fetchone())[0]

            embed = discord.Embed(title="🥩 BEEF INCOMING", color=discord.Color.red())
            embed.add_field(name="😤 From",   value=interaction.user.mention, inline=True)
            embed.add_field(name="🎯 With",   value=member.mention,            inline=True)
            embed.add_field(name="📝 Reason", value=reason or "no reason given", inline=False)
            embed.add_field(name="🆔 ID",     value=f"#{beef_id}",             inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=bonfire_footer("Beef"))

            view = discord.ui.View(timeout=None)
            async def truce_cb(inter: discord.Interaction):
                async with get_db() as db:
                    await db.execute("UPDATE beef SET resolved=1 WHERE id=?", (beef_id,))
                    await db.commit()
                await inter.response.send_message("🤝 Truce called.", ephemeral=True)
            truce_btn = discord.ui.Button(label="🤝 Call Truce", style=discord.ButtonStyle.success)
            truce_btn.callback = truce_cb
            view.add_item(truce_btn)

            await interaction.response.send_message(embed=embed, view=view)
            log_ch = (discord.utils.get(interaction.guild.text_channels, name="🥩・beef-log") or
                      discord.utils.get(interaction.guild.text_channels, name="beef-log"))
            if log_ch and log_ch.id != interaction.channel_id:
                await log_ch.send(embed=embed)

            if beef_count >= 5:
                await check_achievement(self.bot, interaction.guild_id, interaction.user.id, "beefcake")
            await log_timeline(interaction.guild_id, "🥩", f"Beef: {interaction.user.display_name} vs {member.display_name}",
                               [interaction.user.id, member.id])

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
                async with db.execute(
                    "SELECT COUNT(*) FROM beef WHERE guild_id=? AND (initiator_id=? OR target_id=?) AND resolved=1",
                    (interaction.guild_id, interaction.user.id, interaction.user.id)) as cur:
                    resolved_count = (await cur.fetchone())[0]

            embed = discord.Embed(title="🤝 Beef Squashed",
                                  description=f"{interaction.user.mention} and {member.mention} called it.",
                                  color=discord.Color.green())
            embed.set_footer(text=bonfire_footer("Beef"))
            await interaction.response.send_message(embed=embed)
            if resolved_count >= 3:
                await check_achievement(self.bot, interaction.guild_id, interaction.user.id, "peacemaker")
            await log_timeline(interaction.guild_id, "🤝", f"Beef resolved: {interaction.user.display_name} & {member.display_name}",
                               [interaction.user.id, member.id])

        elif action == "leaderboard":
            async with get_db() as db:
                async with db.execute(
                    "SELECT initiator_id, COUNT(*) cnt FROM beef WHERE guild_id=?"
                    " GROUP BY initiator_id ORDER BY cnt DESC LIMIT 10", (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No beefs yet.", ephemeral=True); return
            embed = discord.Embed(title="🥩 Beef Leaderboard", color=discord.Color.red())
            medals = ["🥇", "🥈", "🥉"]
            for i, (uid, cnt) in enumerate(rows, 1):
                m = interaction.guild.get_member(uid)
                medal = medals[i-1] if i <= 3 else f"#{i}"
                embed.add_field(name=f"{medal} {m.display_name if m else uid}",
                                value=f"{cnt} beef(s) started", inline=True)
            embed.set_footer(text=bonfire_footer("Beef"))
            await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [VIBE]
# ─────────────────────────────────────────────────────────

class VibeCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vibecheck", description="📊 Rate the group energy — anonymous 1–5")
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
        embed = discord.Embed(title="📊 Vibe Check", color=PURPLE)
        embed.add_field(name="🎭 Your Score",           value=f"{bars} ({score}/5)", inline=False)
        embed.add_field(name="📈 Server Average Today", value=f"{avg:.1f}/5 ({count} votes)", inline=False)
        embed.set_footer(text=bonfire_footer("Vibe Check"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="vibereport", description="📈 See this week's vibe report")
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
        embed = discord.Embed(title="📈 Weekly Vibe Report", color=PURPLE)
        for day, avg, cnt in rows:
            bars = "█" * round(avg) + "░" * (5 - round(avg))
            embed.add_field(name=day, value=f"{bars} {avg:.1f}/5 ({cnt} votes)", inline=True)
        overall = sum(r[1] for r in rows) / len(rows)
        embed.set_footer(text=bonfire_footer("Vibe Report") + f" · 7-day avg: {overall:.1f}/5")
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
                    ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                          discord.utils.get(guild.text_channels, name="general"))
                    if ch:
                        await ch.send(embed=discord.Embed(
                            title="💔 STREAK BROKEN",
                            description=f"The {current}-day bonfire streak just ended. Restart it today.",
                            color=discord.Color.red()))

    @app_commands.command(name="streak", description="🔥 Check the server's daily activity streak")
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
        embed.add_field(name="📈 Current",     value=f"{current} day(s) {fire}", inline=True)
        embed.add_field(name="🏆 Best",        value=f"{longest} day(s)",         inline=True)
        embed.add_field(name="📅 Last Active", value=last or "Never",             inline=True)
        embed.set_footer(text=bonfire_footer("Streak"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [WRAPPED]
# ─────────────────────────────────────────────────────────

class Wrapped(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wrapped", description="🎁 Monthly Bonfire Wrapped — your squad's recap")
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
                "SELECT COUNT(*) FROM member_intros WHERE guild_id=? AND created_at>=?", (gid, month_ago)) as cur:
                new_homiez = (await cur.fetchone())[0]

        now = datetime.utcnow()
        embed = discord.Embed(
            title=f"🎁 Bonfire Wrapped — {now.strftime('%B %Y')}",
            description="Spotify Wrapped but make it the squad.",
            color=PRIMARY)

        if top_talkers:
            lines = []
            for i, (uid, cnt) in enumerate(top_talkers, 1):
                m = interaction.guild.get_member(uid)
                bar = progress_bar(cnt, top_talkers[0][1])
                lines.append(f"**#{i}** {m.display_name if m else uid} {bar} {cnt}")
            embed.add_field(name="💬 Most Active", value="\n".join(lines), inline=False)
        embed.add_field(name="📖 Lore Added",  value=str(lore_count),      inline=True)
        embed.add_field(name="⭐ Highlights",   value=str(highlight_count), inline=True)
        embed.add_field(name="🆕 New Homiez",   value=str(new_homiez),      inline=True)
        if top_quoted:
            m = interaction.guild.get_member(top_quoted[0])
            embed.add_field(name="💬 Most Quoted", value=f"{m.display_name if m else top_quoted[0]} ({top_quoted[1]}x)", inline=True)
        if top_beef:
            m = interaction.guild.get_member(top_beef[0])
            embed.add_field(name="🥩 Beef King", value=f"{m.display_name if m else top_beef[0]} ({top_beef[1]})", inline=True)
        embed.set_footer(text=bonfire_footer("Wrapped"))
        await interaction.followup.send(embed=embed)


# ─────────────────────────────────────────────────────────
# [CLUTCH]
# ─────────────────────────────────────────────────────────

class Clutch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clutch", description="🔔 Opt in/out of Clutch Mode pings")
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
        ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
              discord.utils.get(guild.text_channels, name="general"))
        if ch:
            await ch.send(msg)
        async with get_db() as db:
            await db.execute(
                "INSERT INTO clutch_cooldown (guild_id,channel_id,last_ping) VALUES (?,?,?)"
                " ON CONFLICT(guild_id,channel_id) DO UPDATE SET last_ping=excluded.last_ping",
                (guild.id, channel.id, now.isoformat()))
            await db.commit()


# ─────────────────────────────────────────────────────────
# [ROLES]
# ─────────────────────────────────────────────────────────

class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _ensure_tracking(self, guild_id: int, user_id: int):
        async with get_db() as db:
            await db.execute("INSERT OR IGNORE INTO role_tracking (guild_id, user_id) VALUES (?,?)", (guild_id, user_id))
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
                    ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                          discord.utils.get(guild.text_channels, name="general"))
                    if ch:
                        await ch.send(embed=discord.Embed(
                            description=f"🎉 {member.mention} earned the **💬 Regular** role. They're a real one now.",
                            color=TEAL))
        if row and row[0] >= 500:
            await check_achievement(self.bot, guild_id, user_id, "yapper")

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
                    await member.add_roles(owl_role, reason="Earned Night Owl")
                    ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                          discord.utils.get(guild.text_channels, name="general"))
                    if ch:
                        await ch.send(embed=discord.Embed(
                            description=f"🌙 {member.mention} earned **🌙 Night Owl**. Never sleeps, always there.",
                            color=discord.Color.from_str("#2C3E50")))
            await check_achievement(self.bot, guild_id, user_id, "3am_club")


# ─────────────────────────────────────────────────────────
# [STORY]
# ─────────────────────────────────────────────────────────

class Story(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="story", description="🏕️ Add to the campfire story — one line at a time")
    @app_commands.describe(line="Your line (max 200 chars)")
    async def story(self, interaction: discord.Interaction, line: str):
        if len(line) > 200:
            await interaction.response.send_message("Keep it under 200 chars.", ephemeral=True); return
        async with get_db() as db:
            async with db.execute(
                "SELECT author_id FROM story WHERE guild_id=? ORDER BY id DESC LIMIT 1",
                (interaction.guild_id,)) as cur:
                last = await cur.fetchone()
            if last and last[0] == interaction.user.id:
                await interaction.response.send_message(
                    "You wrote the last line. Let someone else add one first.", ephemeral=True); return

            async with db.execute("SELECT COUNT(*) FROM story WHERE guild_id=?", (interaction.guild_id,)) as cur:
                count = (await cur.fetchone())[0]

            if count == 0:
                starter = random.choice(STORY_STARTERS)
                await db.execute("INSERT INTO story (guild_id, author_id, line) VALUES (?,?,?)",
                                 (interaction.guild_id, self.bot.user.id, starter))

            await db.execute("INSERT INTO story (guild_id, author_id, line) VALUES (?,?,?)",
                             (interaction.guild_id, interaction.user.id, line))
            await db.commit()

            async with db.execute(
                "SELECT author_id, line FROM story WHERE guild_id=? ORDER BY id DESC LIMIT 5",
                (interaction.guild_id,)) as cur:
                recent = list(reversed(await cur.fetchall()))

            async with db.execute("SELECT COUNT(*) FROM story WHERE guild_id=?", (interaction.guild_id,)) as cur:
                total_lines = (await cur.fetchone())[0]

        embed = discord.Embed(title="🏕️ Campfire Story", color=ORANGE)
        story_text = ""
        for aid, l in recent:
            author = interaction.guild.get_member(aid)
            name   = author.display_name if author else ("Bot" if aid == self.bot.user.id else "Unknown")
            story_text += f"*{l}*  — {name}\n"
        embed.description = story_text
        embed.set_footer(text=bonfire_footer("Story") + f" · Line {total_lines}")
        await interaction.response.send_message(embed=embed)

        story_ch = (discord.utils.get(interaction.guild.text_channels, name="🏕️・campfire-story") or
                    discord.utils.get(interaction.guild.text_channels, name="campfire-story"))
        if story_ch and story_ch.id != interaction.channel_id:
            await story_ch.send(embed=embed)

        if total_lines >= 20:
            await check_achievement(self.bot, interaction.guild_id, interaction.user.id, "storyteller")

    @app_commands.command(name="fullstory", description="📖 Read the full campfire story so far")
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
            embed = discord.Embed(title=title, description=chunk, color=ORANGE)
            if i == len(chunks) - 1:
                embed.set_footer(text=bonfire_footer("Story") + f" · {len(rows)} lines written")
            if i == 0:
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.followup.send(embed=embed)


# ─────────────────────────────────────────────────────────
# [VOUCH]
# ─────────────────────────────────────────────────────────

class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vouch", description="✅ Vouch for a new member — Core/OG only")
    @app_commands.describe(member="Who are you vouching for?", note="Why should they be here?")
    async def vouch(self, interaction: discord.Interaction, member: discord.Member, note: str = None):
        if not _is_core(interaction.user):
            await interaction.response.send_message("Only Core/OG can vouch.", ephemeral=True); return
        async with get_db() as db:
            async with db.execute(
                "SELECT id FROM vouches WHERE guild_id=? AND target_id=? AND voucher_id=?",
                (interaction.guild_id, member.id, interaction.user.id)) as cur:
                if await cur.fetchone():
                    await interaction.response.send_message(f"Already vouched for {member.display_name}.", ephemeral=True); return
            await db.execute(
                "INSERT INTO vouches (guild_id, target_id, voucher_id, note) VALUES (?,?,?,?)",
                (interaction.guild_id, member.id, interaction.user.id, note or "No note"))
            await db.commit()
            async with db.execute(
                "SELECT COUNT(*) FROM vouches WHERE guild_id=? AND target_id=?",
                (interaction.guild_id, member.id)) as cur:
                vouch_count = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(DISTINCT target_id) FROM vouches WHERE guild_id=? AND voucher_id=?",
                (interaction.guild_id, interaction.user.id)) as cur:
                my_vouches = (await cur.fetchone())[0]

        embed = discord.Embed(
            title=f"✅ Vouch — {member.display_name}",
            description=f"{interaction.user.mention} vouched for {member.mention}",
            color=discord.Color.green())
        if note:
            embed.add_field(name="📝 Note", value=note)
        embed.add_field(name="🔢 Total Vouches", value=str(vouch_count))
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=bonfire_footer("Vouch"))
        await interaction.response.send_message(embed=embed)
        if my_vouches >= 3:
            await check_achievement(self.bot, interaction.guild_id, interaction.user.id, "welcome_wagon")

    @app_commands.command(name="vouches", description="✅ See vouches for a member")
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
                            value=note or "No note", inline=True)
        embed.set_footer(text=bonfire_footer("Vouch"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [WEATHER]
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
            ch = (discord.utils.get(guild.text_channels, name="📊・status") or
                  discord.utils.get(guild.text_channels, name="status") or
                  discord.utils.get(guild.text_channels, name="🔥・general"))
            if ch:
                title, desc = random.choice(WEATHER_FORECASTS)
                embed = discord.Embed(
                    title=f"🌤️ Daily Forecast — {datetime.utcnow().strftime('%A %b %d')}",
                    description=f"**{title}**\n{desc}",
                    color=PRIMARY)
                embed.set_footer(text=bonfire_footer("Weather"))
                await ch.send(embed=embed)

    @daily_forecast.before_loop
    async def before_forecast(self):
        await self.bot.wait_until_ready()
        now    = datetime.utcnow()
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

    @app_commands.command(name="forecast", description="🌤️ Get today's server vibe forecast")
    async def forecast(self, interaction: discord.Interaction):
        title, desc = random.choice(WEATHER_FORECASTS)
        embed = discord.Embed(
            title="🌤️ Today's Forecast",
            description=f"**{title}**\n{desc}",
            color=PRIMARY)
        embed.set_footer(text=bonfire_footer("Forecast"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [CHALLENGE]
# ─────────────────────────────────────────────────────────

class Challenge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_post.start()

    def cog_unload(self):
        self.weekly_post.cancel()

    @tasks.loop(hours=168)
    async def weekly_post(self):
        for guild in self.bot.guilds:
            ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                  discord.utils.get(guild.text_channels, name="general"))
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
                color=TEAL,
                timestamp=datetime.utcnow())
            embed.add_field(name="⏰ Duration", value="7 days", inline=True)
            embed.add_field(name="✅ Complete?", value="Click the button to mark done", inline=True)
            embed.set_footer(text=bonfire_footer("Challenge"))

            view = discord.ui.View(timeout=604800)
            completions = []
            async def done_cb(inter: discord.Interaction):
                if inter.user.id in completions:
                    await inter.response.send_message("Already marked!", ephemeral=True); return
                completions.append(inter.user.id)
                async with get_db() as db:
                    await db.execute(
                        "UPDATE weekly_challenge SET completions=? WHERE guild_id=?",
                        (json.dumps(completions), guild.id))
                    await db.commit()
                await inter.response.send_message(f"✅ Marked complete! ({len(completions)} total)", ephemeral=True)
                async with get_db() as db:
                    async with db.execute(
                        "SELECT COUNT(*) FROM achievements WHERE guild_id=? AND user_id=? AND badge_key='never_miss'",
                        (guild.id, inter.user.id)) as cur:
                        already = (await cur.fetchone())[0]
                if not already and len(completions) >= 3:
                    await check_achievement(self.bot, guild.id, inter.user.id, "never_miss")
            done_btn = discord.ui.Button(label="✅ I did it", style=discord.ButtonStyle.success)
            done_btn.callback = done_cb
            view.add_item(done_btn)
            await ch.send(embed=embed, view=view)
            await log_timeline(guild.id, "🎯", f"Weekly challenge: {challenge[:60]}")

    @weekly_post.before_loop
    async def before_weekly(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0 and now.hour >= 10:
            days_until_monday = 7
        target = (now + timedelta(days=days_until_monday)).replace(hour=10, minute=0, second=0, microsecond=0)
        await asyncio.sleep((target - now).total_seconds())

    @app_commands.command(name="challenge", description="🎯 See the current weekly challenge")
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

        embed = discord.Embed(title="🎯 This Week's Challenge", description=f"**{challenge}**", color=TEAL)
        done  = [interaction.guild.get_member(uid) for uid in completions_list]
        done  = [m for m in done if m]
        if done:
            embed.add_field(name="✅ Completed by", value=", ".join(m.display_name for m in done), inline=False)
        embed.set_footer(text=bonfire_footer("Challenge"))
        await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [LATE NIGHT CHECK-IN]  — Feature 1
# ─────────────────────────────────────────────────────────

class LateNight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.nightly_summary.start()

    def cog_unload(self):
        self.nightly_summary.cancel()

    @app_commands.command(name="latenight", description="🌙 What's on your mind tonight?")
    async def latenight(self, interaction: discord.Interaction):
        today = datetime.utcnow().date().isoformat()
        async with get_db() as db:
            async with db.execute(
                "SELECT id FROM late_night_checkins WHERE guild_id=? AND user_id=? AND DATE(created_at)=?",
                (interaction.guild_id, interaction.user.id, today)) as cur:
                if await cur.fetchone():
                    await interaction.response.send_message("Already checked in tonight. See you tomorrow 🌙", ephemeral=True)
                    return

        embed = discord.Embed(title="🌙 Late Night Check-in", description="How you feeling tonight?", color=DARK_GREY)
        embed.set_footer(text=bonfire_footer("Late Night"))
        view = discord.ui.View(timeout=300)
        chosen_mood = {}

        for mood, label in [("😴", "tired"), ("😤", "venting"), ("🔥", "hyped"), ("😶", "just here")]:
            async def cb(inter: discord.Interaction, m=mood, l=label):
                modal = LateNightModal(self.bot, interaction.guild_id, m, l)
                await inter.response.send_modal(modal)
            btn = discord.ui.Button(label=f"{mood} {label}", style=discord.ButtonStyle.secondary)
            btn.callback = cb
            view.add_item(btn)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @tasks.loop(hours=24)
    async def nightly_summary(self):
        for guild in self.bot.guilds:
            yesterday = (datetime.utcnow() - timedelta(hours=1)).date().isoformat()
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, mood, note FROM late_night_checkins"
                    " WHERE guild_id=? AND DATE(created_at)=?",
                    (guild.id, yesterday)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                continue
            ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                  discord.utils.get(guild.text_channels, name="general"))
            if not ch:
                continue
            embed = discord.Embed(
                title=f"🌙 Last Night's Vibe — {yesterday}",
                description=f"{len(rows)} people checked in last night",
                color=DARK_GREY)
            mood_counts = defaultdict(int)
            for uid, mood, note in rows:
                mood_counts[mood] += 1
            for mood, cnt in mood_counts.items():
                embed.add_field(name=mood, value=str(cnt), inline=True)
            embed.set_footer(text=bonfire_footer("Late Night"))
            await ch.send(embed=embed)

    @nightly_summary.before_loop
    async def before_nightly(self):
        await self.bot.wait_until_ready()
        now    = datetime.utcnow()
        target = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())


class LateNightModal(discord.ui.Modal, title="🌙 Late Night Check-in"):
    note = discord.ui.TextInput(label="Anything on your mind? (optional)", required=False, max_length=200,
                                style=discord.TextStyle.paragraph, placeholder="or just leave blank and vibe")

    def __init__(self, bot, guild_id, mood, label):
        super().__init__()
        self.bot      = bot
        self.guild_id = guild_id
        self.mood     = mood
        self.label    = label

    async def on_submit(self, interaction: discord.Interaction):
        async with get_db() as db:
            await db.execute(
                "INSERT INTO late_night_checkins (guild_id, user_id, mood, note) VALUES (?,?,?,?)",
                (self.guild_id, interaction.user.id, self.mood, self.note.value or ""))
            await db.commit()
            # Night Owl badge — 5 nights in a row
            async with db.execute(
                "SELECT COUNT(*) FROM late_night_checkins WHERE guild_id=? AND user_id=?"
                " AND created_at >= datetime('now', '-5 days')",
                (self.guild_id, interaction.user.id)) as cur:
                streak_count = (await cur.fetchone())[0]
        if streak_count >= 5:
            await check_achievement(self.bot, self.guild_id, interaction.user.id, "night_owl_badge")
        await interaction.response.send_message(
            f"🌙 Checked in as **{self.mood} {self.label}**. Good night.", ephemeral=True)


# ─────────────────────────────────────────────────────────
# [MEETUP PLANNER]  — Feature 2
# ─────────────────────────────────────────────────────────

class Meetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="meetup", description="📍 Plan, recap, or view meetup history")
    @app_commands.describe(action="What to do")
    @app_commands.choices(action=[
        app_commands.Choice(name="Plan a meetup",    value="plan"),
        app_commands.Choice(name="Recap a meetup",   value="recap"),
        app_commands.Choice(name="View history",     value="history"),
    ])
    async def meetup(self, interaction: discord.Interaction, action: str):
        if action == "plan":
            await interaction.response.send_modal(MeetupPlanModal(self.bot))
        elif action == "recap":
            async with get_db() as db:
                async with db.execute(
                    "SELECT id, title FROM meetups WHERE guild_id=? AND completed=0 ORDER BY created_at DESC LIMIT 5",
                    (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No recent meetups to recap.", ephemeral=True); return
            embed = discord.Embed(title="📍 Select a meetup to recap", color=TEAL)
            for mid, title in rows:
                embed.add_field(name=f"#{mid}", value=title, inline=True)
            embed.set_footer(text="Use /meetup recap then enter the ID in the modal")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif action == "history":
            await interaction.response.defer()
            async with get_db() as db:
                async with db.execute(
                    "SELECT m.id, m.title, m.meetup_time, m.rsvp_yes,"
                    " AVG(mm.rating), COUNT(mm.id)"
                    " FROM meetups m LEFT JOIN meetup_memories mm ON m.id=mm.meetup_id"
                    " WHERE m.guild_id=?"
                    " GROUP BY m.id ORDER BY m.meetup_time DESC LIMIT 10",
                    (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.followup.send("No meetups yet. Use `/meetup plan` to plan one!", ephemeral=True); return
            embed = discord.Embed(title="📍 Meetup History", color=TEAL)
            for mid, title, mtime, rsvp_yes, avg_rating, memory_count in rows:
                attendees = len(json.loads(rsvp_yes or "[]"))
                rating_str = f"⭐ {avg_rating:.1f}" if avg_rating else "No ratings"
                embed.add_field(
                    name=f"#{mid} — {title}",
                    value=f"📅 {str(mtime)[:10]} · 👥 {attendees} going · {rating_str} · {memory_count} memories",
                    inline=False)
            embed.set_footer(text=bonfire_footer("Meetups"))
            await interaction.followup.send(embed=embed)


class MeetupPlanModal(discord.ui.Modal, title="📍 Plan a Meetup"):
    m_title    = discord.ui.TextInput(label="Event Title", max_length=80)
    m_date     = discord.ui.TextInput(label="Date & Time", max_length=50, placeholder="e.g. Saturday June 15 7pm")
    m_location = discord.ui.TextInput(label="Location (IRL or Online)", max_length=100)
    m_desc     = discord.ui.TextInput(label="Description", required=False, max_length=300,
                                      style=discord.TextStyle.paragraph)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with get_db() as db:
            cur = await db.execute(
                "INSERT INTO meetups (guild_id, creator_id, title, description, location, meetup_time)"
                " VALUES (?,?,?,?,?,?)",
                (interaction.guild_id, interaction.user.id,
                 self.m_title.value, self.m_desc.value, self.m_location.value, self.m_date.value))
            await db.commit()
            meetup_id = cur.lastrowid

        embed = discord.Embed(title=f"📍 {self.m_title.value}", description=self.m_desc.value or "", color=TEAL)
        embed.add_field(name="📅 When",     value=self.m_date.value,     inline=True)
        embed.add_field(name="📍 Location", value=self.m_location.value, inline=True)
        embed.add_field(name="✅ Going",    value="0",                   inline=True)
        embed.add_field(name="❌ Can't",    value="0",                   inline=True)
        embed.add_field(name="🤔 Maybe",   value="0",                   inline=True)
        embed.set_author(name=f"Planned by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=bonfire_footer("Meetups"))

        yes_list = []; no_list = []; maybe_list = []
        view = discord.ui.View(timeout=None)

        async def yes_cb(inter: discord.Interaction):
            if inter.user.id not in yes_list:
                yes_list.append(inter.user.id)
                no_list[:] = [x for x in no_list if x != inter.user.id]
                maybe_list[:] = [x for x in maybe_list if x != inter.user.id]
                async with get_db() as db:
                    await db.execute("UPDATE meetups SET rsvp_yes=? WHERE id=?", (json.dumps(yes_list), meetup_id))
                    await db.commit()
            await inter.response.send_message("✅ You're going!", ephemeral=True)

        async def no_cb(inter: discord.Interaction):
            if inter.user.id not in no_list:
                no_list.append(inter.user.id)
                yes_list[:] = [x for x in yes_list if x != inter.user.id]
                maybe_list[:] = [x for x in maybe_list if x != inter.user.id]
                async with get_db() as db:
                    await db.execute("UPDATE meetups SET rsvp_no=? WHERE id=?", (json.dumps(no_list), meetup_id))
                    await db.commit()
            await inter.response.send_message("❌ Can't make it.", ephemeral=True)

        async def maybe_cb(inter: discord.Interaction):
            if inter.user.id not in maybe_list:
                maybe_list.append(inter.user.id)
                yes_list[:] = [x for x in yes_list if x != inter.user.id]
                no_list[:] = [x for x in no_list if x != inter.user.id]
                async with get_db() as db:
                    await db.execute("UPDATE meetups SET rsvp_maybe=? WHERE id=?", (json.dumps(maybe_list), meetup_id))
                    await db.commit()
            await inter.response.send_message("🤔 Maybe noted.", ephemeral=True)

        yb = discord.ui.Button(label="✅ Going",  style=discord.ButtonStyle.success)
        nb = discord.ui.Button(label="❌ Can't",  style=discord.ButtonStyle.danger)
        mb = discord.ui.Button(label="🤔 Maybe", style=discord.ButtonStyle.secondary)
        yb.callback = yes_cb; nb.callback = no_cb; mb.callback = maybe_cb
        view.add_item(yb); view.add_item(nb); view.add_item(mb)

        meetup_ch = (discord.utils.get(interaction.guild.text_channels, name="🗺️・meetups") or
                     discord.utils.get(interaction.guild.text_channels, name="meetups"))
        target_ch = meetup_ch or interaction.channel
        msg = await target_ch.send(embed=embed, view=view)

        async with get_db() as db:
            await db.execute("UPDATE meetups SET message_id=? WHERE id=?", (msg.id, meetup_id))
            await db.commit()

        await interaction.followup.send(f"✅ Meetup posted! #{meetup_id}", ephemeral=True)
        await log_timeline(interaction.guild_id, "📍", f"Meetup planned: {self.m_title.value}", [interaction.user.id])


# ─────────────────────────────────────────────────────────
# [WEEKLY DIGEST]  — Feature 3
# ─────────────────────────────────────────────────────────

class WeeklyDigest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_digest.start()

    def cog_unload(self):
        self.weekly_digest.cancel()

    @tasks.loop(hours=168)
    async def weekly_digest(self):
        for guild in self.bot.guilds:
            ch = (discord.utils.get(guild.text_channels, name="📊・status") or
                  discord.utils.get(guild.text_channels, name="status"))
            if not ch:
                continue
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, COUNT(*) cnt FROM activity_log"
                    " WHERE guild_id=? AND created_at>=? AND activity_type='message'"
                    " GROUP BY user_id ORDER BY cnt DESC LIMIT 3", (guild.id, week_ago)) as cur:
                    top = await cur.fetchall()
                async with db.execute(
                    "SELECT COUNT(*) FROM highlights WHERE guild_id=? AND posted_at>=?", (guild.id, week_ago)) as cur:
                    h_count = (await cur.fetchone())[0]
                async with db.execute(
                    "SELECT COUNT(*) FROM quotes WHERE guild_id=? AND created_at>=?", (guild.id, week_ago)) as cur:
                    q_count = (await cur.fetchone())[0]
                async with db.execute(
                    "SELECT COUNT(*) FROM beef WHERE guild_id=? AND created_at>=?", (guild.id, week_ago)) as cur:
                    b_count = (await cur.fetchone())[0]
                async with db.execute(
                    "SELECT content FROM lore WHERE guild_id=? ORDER BY RANDOM() LIMIT 1", (guild.id,)) as cur:
                    funniest = await cur.fetchone()
                async with db.execute(
                    "SELECT current_streak FROM streaks WHERE guild_id=?", (guild.id,)) as cur:
                    streak_row = await cur.fetchone()

            embed = discord.Embed(
                title=f"🔥 This Week at the Bonfire — {datetime.utcnow().strftime('%b %d')}",
                color=PRIMARY)
            if top:
                top_str = " · ".join(
                    f"{(guild.get_member(uid) or uid).display_name if guild.get_member(uid) else uid} ({cnt})"
                    for uid, cnt in top)
                embed.add_field(name="💬 Most Active", value=top_str, inline=False)
            embed.add_field(name="⭐ Highlights",  value=str(h_count), inline=True)
            embed.add_field(name="💬 New Quotes",  value=str(q_count), inline=True)
            embed.add_field(name="🥩 Beefs",       value=str(b_count), inline=True)
            if streak_row:
                embed.add_field(name="🔥 Streak", value=f"{streak_row[0]} days", inline=True)
            if funniest:
                snip = funniest[0][:80] + ("…" if len(funniest[0]) > 80 else "")
                embed.add_field(name="📖 Lore of the Week", value=f'*"{snip}"*', inline=False)
            embed.set_footer(text=bonfire_footer("Weekly Digest"))
            await ch.send(embed=embed)

    @weekly_digest.before_loop
    async def before_digest(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        # Next Sunday 6pm UTC
        days_until_sunday = (6 - now.weekday()) % 7
        if days_until_sunday == 0 and now.hour >= 18:
            days_until_sunday = 7
        target = (now + timedelta(days=days_until_sunday)).replace(hour=18, minute=0, second=0, microsecond=0)
        await asyncio.sleep((target - now).total_seconds())


# ─────────────────────────────────────────────────────────
# [ICEBREAKER]  — Feature 4
# ─────────────────────────────────────────────────────────

class Icebreaker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="icebreaker", description="🧊 Post a random deep/fun question to the squad")
    async def icebreaker(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with get_db() as db:
            async with db.execute(
                "SELECT id, question, category FROM icebreakers WHERE used=0 ORDER BY RANDOM() LIMIT 1") as cur:
                row = await cur.fetchone()
            if not row:
                await db.execute("UPDATE icebreakers SET used=0")
                await db.commit()
                async with db.execute(
                    "SELECT id, question, category FROM icebreakers ORDER BY RANDOM() LIMIT 1") as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.followup.send("No icebreaker questions available.", ephemeral=True); return
            q_id, question, category = row
            await db.execute(
                "INSERT INTO icebreakers (guild_id, question, category, used, posted_at) VALUES (?,?,?,1,?)",
                (interaction.guild_id, question, category, datetime.utcnow()))
            await db.commit()

        members = [m for m in interaction.guild.members if not m.bot]
        mentions = " ".join(m.mention for m in members[:15])

        embed = discord.Embed(
            title=f"🧊 Icebreaker — {category.title()}",
            description=f"**{question}**",
            color=TEAL)
        embed.set_footer(text=bonfire_footer("Icebreaker"))

        view = discord.ui.View(timeout=86400)
        reacts = {"🔥": 0, "💀": 0, "👀": 0}

        for emoji in ["🔥", "💀", "👀"]:
            async def cb(inter: discord.Interaction, e=emoji):
                reacts[e] += 1
                async with get_db() as db:
                    await db.execute(
                        "INSERT OR IGNORE INTO icebreaker_answers (guild_id, user_id, icebreaker_id) VALUES (?,?,?)",
                        (interaction.guild_id, inter.user.id, q_id))
                    await db.commit()
                    async with db.execute(
                        "SELECT COUNT(*) FROM icebreaker_answers WHERE guild_id=? AND user_id=?",
                        (interaction.guild_id, inter.user.id)) as cur:
                        ans_count = (await cur.fetchone())[0]
                if ans_count >= 10:
                    await check_achievement(self.bot, interaction.guild_id, inter.user.id, "icebreaker_king")
                await inter.response.send_message(f"{e} reaction logged!", ephemeral=True)
            btn = discord.ui.Button(label=emoji, style=discord.ButtonStyle.secondary)
            btn.callback = cb
            view.add_item(btn)

        ch = (discord.utils.get(interaction.guild.text_channels, name="🔥・general") or
              discord.utils.get(interaction.guild.text_channels, name="general"))
        if ch:
            await ch.send(content=mentions if mentions else None, embed=embed, view=view)
            await interaction.followup.send(f"✅ Icebreaker posted to {ch.mention}!", ephemeral=True)
        else:
            await interaction.followup.send(embed=embed, view=view)


# ─────────────────────────────────────────────────────────
# [VIBE PULSE]  — Feature 5
# ─────────────────────────────────────────────────────────

class VibePulse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.friday_pulse.start()

    def cog_unload(self):
        self.friday_pulse.cancel()

    @tasks.loop(hours=24)
    async def friday_pulse(self):
        if datetime.utcnow().weekday() != 4:  # Friday
            return
        for guild in self.bot.guilds:
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id FROM vibe_pulse_optout WHERE guild_id=?", (guild.id,)) as cur:
                    opted_out = {r[0] for r in await cur.fetchall()}
            for member in guild.members:
                if member.bot or member.id in opted_out:
                    continue
                try:
                    embed = discord.Embed(
                        title="🩺 Friday Vibe Pulse",
                        description=f"Hey **{member.display_name}** — how's the week been?\nDrop a number **1–5** and one word.",
                        color=PURPLE)
                    embed.set_footer(text="Reply here · opt out with /pulse off in the server")
                    await member.send(embed=embed)
                except discord.Forbidden:
                    pass

    @friday_pulse.before_loop
    async def before_pulse(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        target = now.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

    @app_commands.command(name="pulse", description="🩺 Opt in/out of Friday vibe pulse DMs")
    @app_commands.choices(action=[
        app_commands.Choice(name="Turn off", value="off"),
        app_commands.Choice(name="Turn on",  value="on"),
    ])
    async def pulse(self, interaction: discord.Interaction, action: str):
        if action == "off":
            async with get_db() as db:
                await db.execute("INSERT OR IGNORE INTO vibe_pulse_optout (guild_id, user_id) VALUES (?,?)",
                                 (interaction.guild_id, interaction.user.id))
                await db.commit()
            await interaction.response.send_message("🔕 You've opted out of Friday pulse DMs.", ephemeral=True)
        else:
            async with get_db() as db:
                await db.execute("DELETE FROM vibe_pulse_optout WHERE guild_id=? AND user_id=?",
                                 (interaction.guild_id, interaction.user.id))
                await db.commit()
            await interaction.response.send_message("🔔 You're back in the Friday pulse.", ephemeral=True)


# ─────────────────────────────────────────────────────────
# [ACHIEVEMENTS]  — Feature 6
# ─────────────────────────────────────────────────────────

BADGE_DEFS = {
    "fire_starter":    ("🔥", "Fire Starter",      "First to use /start"),
    "yapper":          ("💬", "Yapper",             "500 messages sent"),
    "beefcake":        ("🥩", "Certified Beefcake", "Started 5 beefs"),
    "3am_club":        ("🌙", "3AM Club",           "In VC after 3am five times"),
    "lore_master":     ("📖", "Lore Master",        "Added 10 lore entries"),
    "never_miss":      ("🎯", "Never Miss",         "Completed 3 weekly challenges"),
    "peacemaker":      ("🤝", "Peacemaker",         "Resolved 3 beefs"),
    "welcome_wagon":   ("🆕", "Welcome Wagon",      "Vouched for 3 new members"),
    "night_owl_badge": ("🦉", "Night Owl",          "Checked in 5 nights in a row"),
    "prophet":         ("🔮", "Prophet",            "Won 5 bets"),
    "storyteller":     ("🏕️", "Storyteller",        "Added 20 story lines"),
    "icebreaker_king": ("🧊", "Icebreaker King",    "Answered 10 icebreakers"),
}


class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="achievements", description="🏆 View your unlocked badges")
    @app_commands.describe(member="Whose achievements to view")
    async def achievements(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        async with get_db() as db:
            async with db.execute(
                "SELECT badge_key, unlocked_at FROM achievements WHERE guild_id=? AND user_id=?"
                " ORDER BY unlocked_at ASC",
                (interaction.guild_id, target.id)) as cur:
                rows = await cur.fetchall()

        unlocked = {r[0]: r[1] for r in rows}
        embed = discord.Embed(
            title=f"🏆 {target.display_name}'s Achievements",
            color=PURPLE)
        embed.set_thumbnail(url=target.display_avatar.url)

        for key, (emoji, name, desc) in BADGE_DEFS.items():
            if key in unlocked:
                embed.add_field(name=f"{emoji} {name}", value=f"✅ {desc}\n*Unlocked {str(unlocked[key])[:10]}*", inline=True)
            else:
                embed.add_field(name=f"🔒 {name}", value=f"*{desc}*", inline=True)

        embed.set_footer(text=bonfire_footer("Achievements") + f" · {len(unlocked)}/{len(BADGE_DEFS)} unlocked")
        await interaction.response.send_message(embed=embed, ephemeral=(member is None))


# ─────────────────────────────────────────────────────────
# [SQUAD POLL]  — Feature 7
# ─────────────────────────────────────────────────────────

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="🗳️ Create a poll with up to 6 options")
    @app_commands.describe(
        question="The question",
        option1="Option 1", option2="Option 2",
        option3="Option 3", option4="Option 4",
        option5="Option 5", option6="Option 6",
        anonymous="Anonymous voting?", deadline_hours="Close after X hours")
    async def poll(self, interaction: discord.Interaction,
                   question: str, option1: str, option2: str,
                   option3: str = None, option4: str = None,
                   option5: str = None, option6: str = None,
                   anonymous: bool = False, deadline_hours: int = None):
        await interaction.response.defer()
        options = [o for o in [option1, option2, option3, option4, option5, option6] if o]
        votes   = {str(i): [] for i in range(len(options))}
        deadline = (datetime.utcnow() + timedelta(hours=deadline_hours)) if deadline_hours else None

        async with get_db() as db:
            cur = await db.execute(
                "INSERT INTO polls (guild_id,creator_id,question,options,votes,anonymous,deadline)"
                " VALUES (?,?,?,?,?,?,?)",
                (interaction.guild_id, interaction.user.id, question,
                 json.dumps(options), json.dumps(votes), int(anonymous),
                 deadline.isoformat() if deadline else None))
            await db.commit()
            poll_id = cur.lastrowid

        def make_embed():
            total = sum(len(v) for v in votes.values())
            embed = discord.Embed(title=f"🗳️ {question}", color=GOLD)
            for i, opt in enumerate(options):
                count = len(votes[str(i)])
                pct   = (count / total * 100) if total > 0 else 0
                bar   = progress_bar(count, max(len(v) for v in votes.values()) or 1)
                embed.add_field(name=f"{opt}", value=f"{bar} {count} ({pct:.0f}%)", inline=False)
            embed.add_field(name="📊 Total Votes", value=str(total), inline=True)
            if anonymous:
                embed.add_field(name="🕵️ Mode", value="Anonymous", inline=True)
            if deadline:
                embed.add_field(name="⏰ Closes", value=f"<t:{int(deadline.timestamp())}:R>", inline=True)
            embed.set_footer(text=bonfire_footer("Poll") + f" · #{poll_id}")
            return embed

        view = discord.ui.View(timeout=deadline_hours * 3600 if deadline_hours else None)
        for i, opt in enumerate(options):
            async def vote_cb(inter: discord.Interaction, idx=i, label=opt):
                voter_id = inter.user.id
                for k, v in votes.items():
                    votes[k] = [x for x in v if x != voter_id]
                votes[str(idx)].append(voter_id)
                async with get_db() as db:
                    await db.execute("UPDATE polls SET votes=? WHERE id=?", (json.dumps(votes), poll_id))
                    await db.commit()
                resp = f"✅ Voted **{label}**" if not anonymous else "✅ Vote recorded."
                await inter.response.send_message(resp, ephemeral=True)
                try:
                    msg = await inter.original_response()
                    await msg.edit(embed=make_embed())
                except Exception:
                    pass
            btn = discord.ui.Button(label=f"{opt[:20]}", style=discord.ButtonStyle.primary)
            btn.callback = vote_cb
            view.add_item(btn)

        msg = await interaction.followup.send(embed=make_embed(), view=view)
        async with get_db() as db:
            await db.execute("UPDATE polls SET message_id=? WHERE id=?", (msg.id, poll_id))
            await db.commit()

        if deadline_hours:
            async def auto_close():
                await asyncio.sleep(deadline_hours * 3600)
                total = sum(len(v) for v in votes.values())
                winner_idx = max(range(len(options)), key=lambda i: len(votes[str(i)]))
                close_embed = discord.Embed(
                    title=f"🗳️ Poll Closed — {question}",
                    description=f"🏆 Winner: **{options[winner_idx]}** with {len(votes[str(winner_idx)])} votes",
                    color=GOLD)
                close_embed.set_footer(text=bonfire_footer("Poll"))
                try:
                    await msg.edit(embed=close_embed, view=None)
                except Exception:
                    pass
            asyncio.create_task(auto_close())

    @app_commands.command(name="pollresults", description="📊 See poll results by ID")
    @app_commands.describe(poll_id="Poll ID")
    async def poll_results(self, interaction: discord.Interaction, poll_id: int):
        async with get_db() as db:
            async with db.execute(
                "SELECT question, options, votes, anonymous, closed FROM polls WHERE id=? AND guild_id=?",
                (poll_id, interaction.guild_id)) as cur:
                row = await cur.fetchone()
        if not row:
            await interaction.response.send_message("Poll not found.", ephemeral=True); return
        question, options_str, votes_str, anonymous, closed = row
        options = json.loads(options_str)
        votes   = json.loads(votes_str)
        total   = sum(len(v) for v in votes.values())
        embed   = discord.Embed(
            title=f"📊 Poll Results — {question}",
            description="Final" if closed else "Live",
            color=GOLD)
        for i, opt in enumerate(options):
            count = len(votes.get(str(i), []))
            pct   = (count / total * 100) if total > 0 else 0
            bar   = progress_bar(count, max((len(votes.get(str(j), [])) for j in range(len(options))), default=1))
            voters = "" if anonymous else (", ".join(
                (interaction.guild.get_member(uid) or discord.Object(uid)).display_name
                for uid in votes.get(str(i), [])) or "none")
            embed.add_field(name=opt, value=f"{bar} {count} ({pct:.0f}%)" + (f"\n{voters}" if voters else ""), inline=False)
        embed.set_footer(text=bonfire_footer("Poll"))
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ─────────────────────────────────────────────────────────
# [PAIR CHAT]  — Feature 8
# ─────────────────────────────────────────────────────────

class PairChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_pair.start()

    def cog_unload(self):
        self.weekly_pair.cancel()

    @app_commands.command(name="pairchat", description="🎲 Join or trigger random weekly pairings")
    @app_commands.choices(action=[
        app_commands.Choice(name="Join pool", value="join"),
        app_commands.Choice(name="Leave pool", value="leave"),
        app_commands.Choice(name="Pair now",  value="pair"),
    ])
    async def pairchat(self, interaction: discord.Interaction, action: str = "join"):
        if action == "join":
            async with get_db() as db:
                await db.execute("INSERT OR IGNORE INTO pairchat_members (guild_id, user_id) VALUES (?,?)",
                                 (interaction.guild_id, interaction.user.id))
                await db.commit()
            await interaction.response.send_message("✅ You're in the pairchat pool!", ephemeral=True)
        elif action == "leave":
            async with get_db() as db:
                await db.execute("DELETE FROM pairchat_members WHERE guild_id=? AND user_id=?",
                                 (interaction.guild_id, interaction.user.id))
                await db.commit()
            await interaction.response.send_message("👋 Left the pairchat pool.", ephemeral=True)
        elif action == "pair":
            if not _is_core(interaction.user):
                await interaction.response.send_message("Core/OG only can trigger pairings.", ephemeral=True); return
            await interaction.response.defer()
            await self._do_pairing(interaction.guild)
            await interaction.followup.send("✅ Pairings posted!", ephemeral=True)

    async def _do_pairing(self, guild):
        async with get_db() as db:
            async with db.execute(
                "SELECT user_id FROM pairchat_members WHERE guild_id=?", (guild.id,)) as cur:
                pool = [r[0] for r in await cur.fetchall()]
        members = [guild.get_member(uid) for uid in pool if guild.get_member(uid)]
        if len(members) < 2:
            return
        random.shuffle(members)
        pairs = [(members[i], members[i+1]) for i in range(0, len(members)-1, 2)]

        ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
              discord.utils.get(guild.text_channels, name="general"))
        if not ch:
            return

        question = random.choice(ICEBREAKER_QUESTIONS)[1]
        for m1, m2 in pairs:
            embed = discord.Embed(
                title="🔥 Weekly Spark",
                description=f"{m1.mention} and {m2.mention} — go talk about something.\n\n**Start with:** *{question}*",
                color=PRIMARY)
            embed.set_footer(text=bonfire_footer("PairChat"))
            await ch.send(embed=embed)

            async with get_db() as db:
                await db.execute(
                    "INSERT INTO pairchat_history (guild_id, user1_id, user2_id) VALUES (?,?,?)",
                    (guild.id, m1.id, m2.id))
                await db.commit()

    @tasks.loop(hours=168)
    async def weekly_pair(self):
        for guild in self.bot.guilds:
            await self._do_pairing(guild)

    @weekly_pair.before_loop
    async def before_pair(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0 and now.hour >= 10:
            days_until_monday = 7
        target = (now + timedelta(days=days_until_monday)).replace(hour=10, minute=0, second=0, microsecond=0)
        await asyncio.sleep((target - now).total_seconds())


# ─────────────────────────────────────────────────────────
# [MEMORY BOARD]  — Feature 9
# ─────────────────────────────────────────────────────────

class MemoryBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.on_this_day.start()

    def cog_unload(self):
        self.on_this_day.cancel()

    @app_commands.command(name="memory", description="📸 Save and browse squad memories")
    @app_commands.describe(action="What to do", text="Memory text", image_url="Optional image URL")
    @app_commands.choices(action=[
        app_commands.Choice(name="Add memory",   value="add"),
        app_commands.Choice(name="Random",       value="random"),
        app_commands.Choice(name="On this day",  value="today"),
    ])
    async def memory(self, interaction: discord.Interaction,
                     action: str = "random", text: str = None, image_url: str = None):
        if action == "add":
            if not text:
                await interaction.response.send_message("Provide text for the memory.", ephemeral=True); return
            async with get_db() as db:
                await db.execute(
                    "INSERT INTO memories (guild_id, user_id, text, image_url) VALUES (?,?,?,?)",
                    (interaction.guild_id, interaction.user.id, text, image_url or ""))
                await db.commit()
            embed = discord.Embed(title="📸 Memory Saved", description=text, color=PRIMARY)
            if image_url:
                embed.set_image(url=image_url)
            embed.set_footer(text=bonfire_footer("Memory Board"))
            await interaction.response.send_message(embed=embed)

        elif action == "random":
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, text, image_url, created_at FROM memories WHERE guild_id=? ORDER BY RANDOM() LIMIT 1",
                    (interaction.guild_id,)) as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.response.send_message("No memories yet. Use `/memory add` to start!", ephemeral=True); return
            uid, text, img, created_at = row
            m = interaction.guild.get_member(uid)
            embed = discord.Embed(title="📸 A Memory", description=text, color=PRIMARY, timestamp=datetime.fromisoformat(str(created_at)))
            embed.set_author(name=m.display_name if m else "Unknown", icon_url=m.display_avatar.url if m else None)
            if img:
                embed.set_image(url=img)
            embed.set_footer(text=bonfire_footer("Memory Board"))
            await interaction.response.send_message(embed=embed)

        elif action == "today":
            today = datetime.utcnow()
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, text, image_url, created_at FROM memories"
                    " WHERE guild_id=? AND strftime('%m-%d', created_at) = ?"
                    " AND strftime('%Y', created_at) != ?",
                    (interaction.guild_id,
                     today.strftime("%m-%d"),
                     str(today.year))) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No memories from this day in past years.", ephemeral=True); return
            embed = discord.Embed(title=f"📅 On This Day — {today.strftime('%B %d')}", color=PRIMARY)
            for uid, text, img, created_at in rows[:5]:
                m = interaction.guild.get_member(uid)
                year = str(created_at)[:4]
                snip = (text[:80] + "…") if len(text) > 80 else text
                embed.add_field(name=f"{year} — {m.display_name if m else 'Unknown'}", value=snip, inline=False)
            embed.set_footer(text=bonfire_footer("Memory Board"))
            await interaction.response.send_message(embed=embed)

    @tasks.loop(hours=24)
    async def on_this_day(self):
        today = datetime.utcnow()
        for guild in self.bot.guilds:
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, text, image_url, created_at FROM memories"
                    " WHERE guild_id=? AND strftime('%m-%d', created_at) = ?"
                    " AND strftime('%Y', created_at) != ?",
                    (guild.id, today.strftime("%m-%d"), str(today.year))) as cur:
                    rows = await cur.fetchall()
            if not rows:
                continue
            ch = (discord.utils.get(guild.text_channels, name="📸・memories") or
                  discord.utils.get(guild.text_channels, name="🔥・general") or
                  discord.utils.get(guild.text_channels, name="general"))
            if not ch:
                continue
            embed = discord.Embed(
                title=f"📅 On This Day — {today.strftime('%B %d')}",
                color=PRIMARY)
            for uid, text, img, created_at in rows[:3]:
                m = guild.get_member(uid)
                year = str(created_at)[:4]
                snip = (text[:80] + "…") if len(text) > 80 else text
                embed.add_field(name=f"{year} — {m.display_name if m else 'Unknown'}", value=snip, inline=False)
            embed.set_footer(text=bonfire_footer("Memory Board"))
            await ch.send(embed=embed)

    @on_this_day.before_loop
    async def before_otd(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        target = now.replace(hour=9, minute=30, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())


# ─────────────────────────────────────────────────────────
# [CHECK-IN PING]  — Feature 10
# ─────────────────────────────────────────────────────────

class CheckIn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="checkin", description="🆘 Send a friendly check-in to a quiet member")
    @app_commands.describe(member="Who to check in on", anonymous="Keep your name anonymous?")
    async def checkin(self, interaction: discord.Interaction,
                      member: discord.Member, anonymous: bool = True):
        if member.bot:
            await interaction.response.send_message("Can't check in on the bot.", ephemeral=True); return
        if member.id == interaction.user.id:
            await interaction.response.send_message("You can't check in on yourself.", ephemeral=True); return

        async with get_db() as db:
            await db.execute(
                "INSERT INTO checkin_log (guild_id, target_id, sender_id, anonymous) VALUES (?,?,?,?)",
                (interaction.guild_id, member.id, interaction.user.id, int(anonymous)))
            await db.commit()

        sender_name = "someone" if anonymous else interaction.user.display_name
        guild_name  = interaction.guild.name
        try:
            embed = discord.Embed(
                title=f"🔥 The bonfire misses you",
                description=(
                    f"Hey **{member.display_name}** — {sender_name} noticed you've been quiet in **{guild_name}**.\n\n"
                    f"Everything good? The fire's still lit. Come back when you're ready. 🔥"
                ),
                color=PRIMARY)
            embed.set_footer(text="No pressure. Just wanted to say hey.")
            await member.send(embed=embed)
            await interaction.response.send_message(
                f"✅ Check-in sent to {member.display_name}." +
                (" They won't know it was you." if anonymous else ""), ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"⚠️ Couldn't DM {member.display_name} (DMs closed).", ephemeral=True)


# ─────────────────────────────────────────────────────────
# [VOICE SESSION LOG]  — Feature 11
# ─────────────────────────────────────────────────────────

class VoiceLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sessions", description="🎙️ View VC session leaderboard")
    async def sessions(self, interaction: discord.Interaction):
        async with get_db() as db:
            async with db.execute(
                "SELECT members, duration_minutes, vibe_emoji FROM vc_sessions WHERE guild_id=?"
                " ORDER BY duration_minutes DESC LIMIT 10",
                (interaction.guild_id,)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message("No VC sessions logged yet.", ephemeral=True); return
        embed = discord.Embed(title="🎙️ VC Session Leaderboard", color=TEAL)
        for members_str, duration, vibe in rows:
            members_ids = json.loads(members_str or "[]")
            names = [interaction.guild.get_member(uid).display_name if interaction.guild.get_member(uid) else str(uid)
                     for uid in members_ids[:4]]
            names_str = ", ".join(names) + (f" +{len(members_ids)-4}" if len(members_ids) > 4 else "")
            vibe_str = f" · {vibe}" if vibe else ""
            embed.add_field(name=f"⏱️ {duration} min{vibe_str}", value=names_str or "Unknown", inline=False)
        embed.set_footer(text=bonfire_footer("Voice Log"))
        await interaction.response.send_message(embed=embed)

    async def session_ended(self, guild, channel, members, started_at):
        ended_at = datetime.utcnow()
        duration = int((ended_at - started_at).total_seconds() / 60)
        if duration < 2:
            return

        member_ids = [m.id for m in members]
        ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
              discord.utils.get(guild.text_channels, name="general"))
        if not ch:
            return

        embed = discord.Embed(
            title=f"🎙️ VC Session Ended — {channel.name}",
            color=TEAL)
        embed.add_field(name="👥 Who was in it",
                        value=", ".join(m.display_name for m in members) or "Unknown", inline=False)
        embed.add_field(name="⏱️ Duration",  value=f"{duration} minutes", inline=True)
        embed.add_field(name="🕐 Started",   value=f"<t:{int(started_at.timestamp())}:t>", inline=True)
        embed.add_field(name="🕐 Ended",     value=f"<t:{int(ended_at.timestamp())}:t>", inline=True)
        embed.set_footer(text=bonfire_footer("Voice Log"))

        vibe_counts = {"🔥": 0, "😴": 0, "💀": 0, "🎮": 0}
        view = discord.ui.View(timeout=3600)
        session_id_holder = {}

        for emoji, label in [("🔥", "banger"), ("😴", "chill"), ("💀", "unhinged"), ("🎮", "gaming")]:
            async def cb(inter: discord.Interaction, e=emoji):
                vibe_counts[e] += 1
                dominant = max(vibe_counts, key=vibe_counts.get)
                if sum(vibe_counts.values()) >= 3:
                    async with get_db() as db:
                        if "id" in session_id_holder:
                            await db.execute("UPDATE vc_sessions SET vibe_emoji=? WHERE id=?",
                                             (dominant, session_id_holder["id"]))
                            await db.commit()
                await inter.response.send_message(f"{e} noted!", ephemeral=True)
            btn = discord.ui.Button(label=f"{emoji} {label}", style=discord.ButtonStyle.secondary)
            btn.callback = cb
            view.add_item(btn)

        msg = await ch.send(embed=embed, view=view)
        async with get_db() as db:
            cur = await db.execute(
                "INSERT INTO vc_sessions (guild_id,channel_id,members,started_at,ended_at,duration_minutes,message_id)"
                " VALUES (?,?,?,?,?,?,?)",
                (guild.id, channel.id, json.dumps(member_ids), started_at, ended_at, duration, msg.id))
            await db.commit()
            session_id_holder["id"] = cur.lastrowid
        await log_timeline(guild.id, "🎙️", f"VC session in {channel.name}: {duration} min", member_ids)


# ─────────────────────────────────────────────────────────
# [DRAMA TRACKER]  — Feature 12
# ─────────────────────────────────────────────────────────

class Drama(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="drama", description="🎭 Log and browse drama history")
    @app_commands.describe(action="What to do", user1="Person 1", user2="Person 2", description="What happened?")
    @app_commands.choices(action=[
        app_commands.Choice(name="Log drama",        value="log"),
        app_commands.Choice(name="Full history",     value="history"),
        app_commands.Choice(name="Between two people", value="between"),
        app_commands.Choice(name="Stats leaderboard", value="stats"),
    ])
    async def drama(self, interaction: discord.Interaction,
                    action: str, user1: discord.Member = None,
                    user2: discord.Member = None, description: str = None):
        if action == "log":
            if not _is_core(interaction.user):
                await interaction.response.send_message("Core/OG only can log drama.", ephemeral=True); return
            if not user1 or not user2 or not description:
                await interaction.response.send_message("Provide both members and a description.", ephemeral=True); return
            async with get_db() as db:
                await db.execute(
                    "INSERT INTO drama (guild_id, logger_id, user1_id, user2_id, description) VALUES (?,?,?,?,?)",
                    (interaction.guild_id, interaction.user.id, user1.id, user2.id, description))
                await db.commit()
            embed = discord.Embed(title="🎭 Drama Logged", color=ORANGE)
            embed.add_field(name="👥 Involved",    value=f"{user1.mention} & {user2.mention}", inline=True)
            embed.add_field(name="📝 What Happened", value=description, inline=False)
            embed.set_footer(text=bonfire_footer("Drama"))
            await interaction.response.send_message(embed=embed)
            await log_timeline(interaction.guild_id, "🎭", f"Drama: {description[:60]}", [user1.id, user2.id])

        elif action == "history":
            async with get_db() as db:
                async with db.execute(
                    "SELECT user1_id, user2_id, description, created_at FROM drama WHERE guild_id=?"
                    " ORDER BY created_at DESC LIMIT 10", (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No drama on record. Either everyone's chill or nobody's using this.", ephemeral=True); return
            embed = discord.Embed(title="🎭 Drama Timeline", color=ORANGE)
            for u1, u2, desc, created_at in rows:
                m1 = interaction.guild.get_member(u1)
                m2 = interaction.guild.get_member(u2)
                snip = (desc[:60] + "…") if len(desc) > 60 else desc
                embed.add_field(
                    name=f"📅 {str(created_at)[:10]} — {m1.display_name if m1 else u1} & {m2.display_name if m2 else u2}",
                    value=snip, inline=False)
            embed.set_footer(text=bonfire_footer("Drama"))
            await interaction.response.send_message(embed=embed)

        elif action == "between":
            if not user1 or not user2:
                await interaction.response.send_message("Specify both members.", ephemeral=True); return
            async with get_db() as db:
                async with db.execute(
                    "SELECT description, created_at FROM drama WHERE guild_id=?"
                    " AND ((user1_id=? AND user2_id=?) OR (user1_id=? AND user2_id=?))"
                    " ORDER BY created_at ASC",
                    (interaction.guild_id, user1.id, user2.id, user2.id, user1.id)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No drama between these two. Innocent... for now.", ephemeral=True); return
            embed = discord.Embed(
                title=f"🎭 Drama: {user1.display_name} & {user2.display_name}",
                description=f"{len(rows)} logged incident(s)",
                color=ORANGE)
            for desc, created_at in rows:
                embed.add_field(name=str(created_at)[:10], value=desc, inline=False)
            embed.set_footer(text=bonfire_footer("Drama"))
            await interaction.response.send_message(embed=embed)

        elif action == "stats":
            async with get_db() as db:
                async with db.execute(
                    "SELECT user1_id FROM drama WHERE guild_id=?"
                    " UNION ALL SELECT user2_id FROM drama WHERE guild_id=?",
                    (interaction.guild_id, interaction.guild_id)) as cur:
                    all_ids = [r[0] for r in await cur.fetchall()]
            if not all_ids:
                await interaction.response.send_message("No drama yet.", ephemeral=True); return
            counts = defaultdict(int)
            for uid in all_ids:
                counts[uid] += 1
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            embed = discord.Embed(title="🎭 Drama Stats", color=ORANGE)
            for i, (uid, cnt) in enumerate(sorted_counts[:10], 1):
                m = interaction.guild.get_member(uid)
                embed.add_field(name=f"#{i} {m.display_name if m else uid}", value=f"{cnt} incidents", inline=True)
            embed.set_footer(text=bonfire_footer("Drama"))
            await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [PERSONAL STATS CARD]  — Feature 13
# ─────────────────────────────────────────────────────────

class StatsCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="me", description="📊 View your personal stats card")
    async def me(self, interaction: discord.Interaction):
        await self._show_stats(interaction, interaction.user)

    @app_commands.command(name="stats", description="📊 View someone's stats card")
    @app_commands.describe(member="Who to view")
    async def stats(self, interaction: discord.Interaction, member: discord.Member):
        await self._show_stats(interaction, member)

    async def _show_stats(self, interaction: discord.Interaction, target: discord.Member):
        await interaction.response.defer(ephemeral=(target == interaction.user))
        gid = interaction.guild_id
        uid = target.id
        month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()

        async with get_db() as db:
            async with db.execute(
                "SELECT COUNT(*) FROM activity_log WHERE guild_id=? AND user_id=? AND activity_type='message'",
                (gid, uid)) as cur:
                total_messages = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM activity_log WHERE guild_id=? AND user_id=? AND activity_type='message' AND created_at>=?",
                (gid, uid, month_ago)) as cur:
                month_messages = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM highlights WHERE guild_id=? AND author_id=?", (gid, uid)) as cur:
                highlights = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM quotes WHERE guild_id=? AND author_id=?", (gid, uid)) as cur:
                quotes_count = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM beef WHERE guild_id=? AND initiator_id=?", (gid, uid)) as cur:
                beefs_started = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM beef WHERE guild_id=? AND (initiator_id=? OR target_id=?) AND resolved=1",
                (gid, uid, uid)) as cur:
                beefs_resolved = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM lore WHERE guild_id=? AND author_id=?", (gid, uid)) as cur:
                lore_count = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM achievements WHERE guild_id=? AND user_id=?", (gid, uid)) as cur:
                achievement_count = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT AVG(score) FROM vibe_checks WHERE guild_id=? AND user_id=?", (gid, uid)) as cur:
                vibe_avg = (await cur.fetchone())[0] or 0
            async with db.execute(
                "SELECT name FROM alter_egos WHERE guild_id=? AND user_id=?", (gid, uid)) as cur:
                ego_row = await cur.fetchone()
            async with db.execute(
                "SELECT COUNT(*) FROM vc_sessions WHERE guild_id=? AND members LIKE ?",
                (gid, f'%{uid}%')) as cur:
                vc_sessions = (await cur.fetchone())[0]

        # Determine auto-title
        stat_maxes = {
            "messages": total_messages,
            "lore":     lore_count,
            "highlights": highlights,
            "quotes":   quotes_count,
            "beef":     beefs_started,
            "vc":       vc_sessions,
        }
        top_stat = max(stat_maxes, key=stat_maxes.get) if any(stat_maxes.values()) else "default"
        title_label = STAT_TITLES.get(top_stat, STAT_TITLES["default"])

        embed = discord.Embed(
            title=f"📊 {target.display_name}",
            description=f'*"{title_label}"*',
            color=PRIMARY)
        embed.set_thumbnail(url=target.display_avatar.url)

        embed.add_field(name="💬 Messages (all time)", value=f"{progress_bar(total_messages, max(total_messages, 1000))} {total_messages}", inline=True)
        embed.add_field(name="💬 Messages (this month)", value=f"{progress_bar(month_messages, max(month_messages, 200))} {month_messages}", inline=True)
        embed.add_field(name="⭐ Highlights", value=f"{progress_bar(highlights, max(highlights, 20))} {highlights}", inline=True)
        embed.add_field(name="💬 Quotes",     value=f"{progress_bar(quotes_count, max(quotes_count, 20))} {quotes_count}", inline=True)
        embed.add_field(name="🥩 Beefs Started",  value=str(beefs_started), inline=True)
        embed.add_field(name="🤝 Beefs Resolved", value=str(beefs_resolved), inline=True)
        embed.add_field(name="📖 Lore Entries",  value=str(lore_count), inline=True)
        embed.add_field(name="🏆 Achievements",  value=f"{achievement_count}/{len(BADGE_DEFS)}", inline=True)
        embed.add_field(name="📈 Vibe Avg",      value=f"{'█'*round(vibe_avg)}{'░'*(5-round(vibe_avg))} {vibe_avg:.1f}/5" if vibe_avg else "No data", inline=True)
        embed.add_field(name="🎙️ VC Sessions",   value=str(vc_sessions), inline=True)
        if ego_row:
            embed.add_field(name="🎭 Alter Ego", value=ego_row[0], inline=True)
        if target.joined_at:
            days_in = (datetime.utcnow() - target.joined_at.replace(tzinfo=None)).days
            embed.add_field(name="📅 Days in Server", value=str(days_in), inline=True)

        embed.set_footer(text=bonfire_footer("Stats Card"))
        await interaction.followup.send(embed=embed)


# ─────────────────────────────────────────────────────────
# [BONFIRE BETS]  — Feature 14
# ─────────────────────────────────────────────────────────

class BonfireBets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bet", description="🎰 Create or manage squad bets")
    @app_commands.describe(action="What to do", question="The bet question",
                           option1="Option 1", option2="Option 2",
                           deadline_hours="Hours until deadline",
                           bet_id="Bet ID (for close/leaderboard)")
    @app_commands.choices(action=[
        app_commands.Choice(name="Create bet",     value="create"),
        app_commands.Choice(name="Close bet",      value="close"),
        app_commands.Choice(name="Leaderboard",    value="leaderboard"),
    ])
    async def bet(self, interaction: discord.Interaction,
                  action: str, question: str = None,
                  option1: str = None, option2: str = None,
                  deadline_hours: int = 24,
                  bet_id: int = None):
        if action == "create":
            if not question or not option1 or not option2:
                await interaction.response.send_message("Provide question and both options.", ephemeral=True); return
            deadline = datetime.utcnow() + timedelta(hours=deadline_hours)
            async with get_db() as db:
                cur = await db.execute(
                    "INSERT INTO bets (guild_id,creator_id,question,option1,option2,deadline)"
                    " VALUES (?,?,?,?,?,?)",
                    (interaction.guild_id, interaction.user.id, question, option1, option2, deadline))
                await db.commit()
                b_id = cur.lastrowid

            votes1 = []; votes2 = []
            def make_bet_embed():
                embed = discord.Embed(title=f"🎰 Bet #{b_id} — {question}", color=GOLD)
                bar1 = progress_bar(len(votes1), max(len(votes1)+len(votes2), 1))
                bar2 = progress_bar(len(votes2), max(len(votes1)+len(votes2), 1))
                embed.add_field(name=f"1️⃣ {option1}", value=f"{bar1} {len(votes1)}", inline=True)
                embed.add_field(name=f"2️⃣ {option2}", value=f"{bar2} {len(votes2)}", inline=True)
                embed.add_field(name="⏰ Deadline", value=f"<t:{int(deadline.timestamp())}:R>", inline=False)
                embed.set_footer(text=bonfire_footer("Bets"))
                return embed

            view = discord.ui.View(timeout=deadline_hours * 3600)
            async def v1_cb(inter: discord.Interaction):
                votes2[:] = [x for x in votes2 if x != inter.user.id]
                if inter.user.id not in votes1: votes1.append(inter.user.id)
                async with get_db() as db:
                    await db.execute("UPDATE bets SET votes1=? WHERE id=?", (json.dumps(votes1), b_id))
                    await db.commit()
                await inter.response.send_message(f"✅ Voted **{option1}**", ephemeral=True)
            async def v2_cb(inter: discord.Interaction):
                votes1[:] = [x for x in votes1 if x != inter.user.id]
                if inter.user.id not in votes2: votes2.append(inter.user.id)
                async with get_db() as db:
                    await db.execute("UPDATE bets SET votes2=? WHERE id=?", (json.dumps(votes2), b_id))
                    await db.commit()
                await inter.response.send_message(f"✅ Voted **{option2}**", ephemeral=True)

            b1 = discord.ui.Button(label=f"1️⃣ {option1[:20]}", style=discord.ButtonStyle.primary)
            b2 = discord.ui.Button(label=f"2️⃣ {option2[:20]}", style=discord.ButtonStyle.secondary)
            b1.callback = v1_cb; b2.callback = v2_cb
            view.add_item(b1); view.add_item(b2)

            await interaction.response.send_message(embed=make_bet_embed(), view=view)
            await log_timeline(interaction.guild_id, "🎰", f"Bet: {question}", [interaction.user.id])

        elif action == "close":
            if not _is_core(interaction.user):
                await interaction.response.send_message("Core/OG only can close bets.", ephemeral=True); return
            if not bet_id or not option1:
                await interaction.response.send_message("Provide bet_id and option1 as the winning option name.", ephemeral=True); return
            async with get_db() as db:
                async with db.execute(
                    "SELECT question, option1, option2, votes1, votes2 FROM bets WHERE id=? AND guild_id=?",
                    (bet_id, interaction.guild_id)) as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.response.send_message("Bet not found.", ephemeral=True); return
            q, opt1, opt2, v1_str, v2_str = row
            winner_num = 1 if option1.lower() == opt1.lower() else 2
            async with get_db() as db:
                await db.execute("UPDATE bets SET closed=1, winner=? WHERE id=?", (winner_num, bet_id))
                await db.commit()
            winners = json.loads(v1_str if winner_num == 1 else v2_str)
            embed = discord.Embed(
                title=f"🎰 Bet #{bet_id} Closed — {q}",
                description=f"🏆 **{opt1 if winner_num == 1 else opt2}** wins!",
                color=GOLD)
            if winners:
                winner_names = [interaction.guild.get_member(uid).display_name if interaction.guild.get_member(uid) else str(uid)
                                for uid in winners]
                embed.add_field(name="🎉 Correct pickers", value=", ".join(winner_names), inline=False)
            embed.set_footer(text=bonfire_footer("Bets"))
            await interaction.response.send_message(embed=embed)
            for uid in winners:
                async with get_db() as db:
                    async with db.execute(
                        "SELECT COUNT(*) FROM bets WHERE guild_id=? AND winner=1 AND closed=1"
                        " AND votes1 LIKE ?", (interaction.guild_id, f'%{uid}%')) as cur:
                        won1 = (await cur.fetchone())[0]
                    async with db.execute(
                        "SELECT COUNT(*) FROM bets WHERE guild_id=? AND winner=2 AND closed=1"
                        " AND votes2 LIKE ?", (interaction.guild_id, f'%{uid}%')) as cur:
                        won2 = (await cur.fetchone())[0]
                if won1 + won2 >= 5:
                    await check_achievement(self.bot, interaction.guild_id, uid, "prophet")

        elif action == "leaderboard":
            async with get_db() as db:
                async with db.execute(
                    "SELECT votes1, votes2, winner FROM bets WHERE guild_id=? AND closed=1",
                    (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No closed bets yet.", ephemeral=True); return
            user_stats = defaultdict(lambda: [0, 0])  # [correct, total]
            for v1_str, v2_str, winner in rows:
                v1 = json.loads(v1_str); v2 = json.loads(v2_str)
                all_voters = [(uid, 1) for uid in v1] + [(uid, 2) for uid in v2]
                for uid, choice in all_voters:
                    user_stats[uid][1] += 1
                    if choice == winner:
                        user_stats[uid][0] += 1
            sorted_stats = sorted(user_stats.items(), key=lambda x: (x[1][0] / max(x[1][1], 1)), reverse=True)
            embed = discord.Embed(title="🎰 Bet Leaderboard", color=GOLD)
            for i, (uid, (correct, total)) in enumerate(sorted_stats[:10], 1):
                m = interaction.guild.get_member(uid)
                pct = correct / total * 100 if total > 0 else 0
                embed.add_field(name=f"#{i} {m.display_name if m else uid}",
                                value=f"{correct}/{total} correct ({pct:.0f}%)", inline=True)
            embed.set_footer(text=bonfire_footer("Bets"))
            await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [SERVER TEMPERATURE]  — Feature 15
# ─────────────────────────────────────────────────────────

class ServerTemp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_temp.start()

    def cog_unload(self):
        self.daily_temp.cancel()

    async def _calculate_temp(self, guild):
        day_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        async with get_db() as db:
            async with db.execute(
                "SELECT COUNT(*) FROM activity_log WHERE guild_id=? AND created_at>=? AND activity_type='message'",
                (guild.id, day_ago)) as cur:
                messages = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM vc_sessions WHERE guild_id=? AND created_at>=?",
                (guild.id, day_ago)) as cur:
                vc_sessions = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM quotes WHERE guild_id=? AND created_at>=?",
                (guild.id, day_ago)) as cur:
                new_quotes = (await cur.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM lore WHERE guild_id=? AND created_at>=?",
                (guild.id, day_ago)) as cur:
                new_lore = (await cur.fetchone())[0]

        score = min(100, (messages * 2) + (vc_sessions * 10) + (new_quotes * 5) + (new_lore * 5))
        if score <= 20:   label, color = "❄️ Dead server energy",        discord.Color.blue()
        elif score <= 40: label, color = "😴 Quiet bonfire",             discord.Color.greyple()
        elif score <= 60: label, color = "🌤️ Warming up",               discord.Color.gold()
        elif score <= 80: label, color = "🔥 Things are heating up",     discord.Color.orange()
        else:             label, color = "💥 ABSOLUTE CHAOS MODE",       discord.Color.red()
        return score, label, color

    @tasks.loop(hours=24)
    async def daily_temp(self):
        for guild in self.bot.guilds:
            score, label, color = await self._calculate_temp(guild)
            ch = (discord.utils.get(guild.text_channels, name="📊・status") or
                  discord.utils.get(guild.text_channels, name="status"))
            if not ch:
                continue
            bar = progress_bar(score, 100)
            embed = discord.Embed(
                title="🌡️ Server Temperature",
                description=f"**{label}**\n{bar} {score}/100",
                color=color)
            embed.set_footer(text=bonfire_footer("Server Temp"))
            await ch.send(embed=embed)
            async with get_db() as db:
                await db.execute(
                    "INSERT INTO server_temp (guild_id, score, label) VALUES (?,?,?)",
                    (guild.id, score, label))
                await db.commit()

    @daily_temp.before_loop
    async def before_temp(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        target = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

    @app_commands.command(name="temperature", description="🌡️ Check server temperature")
    @app_commands.choices(view=[
        app_commands.Choice(name="Current", value="now"),
        app_commands.Choice(name="This week", value="week"),
    ])
    async def temperature(self, interaction: discord.Interaction, view: str = "now"):
        await interaction.response.defer()
        if view == "now":
            score, label, color = await self._calculate_temp(interaction.guild)
            bar = progress_bar(score, 100)
            embed = discord.Embed(title="🌡️ Server Temperature", description=f"**{label}**\n{bar} {score}/100", color=color)
            embed.set_footer(text=bonfire_footer("Server Temp"))
            await interaction.followup.send(embed=embed)
        else:
            async with get_db() as db:
                async with db.execute(
                    "SELECT score, label, recorded_at FROM server_temp WHERE guild_id=?"
                    " ORDER BY recorded_at DESC LIMIT 7", (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.followup.send("No temperature history yet.", ephemeral=True); return
            embed = discord.Embed(title="🌡️ Temperature — This Week", color=PRIMARY)
            for score, label, rec_at in reversed(rows):
                bar = progress_bar(score, 100)
                embed.add_field(name=str(rec_at)[:10], value=f"{bar} {score} — {label}", inline=False)
            embed.set_footer(text=bonfire_footer("Server Temp"))
            await interaction.followup.send(embed=embed)


# ─────────────────────────────────────────────────────────
# [ANONYMOUS CONFESSIONS]  — Feature 16
# ─────────────────────────────────────────────────────────

class Confessions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="confess", description="💌 Submit an anonymous confession")
    async def confess(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfessionModal(self.bot))

    @app_commands.command(name="confessdelete", description="💌 Delete a confession — Core/OG only")
    @app_commands.describe(confession_id="ID of the confession")
    async def confess_delete(self, interaction: discord.Interaction, confession_id: int):
        if not _is_core(interaction.user):
            await interaction.response.send_message("Core/OG only.", ephemeral=True); return
        async with get_db() as db:
            async with db.execute(
                "SELECT message_id FROM confessions WHERE id=? AND guild_id=?",
                (confession_id, interaction.guild_id)) as cur:
                row = await cur.fetchone()
            if not row:
                await interaction.response.send_message("Confession not found.", ephemeral=True); return
            await db.execute("DELETE FROM confessions WHERE id=?", (confession_id,))
            await db.commit()
        ch = (discord.utils.get(interaction.guild.text_channels, name="💌・confessions") or
              discord.utils.get(interaction.guild.text_channels, name="confessions"))
        if ch and row[0]:
            try:
                msg = await ch.fetch_message(row[0])
                await msg.delete()
            except Exception:
                pass
        await interaction.response.send_message("✅ Confession deleted.", ephemeral=True)


class ConfessionModal(discord.ui.Modal, title="💌 Anonymous Confession"):
    confession = discord.ui.TextInput(
        label="Your confession (anonymous)",
        style=discord.TextStyle.paragraph,
        max_length=500,
        placeholder="Speak your truth. Nobody will know it was you.")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        user_hash = hashlib.sha256(
            f"{interaction.user.id}{guild.id}{datetime.utcnow().strftime('%Y%m')}".encode()
        ).hexdigest()[:8]

        ch = (discord.utils.get(guild.text_channels, name="💌・confessions") or
              discord.utils.get(guild.text_channels, name="confessions") or
              discord.utils.get(guild.text_channels, name="🔥・general"))
        if not ch:
            await interaction.followup.send("No confessions channel found.", ephemeral=True); return

        placeholders = ["👤", "🎭", "🕵️", "👻", "🫥", "🔮"]
        placeholder = random.choice(placeholders)

        async with get_db() as db:
            cur = await db.execute(
                "INSERT INTO confessions (guild_id, user_hash, content) VALUES (?,?,?)",
                (guild.id, user_hash, self.confession.value))
            await db.commit()
            conf_id = cur.lastrowid

        embed = discord.Embed(
            title=f"{placeholder} Anonymous Confession #{conf_id}",
            description=self.confession.value,
            color=DARK_GREY)
        embed.set_footer(text=bonfire_footer("Confessions"))

        view = discord.ui.View(timeout=None)
        for emoji in ["💀", "😭", "🔥", "👀"]:
            async def cb(inter: discord.Interaction, e=emoji):
                await inter.response.send_message(f"{e}", ephemeral=True)
            btn = discord.ui.Button(label=emoji, style=discord.ButtonStyle.secondary)
            btn.callback = cb
            view.add_item(btn)

        msg = await ch.send(embed=embed, view=view)
        async with get_db() as db:
            await db.execute("UPDATE confessions SET message_id=? WHERE id=?", (msg.id, conf_id))
            await db.commit()

        await interaction.followup.send("✅ Confession posted anonymously.", ephemeral=True)


# ─────────────────────────────────────────────────────────
# [AVAILABILITY BOARD]  — Feature 17
# ─────────────────────────────────────────────────────────

class Availability(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avail", description="📅 Set or check availability")
    @app_commands.describe(action="What to do", schedule="Your availability (for set)")
    @app_commands.choices(action=[
        app_commands.Choice(name="Set my availability", value="set"),
        app_commands.Choice(name="Check everyone",      value="check"),
        app_commands.Choice(name="Squad overlap",       value="squad"),
    ])
    async def avail(self, interaction: discord.Interaction, action: str, schedule: str = None):
        if action == "set":
            if not schedule:
                await interaction.response.send_message("Provide your schedule.", ephemeral=True); return
            async with get_db() as db:
                await db.execute(
                    "INSERT OR REPLACE INTO availability (guild_id, user_id, schedule, updated_at) VALUES (?,?,?,?)",
                    (interaction.guild_id, interaction.user.id, schedule, datetime.utcnow()))
                await db.commit()
            embed = discord.Embed(title="📅 Availability Set", description=f"**{schedule}**", color=TEAL)
            embed.set_footer(text=bonfire_footer("Availability"))
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif action == "check":
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, schedule FROM availability WHERE guild_id=?",
                    (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("Nobody has set their availability yet.", ephemeral=True); return
            embed = discord.Embed(title="📅 Squad Availability", color=TEAL)
            for uid, schedule in rows:
                m = interaction.guild.get_member(uid)
                embed.add_field(name=m.display_name if m else str(uid), value=schedule, inline=False)
            embed.set_footer(text=bonfire_footer("Availability"))
            await interaction.response.send_message(embed=embed)

        elif action == "squad":
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, schedule FROM availability WHERE guild_id=?",
                    (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if len(rows) < 2:
                await interaction.response.send_message("Not enough people have set availability yet.", ephemeral=True); return
            embed = discord.Embed(
                title="📅 Squad Availability Overlap",
                description="Based on everyone's schedules:",
                color=TEAL)
            for uid, schedule in rows:
                m = interaction.guild.get_member(uid)
                embed.add_field(name=m.display_name if m else str(uid), value=schedule, inline=True)
            embed.add_field(name="💡 Tip", value="Look for days/times that appear most often above!", inline=False)
            embed.set_footer(text=bonfire_footer("Availability"))
            await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [HOT SEAT]  — Feature 18
# ─────────────────────────────────────────────────────────

class HotSeat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hotseat", description="🎤 Put someone in the hot seat")
    @app_commands.describe(action="What to do", member="Who to put in the hot seat")
    @app_commands.choices(action=[
        app_commands.Choice(name="Start",  value="start"),
        app_commands.Choice(name="Replay", value="replay"),
    ])
    async def hotseat(self, interaction: discord.Interaction, action: str, member: discord.Member = None):
        if action == "start":
            if not member:
                await interaction.response.send_message("Specify who's going in.", ephemeral=True); return

            async with get_db() as db:
                cur = await db.execute(
                    "INSERT INTO hotseat (guild_id, target_id, starter_id) VALUES (?,?,?)",
                    (interaction.guild_id, member.id, interaction.user.id))
                await db.commit()
                hs_id = cur.lastrowid

            questions = []
            embed = discord.Embed(
                title=f"🎤 {member.display_name} is in the HOT SEAT",
                description=f"You have 10 minutes. Ask them anything. Click to submit questions.",
                color=discord.Color.red())
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=bonfire_footer("Hot Seat"))

            view = discord.ui.View(timeout=600)
            async def ask_cb(inter: discord.Interaction):
                await inter.response.send_modal(HotSeatQuestionModal(self.bot, hs_id, questions, member))
            ask_btn = discord.ui.Button(label="❓ Ask a question", style=discord.ButtonStyle.danger)
            ask_btn.callback = ask_cb
            view.add_item(ask_btn)

            await interaction.response.send_message(embed=embed, view=view)

            async def end_hotseat():
                await asyncio.sleep(600)
                async with get_db() as db:
                    await db.execute("UPDATE hotseat SET active=0, ended_at=? WHERE id=?",
                                     (datetime.utcnow(), hs_id))
                    await db.commit()
                end_embed = discord.Embed(
                    title=f"🎤 Hot Seat Report — {member.display_name}",
                    description=f"Time's up! {len(questions)} question(s) were asked.",
                    color=discord.Color.red())
                if questions:
                    for q in questions[:10]:
                        end_embed.add_field(name="❓ Question", value=q, inline=False)
                end_embed.set_footer(text=bonfire_footer("Hot Seat"))
                await interaction.channel.send(embed=end_embed)

            asyncio.create_task(end_hotseat())
            await log_timeline(interaction.guild_id, "🎤", f"{member.display_name} went in the hot seat", [member.id, interaction.user.id])

        elif action == "replay":
            if not member:
                await interaction.response.send_message("Specify the member.", ephemeral=True); return
            async with get_db() as db:
                async with db.execute(
                    "SELECT questions, started_at FROM hotseat WHERE guild_id=? AND target_id=? AND active=0"
                    " ORDER BY started_at DESC LIMIT 1",
                    (interaction.guild_id, member.id)) as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.response.send_message(f"No hot seat history for {member.display_name}.", ephemeral=True); return
            questions_str, started_at = row
            questions = json.loads(questions_str)
            embed = discord.Embed(
                title=f"🎤 Hot Seat Replay — {member.display_name}",
                description=f"From {str(started_at)[:10]}",
                color=discord.Color.red())
            for q in questions[:10]:
                embed.add_field(name="❓", value=q, inline=False)
            embed.set_footer(text=bonfire_footer("Hot Seat"))
            await interaction.response.send_message(embed=embed)


class HotSeatQuestionModal(discord.ui.Modal, title="❓ Ask a question"):
    question = discord.ui.TextInput(label="Your question", max_length=200)

    def __init__(self, bot, hs_id, questions, target):
        super().__init__()
        self.bot       = bot
        self.hs_id     = hs_id
        self.questions = questions
        self.target    = target

    async def on_submit(self, interaction: discord.Interaction):
        self.questions.append(self.question.value)
        async with get_db() as db:
            await db.execute("UPDATE hotseat SET questions=? WHERE id=?",
                             (json.dumps(self.questions), self.hs_id))
            await db.commit()
        q_embed = discord.Embed(
            title=f"❓ Question for {self.target.display_name}",
            description=self.question.value,
            color=discord.Color.red())
        q_embed.set_footer(text=bonfire_footer("Hot Seat"))
        await interaction.response.send_message(embed=q_embed)


# ─────────────────────────────────────────────────────────
# [TIMELINE]  — Feature 20
# ─────────────────────────────────────────────────────────

class Timeline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ITEMS_PER_PAGE = 5

    @app_commands.command(name="timeline", description="🗺️ Browse the server's living history")
    @app_commands.describe(member="Filter by member", month="Month number (1-12)", year="Year")
    async def timeline(self, interaction: discord.Interaction,
                       member: discord.Member = None, month: int = None, year: int = None):
        await interaction.response.defer()
        conditions = ["guild_id=?"]
        params     = [interaction.guild_id]
        if member:
            conditions.append("members LIKE ?")
            params.append(f'%{member.id}%')
        if month and year:
            conditions.append("strftime('%m', created_at) = ? AND strftime('%Y', created_at) = ?")
            params.extend([f"{month:02d}", str(year)])
        elif year:
            conditions.append("strftime('%Y', created_at) = ?")
            params.append(str(year))

        where = " AND ".join(conditions)
        async with get_db() as db:
            async with db.execute(
                f"SELECT category, description, members, created_at FROM timeline_events"
                f" WHERE {where} ORDER BY created_at DESC",
                params) as cur:
                rows = await cur.fetchall()

        if not rows:
            await interaction.followup.send("No timeline events found.", ephemeral=True); return

        pages = [rows[i:i+self.ITEMS_PER_PAGE] for i in range(0, len(rows), self.ITEMS_PER_PAGE)]
        current = [0]

        def make_page(idx):
            embed = discord.Embed(
                title=f"🗺️ Server Timeline{f' — {member.display_name}' if member else ''}",
                color=PRIMARY)
            for category, description, members_str, created_at in pages[idx]:
                embed.add_field(
                    name=f"{category} {str(created_at)[:10]}",
                    value=description, inline=False)
            embed.set_footer(text=bonfire_footer("Timeline") + f" · Page {idx+1}/{len(pages)}")
            return embed

        view = discord.ui.View(timeout=120)
        async def prev_cb(inter: discord.Interaction):
            if current[0] > 0:
                current[0] -= 1
                await inter.response.edit_message(embed=make_page(current[0]))
            else:
                await inter.response.defer()
        async def next_cb(inter: discord.Interaction):
            if current[0] < len(pages) - 1:
                current[0] += 1
                await inter.response.edit_message(embed=make_page(current[0]))
            else:
                await inter.response.defer()

        pb = discord.ui.Button(label="◀ Previous", style=discord.ButtonStyle.secondary)
        nb = discord.ui.Button(label="▶ Next",     style=discord.ButtonStyle.secondary)
        pb.callback = prev_cb; nb.callback = next_cb
        view.add_item(pb); view.add_item(nb)

        msg = await interaction.followup.send(embed=make_page(0), view=view)

        async def disable_after():
            await asyncio.sleep(120)
            try:
                for item in view.children:
                    item.disabled = True
                await msg.edit(view=view)
            except Exception:
                pass
        asyncio.create_task(disable_after())

    @app_commands.command(name="timelineadd", description="🗺️ Manually add a historical note — Core/OG only")
    @app_commands.describe(text="What happened?")
    async def timeline_add(self, interaction: discord.Interaction, text: str):
        if not _is_core(interaction.user):
            await interaction.response.send_message("Core/OG only.", ephemeral=True); return
        await log_timeline(interaction.guild_id, "📝", text, [interaction.user.id])
        await interaction.response.send_message("✅ Added to the timeline.", ephemeral=True)


# ─────────────────────────────────────────────────────────
# [ALTER EGO]  — Feature 22
# ─────────────────────────────────────────────────────────

class AlterEgo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ego", description="🎭 Manage your server alter ego")
    @app_commands.describe(action="What to do", member="Target member",
                           name="Ego name", description="Ego description", vibe="Ego vibe")
    @app_commands.choices(action=[
        app_commands.Choice(name="Set my ego",   value="set"),
        app_commands.Choice(name="Show someone's ego", value="show"),
        app_commands.Choice(name="Ego battle",   value="battle"),
        app_commands.Choice(name="List all egos", value="list"),
    ])
    async def ego(self, interaction: discord.Interaction,
                  action: str, member: discord.Member = None,
                  name: str = None, description: str = None, vibe: str = None):
        if action == "set":
            if not name or not description or not vibe:
                await interaction.response.send_message("Provide name, description, and vibe.", ephemeral=True); return
            async with get_db() as db:
                await db.execute(
                    "INSERT OR REPLACE INTO alter_egos (guild_id, user_id, name, description, vibe)"
                    " VALUES (?,?,?,?,?)",
                    (interaction.guild_id, interaction.user.id, name, description, vibe))
                await db.commit()
            embed = discord.Embed(title=f"🎭 Alter Ego Set", color=PURPLE)
            embed.add_field(name="👤 Name",        value=name,        inline=True)
            embed.add_field(name="📝 Description", value=description, inline=True)
            embed.add_field(name="✨ Vibe",         value=vibe,        inline=True)
            embed.set_footer(text=bonfire_footer("Alter Ego"))
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif action == "show":
            target = member or interaction.user
            async with get_db() as db:
                async with db.execute(
                    "SELECT name, description, vibe FROM alter_egos WHERE guild_id=? AND user_id=?",
                    (interaction.guild_id, target.id)) as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.response.send_message(f"{target.display_name} hasn't set an alter ego yet.", ephemeral=True); return
            name, desc, v = row
            embed = discord.Embed(title=f"🎭 {name}", description=desc, color=PURPLE)
            embed.add_field(name="✨ Vibe", value=v)
            embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
            embed.set_footer(text=bonfire_footer("Alter Ego"))
            await interaction.response.send_message(embed=embed)

        elif action == "battle":
            if not member:
                await interaction.response.send_message("Pick someone to battle.", ephemeral=True); return
            async with get_db() as db:
                async with db.execute(
                    "SELECT name, vibe FROM alter_egos WHERE guild_id=? AND user_id=?",
                    (interaction.guild_id, interaction.user.id)) as cur:
                    e1 = await cur.fetchone()
                async with db.execute(
                    "SELECT name, vibe FROM alter_egos WHERE guild_id=? AND user_id=?",
                    (interaction.guild_id, member.id)) as cur:
                    e2 = await cur.fetchone()
            if not e1 or not e2:
                await interaction.response.send_message("Both members need an alter ego set. Use `/ego set`.", ephemeral=True); return
            winner = random.choice([interaction.user, member])
            outcomes = [
                f"It was close, but {winner.display_name}'s energy completely absorbed the competition.",
                f"{winner.display_name} read the room better. It's not even close.",
                f"After a legendary clash, {winner.display_name} stands victorious. Barely.",
                f"The vibes were unmatched. {winner.display_name} wins by pure aura.",
            ]
            embed = discord.Embed(
                title=f"🎭 Ego Battle: {interaction.user.display_name} vs {member.display_name}",
                description=random.choice(outcomes),
                color=PURPLE)
            embed.add_field(name=f"⚔️ {e1[0]}", value=e1[1], inline=True)
            embed.add_field(name=f"⚔️ {e2[0]}", value=e2[1], inline=True)
            embed.add_field(name="🏆 Winner", value=winner.mention, inline=False)
            embed.set_footer(text=bonfire_footer("Alter Ego"))
            await interaction.response.send_message(embed=embed)

        elif action == "list":
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, name, vibe FROM alter_egos WHERE guild_id=?",
                    (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.response.send_message("No alter egos set yet.", ephemeral=True); return
            embed = discord.Embed(title="🎭 Server Alter Egos", color=PURPLE)
            for uid, ego_name, ego_vibe in rows:
                m = interaction.guild.get_member(uid)
                embed.add_field(name=f"{m.display_name if m else uid}", value=f"**{ego_name}** · {ego_vibe}", inline=True)
            embed.set_footer(text=bonfire_footer("Alter Ego"))
            await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────────────────
# [FRIDAY WEEKEND POST]  — Feature 23
# ─────────────────────────────────────────────────────────

class FridayPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.friday_post.start()
        self.friday_tally.start()

    def cog_unload(self):
        self.friday_post.cancel()
        self.friday_tally.cancel()

    @tasks.loop(hours=24)
    async def friday_post(self):
        if datetime.utcnow().weekday() != 4:
            return
        for guild in self.bot.guilds:
            ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                  discord.utils.get(guild.text_channels, name="general"))
            if not ch:
                continue

            votes = {"gaming": [], "movie": [], "meetup": [], "nothing": []}
            embed = discord.Embed(
                title="🔥 It's Friday. What's the move this weekend?",
                color=PRIMARY)
            embed.set_footer(text=bonfire_footer("Friday Post"))

            view = discord.ui.View(timeout=7200)
            for key, label in [("gaming","🎮 Gaming"), ("movie","🎬 Movie night"), ("meetup","📍 IRL meetup"), ("nothing","😴 Nothing")]:
                async def cb(inter: discord.Interaction, k=key, l=label):
                    for v in votes.values():
                        if inter.user.id in v: v.remove(inter.user.id)
                    votes[k].append(inter.user.id)
                    await inter.response.send_message(f"Voted **{l}**!", ephemeral=True)
                btn = discord.ui.Button(label=label, style=discord.ButtonStyle.primary)
                btn.callback = cb
                view.add_item(btn)

            await ch.send(embed=embed, view=view)

            # Store for tally
            async with get_db() as db:
                await db.execute(
                    "INSERT INTO weekly_vote (guild_id, posted_at) VALUES (?,?)",
                    (guild.id, datetime.utcnow()))
                await db.commit()

            # Post forecast at 7pm
            async def forecast():
                await asyncio.sleep(7200)
                top = max(votes, key=lambda k: len(votes[k]))
                labels = {"gaming":"🎮 Gaming","movie":"🎬 Movie Night","meetup":"📍 IRL Meetup","nothing":"😴 Chill night"}
                forecast_embed = discord.Embed(
                    title=f"📊 Weekend Forecast",
                    description=f"The squad has spoken. This weekend is **{labels[top]}** ({len(votes[top])} votes).",
                    color=PRIMARY)
                for k, l in labels.items():
                    forecast_embed.add_field(name=l, value=str(len(votes[k])), inline=True)
                forecast_embed.set_footer(text=bonfire_footer("Friday Post"))
                await ch.send(embed=forecast_embed)
            asyncio.create_task(forecast())

    @friday_post.before_loop
    async def before_friday(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        days_until_friday = (4 - now.weekday()) % 7
        if days_until_friday == 0 and now.hour >= 17:
            days_until_friday = 7
        target = (now + timedelta(days=days_until_friday)).replace(hour=17, minute=0, second=0, microsecond=0)
        await asyncio.sleep((target - now).total_seconds())

    @tasks.loop(hours=24)
    async def friday_tally(self):
        pass  # placeholder

    @friday_tally.before_loop
    async def before_tally(self):
        await self.bot.wait_until_ready()


# ─────────────────────────────────────────────────────────
# [DEAD CHAT DETECTION]  — Feature 24
# ─────────────────────────────────────────────────────────

class DeadChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_dead_chat.start()
        self.enabled = {}  # guild_id -> bool

    def cog_unload(self):
        self.check_dead_chat.cancel()

    @tasks.loop(minutes=30)
    async def check_dead_chat(self):
        for guild in self.bot.guilds:
            if not self.enabled.get(guild.id, True):
                continue
            ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                  discord.utils.get(guild.text_channels, name="general"))
            if not ch:
                continue

            # Check last message time
            try:
                async for msg in ch.history(limit=1):
                    last_msg_time = msg.created_at.replace(tzinfo=None)
                    hours_since = (datetime.utcnow() - last_msg_time).total_seconds() / 3600
                    if hours_since < DEAD_CHAT_HOURS:
                        break

                    # Check cooldown
                    async with get_db() as db:
                        async with db.execute(
                            "SELECT last_post FROM dead_chat_log WHERE guild_id=?", (guild.id,)) as cur:
                            row = await cur.fetchone()
                    if row:
                        hours_since_last = (datetime.utcnow() - datetime.fromisoformat(row[0])).total_seconds() / 3600
                        if hours_since_last < DEAD_CHAT_COOLDOWN_HOURS:
                            break

                    # Post prompt
                    prompt_type = random.choice(["message", "spark", "icebreaker"])
                    if prompt_type == "message":
                        content = random.choice(DEAD_CHAT_PROMPTS)
                        await ch.send(content)
                    elif prompt_type == "spark":
                        spark = random.choice(BONFIRE_SPARKS)
                        embed = discord.Embed(description=f"🔥 **{spark}**", color=PRIMARY)
                        embed.set_footer(text=bonfire_footer("Dead Chat"))
                        await ch.send(embed=embed)
                    else:
                        q = random.choice(ICEBREAKER_QUESTIONS)[1]
                        embed = discord.Embed(
                            title="🧊 Keeping the fire going",
                            description=q,
                            color=TEAL)
                        embed.set_footer(text=bonfire_footer("Dead Chat"))
                        await ch.send(embed=embed)

                    async with get_db() as db:
                        await db.execute(
                            "INSERT OR REPLACE INTO dead_chat_log (guild_id, last_post) VALUES (?,?)",
                            (guild.id, datetime.utcnow().isoformat()))
                        await db.commit()
            except Exception:
                pass

    @check_dead_chat.before_loop
    async def before_dead_chat(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="deadchat", description="🔥 Toggle dead chat detection")
    @app_commands.choices(action=[
        app_commands.Choice(name="Turn off", value="off"),
        app_commands.Choice(name="Turn on",  value="on"),
    ])
    async def deadchat(self, interaction: discord.Interaction, action: str):
        if not _is_core(interaction.user):
            await interaction.response.send_message("Core/OG only.", ephemeral=True); return
        self.enabled[interaction.guild_id] = (action == "on")
        await interaction.response.send_message(
            f"🔥 Dead chat detection turned **{action}**.", ephemeral=True)


# ─────────────────────────────────────────────────────────
# [SEASONS]  — Feature 25
# ─────────────────────────────────────────────────────────

class Seasons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quarterly_season.start()

    def cog_unload(self):
        self.quarterly_season.cancel()

    @tasks.loop(hours=2160)  # ~90 days
    async def quarterly_season(self):
        for guild in self.bot.guilds:
            # End previous season
            async with get_db() as db:
                async with db.execute(
                    "SELECT id, name, started_at FROM seasons WHERE guild_id=? AND ended_at IS NULL ORDER BY id DESC LIMIT 1",
                    (guild.id,)) as cur:
                    prev = await cur.fetchone()
                if prev:
                    await db.execute("UPDATE seasons SET ended_at=? WHERE id=?", (datetime.utcnow(), prev[0]))
                    await db.commit()

            # Start new season
            season_name = random.choice(SEASON_NAMES)
            async with get_db() as db:
                await db.execute(
                    "INSERT INTO seasons (guild_id, name, started_at) VALUES (?,?,?)",
                    (guild.id, season_name, datetime.utcnow()))
                await db.commit()

            ch = (discord.utils.get(guild.text_channels, name="📊・status") or
                  discord.utils.get(guild.text_channels, name="status") or
                  discord.utils.get(guild.text_channels, name="general"))
            if not ch:
                continue
 
            # Build recap embed for old season
            if prev:
                old_name   = prev[1]
                started_at = prev[2]
                week_ago   = (datetime.utcnow() - timedelta(days=90)).isoformat()
                async with get_db() as db:
                    async with db.execute(
                        "SELECT user_id, COUNT(*) cnt FROM activity_log"
                        " WHERE guild_id=? AND created_at>=? AND activity_type='message'"
                        " GROUP BY user_id ORDER BY cnt DESC LIMIT 1", (guild.id, week_ago)) as cur:
                        mvp_row = await cur.fetchone()
                    async with db.execute(
                        "SELECT COUNT(*) FROM beef WHERE guild_id=? AND created_at>=?",
                        (guild.id, week_ago)) as cur:
                        beef_cnt = (await cur.fetchone())[0]
                    async with db.execute(
                        "SELECT COUNT(*) FROM lore WHERE guild_id=? AND created_at>=?",
                        (guild.id, week_ago)) as cur:
                        lore_cnt = (await cur.fetchone())[0]
 
                recap = discord.Embed(
                    title=f"🏕️ Season Recap — {old_name}",
                    description="Another era ends at the bonfire. Here's what went down.",
                    color=GOLD)
                if mvp_row:
                    m = guild.get_member(mvp_row[0])
                    recap.add_field(name="🏆 MVP", value=m.display_name if m else str(mvp_row[0]), inline=True)
                recap.add_field(name="🥩 Beefs",      value=str(beef_cnt), inline=True)
                recap.add_field(name="📖 Lore Added", value=str(lore_cnt), inline=True)
                recap.set_footer(text=bonfire_footer("Seasons"))
                await ch.send(embed=recap)
 
            # Announce new season
            new_embed = discord.Embed(
                title=f"🔥 New Season: {season_name}",
                description="A new chapter begins at the bonfire. Make it legendary.",
                color=PRIMARY)
            new_embed.set_footer(text=bonfire_footer("Seasons"))
            await ch.send(embed=new_embed)
            await log_timeline(guild.id, "🏕️", f"New season started: {season_name}")
 
    @quarterly_season.before_loop
    async def before_season(self):
        await self.bot.wait_until_ready()
 
    @app_commands.command(name="season", description="🏕️ View current or past seasons")
    @app_commands.choices(view=[
        app_commands.Choice(name="Current season", value="current"),
        app_commands.Choice(name="Season history",  value="history"),
    ])
    async def season(self, interaction: discord.Interaction, view: str = "current"):
        await interaction.response.defer()
        if view == "current":
            async with get_db() as db:
                async with db.execute(
                    "SELECT name, started_at FROM seasons WHERE guild_id=? AND ended_at IS NULL"
                    " ORDER BY id DESC LIMIT 1", (interaction.guild_id,)) as cur:
                    row = await cur.fetchone()
            if not row:
                await interaction.followup.send("No active season. One starts automatically every 3 months.", ephemeral=True)
                return
            name, started_at = row
            days_in = (datetime.utcnow() - datetime.fromisoformat(str(started_at))).days
            week_ago = (datetime.utcnow() - timedelta(days=days_in)).isoformat()
            async with get_db() as db:
                async with db.execute(
                    "SELECT user_id, COUNT(*) cnt FROM activity_log"
                    " WHERE guild_id=? AND created_at>=? AND activity_type='message'"
                    " GROUP BY user_id ORDER BY cnt DESC LIMIT 5", (interaction.guild_id, week_ago)) as cur:
                    top = await cur.fetchall()
                async with db.execute(
                    "SELECT COUNT(*) FROM beef WHERE guild_id=? AND created_at>=?",
                    (interaction.guild_id, week_ago)) as cur:
                    beef_cnt = (await cur.fetchone())[0]
            embed = discord.Embed(
                title=f"🏕️ Current Season: {name}",
                description=f"Day **{days_in}** of the season",
                color=PRIMARY)
            if top:
                lines = []
                for uid, cnt in top:
                    m = interaction.guild.get_member(uid)
                    lines.append(f"{m.display_name if m else uid} ({cnt} messages)")
                embed.add_field(name="💬 Top Talkers", value="\n".join(lines), inline=False)
            embed.add_field(name="🥩 Beefs This Season", value=str(beef_cnt), inline=True)
            embed.set_footer(text=bonfire_footer("Seasons"))
            await interaction.followup.send(embed=embed)
 
        else:
            async with get_db() as db:
                async with db.execute(
                    "SELECT name, started_at, ended_at FROM seasons WHERE guild_id=? ORDER BY id DESC LIMIT 10",
                    (interaction.guild_id,)) as cur:
                    rows = await cur.fetchall()
            if not rows:
                await interaction.followup.send("No seasons recorded yet.", ephemeral=True)
                return
            embed = discord.Embed(title="🏕️ Season History", color=GOLD)
            for name, started, ended in rows:
                duration = ""
                if started and ended:
                    d = (datetime.fromisoformat(str(ended)) - datetime.fromisoformat(str(started))).days
                    duration = f" · {d} days"
                status = "🔥 Active" if not ended else f"Ended {str(ended)[:10]}"
                embed.add_field(
                    name=name,
                    value=f"Started {str(started)[:10]}{duration} · {status}",
                    inline=False)
            embed.set_footer(text=bonfire_footer("Seasons"))
            await interaction.followup.send(embed=embed)
 
 
# ─────────────────────────────────────────────────────────
# [SMART NOTIFICATIONS]  — Feature 21
# ─────────────────────────────────────────────────────────
 
NOTIFY_KEYS = [
    ("highlights",    "⭐ New highlights"),
    ("quotes",        "💬 Quotes about you"),
    ("beef",          "🥩 Beef started with you"),
    ("meetups",       "📍 Meetup reminders"),
    ("digest",        "📰 Weekly digest"),
    ("pulse",         "🩺 Friday vibe pulse DMs"),
    ("icebreaker",    "🧊 Icebreaker posts"),
    ("temperature",   "🌡️ Server temperature alerts"),
]
 
 
class Notify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    async def _get_prefs(self, guild_id: int, user_id: int) -> dict:
        async with get_db() as db:
            async with db.execute(
                "SELECT prefs FROM notify_prefs WHERE guild_id=? AND user_id=?",
                (guild_id, user_id)) as cur:
                row = await cur.fetchone()
        if not row:
            return {k: True for k, _ in NOTIFY_KEYS}
        return json.loads(row[0])
 
    async def _save_prefs(self, guild_id: int, user_id: int, prefs: dict):
        async with get_db() as db:
            await db.execute(
                "INSERT OR REPLACE INTO notify_prefs (guild_id, user_id, prefs) VALUES (?,?,?)",
                (guild_id, user_id, json.dumps(prefs)))
            await db.commit()
 
    @app_commands.command(name="notify", description="🔔 Manage your notification preferences")
    @app_commands.choices(action=[
        app_commands.Choice(name="Settings dashboard", value="set"),
        app_commands.Choice(name="View current status", value="status"),
    ])
    async def notify(self, interaction: discord.Interaction, action: str = "status"):
        prefs = await self._get_prefs(interaction.guild_id, interaction.user.id)
 
        if action == "status":
            embed = discord.Embed(title="🔔 Your Notification Settings", color=TEAL)
            for key, label in NOTIFY_KEYS:
                val = prefs.get(key, True)
                embed.add_field(name=label, value="✅ On" if val else "🔕 Off", inline=True)
            embed.set_footer(text=bonfire_footer("Notifications"))
            await interaction.response.send_message(embed=embed, ephemeral=True)
 
        else:
            embed = discord.Embed(
                title="🔔 Notification Settings",
                description="Toggle what you want to hear about:",
                color=TEAL)
            embed.set_footer(text=bonfire_footer("Notifications"))
 
            view = discord.ui.View(timeout=120)
            for key, label in NOTIFY_KEYS:
                current = prefs.get(key, True)
                style = discord.ButtonStyle.success if current else discord.ButtonStyle.secondary
                async def toggle_cb(inter: discord.Interaction, k=key, lbl=label):
                    p = await self._get_prefs(inter.guild_id, inter.user.id)
                    p[k] = not p.get(k, True)
                    await self._save_prefs(inter.guild_id, inter.user.id, p)
                    status = "✅ On" if p[k] else "🔕 Off"
                    await inter.response.send_message(f"**{lbl}** → {status}", ephemeral=True)
                btn = discord.ui.Button(
                    label=f"{'✅' if current else '🔕'} {label[:20]}",
                    style=style)
                btn.callback = toggle_cb
                view.add_item(btn)
 
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
 
    async def send_notify(self, guild_id: int, user_id: int, key: str, embed: discord.Embed):
        """Send a DM notification if the user has that key enabled."""
        prefs = await self._get_prefs(guild_id, user_id)
        if not prefs.get(key, True):
            return
        guild  = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id) if guild else None
        if not member:
            return
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass
 
 
# ─────────────────────────────────────────────────────────
# [FRIENDSHIP MILESTONES]  — Feature 19
# ─────────────────────────────────────────────────────────
 
class FriendshipMilestones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    async def _post_milestone(self, guild, user1_id: int, user2_id: int, milestone: str):
        async with get_db() as db:
            async with db.execute(
                "SELECT id FROM friendship_milestones WHERE guild_id=? AND user1_id=? AND user2_id=? AND milestone=?",
                (guild.id, min(user1_id, user2_id), max(user1_id, user2_id), milestone)) as cur:
                if await cur.fetchone():
                    return  # already logged
            await db.execute(
                "INSERT INTO friendship_milestones (guild_id, user1_id, user2_id, milestone) VALUES (?,?,?,?)",
                (guild.id, min(user1_id, user2_id), max(user1_id, user2_id), milestone))
            await db.commit()
 
        m1 = guild.get_member(user1_id)
        m2 = guild.get_member(user2_id)
        ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
              discord.utils.get(guild.text_channels, name="general"))
        if not ch or not m1 or not m2:
            return
 
        embed = discord.Embed(
            title="🤝 Friendship Level Up",
            description=f"{m1.mention} & {m2.mention}\n\n**{milestone}**",
            color=PRIMARY)
        embed.set_footer(text=bonfire_footer("Milestones"))
        await ch.send(embed=embed)
        await log_timeline(guild.id, "🤝", f"Milestone: {m1.display_name} & {m2.display_name} — {milestone}",
                           [user1_id, user2_id])
 
    async def check_vc_milestone(self, guild, user1_id: int, user2_id: int):
        async with get_db() as db:
            async with db.execute(
                "SELECT COUNT(*) FROM vc_sessions WHERE guild_id=?"
                " AND members LIKE ? AND members LIKE ?",
                (guild.id, f'%{user1_id}%', f'%{user2_id}%')) as cur:
                count = (await cur.fetchone())[0]
        if count == 1:
            await self._post_milestone(guild, user1_id, user2_id, "🔥 First Spark — first VC session together")
        elif count == 10:
            await self._post_milestone(guild, user1_id, user2_id, "🔥 Real Ones — 10 VC sessions together")
 
    @app_commands.command(name="milestones", description="🤝 View friendship milestones with someone")
    @app_commands.describe(member="Who to check")
    async def milestones(self, interaction: discord.Interaction, member: discord.Member):
        u1 = min(interaction.user.id, member.id)
        u2 = max(interaction.user.id, member.id)
        async with get_db() as db:
            async with db.execute(
                "SELECT milestone, created_at FROM friendship_milestones"
                " WHERE guild_id=? AND user1_id=? AND user2_id=? ORDER BY created_at ASC",
                (interaction.guild_id, u1, u2)) as cur:
                rows = await cur.fetchall()
        if not rows:
            await interaction.response.send_message(
                f"No milestones yet with {member.display_name}. Spend more time together!", ephemeral=True)
            return
        embed = discord.Embed(
            title=f"🤝 {interaction.user.display_name} & {member.display_name}",
            description=f"{len(rows)} milestone(s) together",
            color=PRIMARY)
        embed.set_thumbnail(url=member.display_avatar.url)
        for milestone, created_at in rows:
            embed.add_field(name=str(created_at)[:10], value=milestone, inline=False)
        embed.set_footer(text=bonfire_footer("Milestones"))
        await interaction.response.send_message(embed=embed)
 
    async def check_server_anniversary(self, guild, member: discord.Member):
        if not member.joined_at:
            return
        days = (datetime.utcnow() - member.joined_at.replace(tzinfo=None)).days
        milestones_map = {
            30:  "📅 1 Month at the Bonfire",
            90:  "📅 3 Months — you're becoming lore",
            180: "📅 6 Months — a true regular",
            365: "🏆 1 Year Anniversary — a legend of the bonfire",
        }
        if days in milestones_map:
            ch = (discord.utils.get(guild.text_channels, name="🔥・general") or
                  discord.utils.get(guild.text_channels, name="general"))
            if ch:
                embed = discord.Embed(
                    title="📅 Server Anniversary",
                    description=f"{member.mention} — **{milestones_map[days]}**\n{days} days and counting.",
                    color=GOLD)
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=bonfire_footer("Milestones"))
                await ch.send(embed=embed)
 
 
# ─────────────────────────────────────────────────────────
# [EVENT LISTENERS — central hub]
# ─────────────────────────────────────────────────────────
 
class EventHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    # ── Message events ────────────────────────────────────
 
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
 
        streak_cog    = self.bot.get_cog("Streak")
        auto_role_cog = self.bot.get_cog("AutoRoles")
        milestones_cog = self.bot.get_cog("FriendshipMilestones")
 
        if streak_cog:
            await streak_cog.record_activity(message.guild.id)
        if auto_role_cog:
            await auto_role_cog.increment_messages(message.guild.id, message.author.id)
 
        # Log activity
        async with get_db() as db:
            await db.execute(
                "INSERT INTO activity_log (guild_id, user_id, activity_type, detail) VALUES (?,?,?,?)",
                (message.guild.id, message.author.id, "message", message.channel.name))
            await db.commit()
 
        # Server anniversary check (daily, only if message was first today from user)
        if milestones_cog and message.author.joined_at:
            today = datetime.utcnow().date()
            join_day = message.author.joined_at.date()
            if today.month == join_day.month and today.day == join_day.day:
                await milestones_cog.check_server_anniversary(message.guild, message.author)
 
    # ── Reaction events ───────────────────────────────────
 
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return
 
        emoji = str(payload.emoji)
 
        if emoji == "⭐":
            channel = guild.get_channel(payload.channel_id)
            if channel:
                try:
                    message = await channel.fetch_message(payload.message_id)
                    star_count = sum(1 for r in message.reactions if str(r.emoji) == "⭐" and r.count >= HIGHLIGHT_STAR_THRESHOLD)
                    if star_count >= 1:
                        highlights_cog = self.bot.get_cog("Highlights")
                        if highlights_cog:
                            await highlights_cog.post_highlight(message)
                except (discord.NotFound, discord.Forbidden):
                    pass
 
        elif emoji == "💬":
            channel = guild.get_channel(payload.channel_id)
            if channel:
                try:
                    message = await channel.fetch_message(payload.message_id)
                    if message.author.bot or not message.content:
                        return
                    async with get_db() as db:
                        await db.execute(
                            "INSERT OR IGNORE INTO quotes (guild_id, message_id, author_id, content, jump_url)"
                            " VALUES (?,?,?,?,?)",
                            (guild.id, message.id, message.author.id, message.content, message.jump_url))
                        await db.commit()
                    q_ch = (discord.utils.get(guild.text_channels, name="💬・quotes-wall") or
                            discord.utils.get(guild.text_channels, name="quotes-wall"))
                    if q_ch:
                        q_embed = discord.Embed(description=f'"{message.content}"', color=TEAL)
                        q_embed.set_author(name=message.author.display_name,
                                           icon_url=message.author.display_avatar.url)
                        q_embed.set_footer(text=bonfire_footer("Quotes"))
                        await q_ch.send(embed=q_embed)
                    await log_timeline(guild.id, "💬",
                                       f"{message.author.display_name} was quoted: {message.content[:60]}",
                                       [message.author.id, payload.user_id])
                except (discord.NotFound, discord.Forbidden):
                    pass
 
        elif emoji == "📖":
            channel = guild.get_channel(payload.channel_id)
            if channel:
                try:
                    message = await channel.fetch_message(payload.message_id)
                    if message.author.bot or not message.content:
                        return
                    async with get_db() as db:
                        await db.execute(
                            "INSERT INTO lore (guild_id, author_id, target_id, content) VALUES (?,?,?,?)",
                            (guild.id, payload.user_id, message.author.id, message.content))
                        await db.commit()
                    lore_ch = (discord.utils.get(guild.text_channels, name="📖・lore-archive") or
                               discord.utils.get(guild.text_channels, name="lore-archive"))
                    if lore_ch:
                        lore_embed = discord.Embed(
                            title="📖 Lore Added",
                            description=message.content,
                            color=PURPLE)
                        lore_embed.set_footer(text=bonfire_footer("Lore"))
                        await lore_ch.send(embed=lore_embed)
                    await log_timeline(guild.id, "📖",
                                       f"Lore: {message.content[:60]}",
                                       [message.author.id])
                except (discord.NotFound, discord.Forbidden):
                    pass
 
    # ── Voice state events ────────────────────────────────
 
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member,
                                    before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild
 
        auto_role_cog = self.bot.get_cog("AutoRoles")
        voice_log_cog = self.bot.get_cog("VoiceLog")
        milestones_cog = self.bot.get_cog("FriendshipMilestones")
        clutch_cog    = self.bot.get_cog("Clutch")
 
        # Member joined a VC
        if after.channel and after.channel != before.channel:
            async with get_db() as db:
                async with db.execute(
                    "SELECT members, started_at FROM vc_active WHERE guild_id=? AND channel_id=?",
                    (guild.id, after.channel.id)) as cur:
                    row = await cur.fetchone()
            if row:
                members_ids = json.loads(row[0])
                if member.id not in members_ids:
                    members_ids.append(member.id)
                async with get_db() as db:
                    await db.execute(
                        "UPDATE vc_active SET members=? WHERE guild_id=? AND channel_id=?",
                        (json.dumps(members_ids), guild.id, after.channel.id))
                    await db.commit()
                # Milestone: first VC together with each other member
                if milestones_cog:
                    for uid in members_ids:
                        if uid != member.id:
                            await milestones_cog.check_vc_milestone(guild, member.id, uid)
            else:
                async with get_db() as db:
                    await db.execute(
                        "INSERT INTO vc_active (guild_id, channel_id, members, started_at) VALUES (?,?,?,?)",
                        (guild.id, after.channel.id, json.dumps([member.id]), datetime.utcnow()))
                    await db.commit()
 
            # Late VC role tracking
            if auto_role_cog:
                await auto_role_cog.log_late_vc(guild.id, member.id)
 
        # Member left a VC
        if before.channel and before.channel != after.channel:
            async with get_db() as db:
                async with db.execute(
                    "SELECT members, started_at FROM vc_active WHERE guild_id=? AND channel_id=?",
                    (guild.id, before.channel.id)) as cur:
                    row = await cur.fetchone()
            if row:
                members_ids = json.loads(row[0])
                members_ids = [uid for uid in members_ids if uid != member.id]
 
                if not members_ids:
                    # Session ended — everyone left
                    started_at = datetime.fromisoformat(str(row[1]))
                    past_members_objs = [guild.get_member(uid) for uid in json.loads(row[0]) if guild.get_member(uid)]
 
                    async with get_db() as db:
                        await db.execute(
                            "DELETE FROM vc_active WHERE guild_id=? AND channel_id=?",
                            (guild.id, before.channel.id))
                        await db.commit()
 
                    if voice_log_cog and past_members_objs:
                        await voice_log_cog.session_ended(guild, before.channel, past_members_objs, started_at)
                else:
                    async with get_db() as db:
                        await db.execute(
                            "UPDATE vc_active SET members=? WHERE guild_id=? AND channel_id=?",
                            (json.dumps(members_ids), guild.id, before.channel.id))
                        await db.commit()
 
                    # Clutch check: only one person left
                    if len(members_ids) == 1 and clutch_cog:
                        lone_member = guild.get_member(members_ids[0])
                        if lone_member:
                            await clutch_cog.check_clutch(guild, before.channel, lone_member)
 
        # Log activity
        async with get_db() as db:
            await db.execute(
                "INSERT INTO activity_log (guild_id, user_id, activity_type, detail) VALUES (?,?,?,?)",
                (guild.id, member.id, "vc",
                 f"joined {after.channel.name}" if after.channel else f"left {before.channel.name}"))
            await db.commit()
 
 
# ─────────────────────────────────────────────────────────
# [BOT CORE]
# ─────────────────────────────────────────────────────────
 
ALL_COGS = [
    Setup,
    Onboarding,
    Utility,
    Voice,
    Fun,
    LFG,
    Reminders,
    Highlights,
    Lore,
    Quotes,
    Beef,
    VibeCheck,
    Streak,
    Wrapped,
    Clutch,
    AutoRoles,
    Story,
    Vouch,
    Weather,
    Challenge,
    # New features (1-25)
    LateNight,
    Meetup,
    WeeklyDigest,
    Icebreaker,
    VibePulse,
    Achievements,
    Poll,
    PairChat,
    MemoryBoard,
    CheckIn,
    VoiceLog,
    Drama,
    StatsCard,
    BonfireBets,
    ServerTemp,
    Confessions,
    Availability,
    HotSeat,
    FriendshipMilestones,
    Timeline,
    Notify,
    AlterEgo,
    FridayPost,
    DeadChat,
    Seasons,
    # Central event hub (must be last so cog references resolve)
    EventHub,
]
 
 
class BonfireBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members          = True
        intents.voice_states     = True
        intents.reactions        = True
        super().__init__(command_prefix="!", intents=intents)
 
    async def setup_hook(self):
        await init_db()
        for cog_cls in ALL_COGS:
            await self.add_cog(cog_cls(self))
        await self.tree.sync()
        print(f"[Bonfire] Synced {len(ALL_COGS)} cogs and slash commands.")
 
    async def on_ready(self):
        print(f"[Bonfire] 🔥 {self.user} is online — {len(self.guilds)} guild(s)")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="the bonfire burn 🔥"))
 
    async def on_app_command_error(self, interaction: discord.Interaction,
                                   error: app_commands.AppCommandError):
        msg = str(error)
        embed = discord.Embed(
            title="🚨 Something went wrong",
            description=msg[:500],
            color=discord.Color.red())
        embed.set_footer(text=bonfire_footer("Error"))
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            pass
 
 
# ─────────────────────────────────────────────────────────
# [ENTRY POINT]
# ─────────────────────────────────────────────────────────
 
def main():
    if not DISCORD_TOKEN:
        print("[Bonfire] ❌ DISCORD_TOKEN not set in .env")
        sys.exit(1)
    bot = BonfireBot()
    bot.run(DISCORD_TOKEN)
 
 
if __name__ == "__main__":
    main()
