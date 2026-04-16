import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

HIGHLIGHT_STAR_THRESHOLD = 1
ROAST_COOLDOWN_SECONDS = 30
DECIDE_COOLDOWN_SECONDS = 10
SPAM_MESSAGE_THRESHOLD = 5
SPAM_TIME_WINDOW_SECONDS = 5
CLUTCH_COOLDOWN_MINUTES = 15
LFG_EXPIRY_MINUTES = 30

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
    "no bad days in this server",
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
]

CLUTCH_MESSAGES = [
    "bro {lonely} is alone in VC… who's gonna pull up?",
    "{lonely} is holding down the VC solo rn, someone roll through",
    "{lonely} is just vibing alone in VC, don't leave them hanging",
    "VC check: {lonely} is in there all by themselves 💀 {pinged} pull up",
    "{lonely} deployed solo mode in VC, someone rescue them",
]
