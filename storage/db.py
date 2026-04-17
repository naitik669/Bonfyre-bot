import aiosqlite

DB_PATH = "bot.db"


async def get_db():
    return await aiosqlite.connect(DB_PATH)


async def init_db():
    async with await get_db() as db:

        # =========================
        # ICEBREAKERS
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS icebreakers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL
        )
        """)

        # =========================
        # CLUTCH COOLDOWN
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS clutch_cooldown (
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            last_ping TEXT,
            PRIMARY KEY (guild_id, channel_id)
        )
        """)

        # =========================
        # QUOTES
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            content TEXT,
            created_at TEXT
        )
        """)

        # =========================
        # ECONOMY
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS economy (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
        """)

        # =========================
        # LEVELS / XP
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS levels (
            user_id INTEGER,
            guild_id INTEGER,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        )
        """)

        # =========================
        # TICKETS
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            channel_id INTEGER,
            status TEXT DEFAULT 'open',
            created_at TEXT
        )
        """)

        # =========================
        # SETTINGS (GENERIC)
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER,
            key TEXT,
            value TEXT,
            PRIMARY KEY (guild_id, key)
        )
        """)

        # =========================
        # DEFAULT DATA (ICEBREAKERS)
        # =========================
        async with db.execute("SELECT COUNT(*) FROM icebreakers") as cur:
            count = (await cur.fetchone())[0]

        if count == 0:
            await db.executemany(
                "INSERT INTO icebreakers (question) VALUES (?)",
                [
                    ("What's your favorite hobby?",),
                    ("If you could travel anywhere, where would you go?",),
                    ("What's your dream job?",),
                    ("Favorite movie or series?",),
                    ("What's something you're proud of?",),
                ]
            )

        await db.commit()
