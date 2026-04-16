import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "csb.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS highlights (
                message_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                channel_id INTEGER,
                author_id INTEGER,
                content TEXT,
                jump_url TEXT,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                channel_id INTEGER,
                user_id INTEGER,
                message TEXT,
                trigger_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS lore (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                author_id INTEGER,
                target_id INTEGER,
                content TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                message_id INTEGER UNIQUE,
                author_id INTEGER,
                content TEXT,
                jump_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS beef (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                initiator_id INTEGER,
                target_id INTEGER,
                reason TEXT,
                resolved INTEGER DEFAULT 0,
                winner_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS vibe_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                guild_id INTEGER PRIMARY KEY,
                current_streak INTEGER DEFAULT 0,
                last_active_date TEXT,
                longest_streak INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                activity_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS lfg_lobbies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                channel_id INTEGER,
                message_id INTEGER,
                creator_id INTEGER,
                game TEXT,
                size INTEGER,
                members TEXT DEFAULT '[]',
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clutch_opt_in (
                guild_id INTEGER,
                user_id INTEGER,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clutch_cooldown (
                guild_id INTEGER,
                channel_id INTEGER,
                last_ping TIMESTAMP,
                PRIMARY KEY (guild_id, channel_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS decide_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                options TEXT,
                result TEXT,
                decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def get_db():
    return aiosqlite.connect(DB_PATH)
