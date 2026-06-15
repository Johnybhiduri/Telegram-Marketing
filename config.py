"""
╔══════════════════════════════════════════════════════════════════╗
║        TELEGRAM MARKETING BOT — config.py                       ║
║  Edit ONLY this file and templates.py before running main.py    ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────────────────────────
# STEP 1 ─ API CREDENTIALS
# Get these from https://my.telegram.org  (free, one-time setup)
# ─────────────────────────────────────────────────────────────────
API_ID   = 12345678            # ← Replace with YOUR api_id   (integer, no quotes)
API_HASH = "your_api_hash"     # ← Replace with YOUR api_hash (string, with quotes)
PHONE    = "+91XXXXXXXXXX"     # ← Your phone number with country code

# ─────────────────────────────────────────────────────────────────
# STEP 2 ─ SESSION FILE NAME
# Telethon creates a file called "marketing_session.session"
# in your project folder. Keep it safe — it stores your login.
# ─────────────────────────────────────────────────────────────────
SESSION_NAME = "marketing_session"

# ─────────────────────────────────────────────────────────────────
# STEP 3 ─ DEVICE INFO
# Makes Telethon look like a real Android phone to Telegram.
# You can change the model name if you like.
# ─────────────────────────────────────────────────────────────────
DEVICE_MODEL   = "Samsung Galaxy S23"
SYSTEM_VERSION = "Android 14"
APP_VERSION    = "10.9.1"

# ─────────────────────────────────────────────────────────────────
# STEP 4 ─ GROUPS TO POST IN
# ─────────────────────────────────────────────────────────────────
# Rules:
#   - You MUST already be a member of every group listed here.
#   - The group MUST allow marketing/promotional posts.
#   - Use the group's @username WITHOUT the @ sign.
#   - Or use the group's numeric ID (negative number like -1001234567890).
#   - Do NOT add groups that ban advertising — it wastes your time
#     and trains Telegram to flag your account.
# ─────────────────────────────────────────────────────────────────
GROUPS = [
    "example_promo_group_1",      # ← Replace with real group usernames
    "example_business_group_2",
    "example_marketplace_group_3",
    # "example_group_4",
    # "example_group_5",
    # Add as many as you want — but quality > quantity.
    # 10-20 highly relevant groups is better than 100 random ones.
]

# ─────────────────────────────────────────────────────────────────
# STEP 5 ─ TIMING (in seconds)
# ─────────────────────────────────────────────────────────────────
# Between every single post, the bot waits a RANDOM amount of time
# within this range.  30–60 minutes is human-like and safe.
# Do NOT go below 20 minutes — shorter intervals risk your account.
# ─────────────────────────────────────────────────────────────────
MIN_DELAY = 30 * 60    # 30 minutes = 1800 seconds
MAX_DELAY = 60 * 60    # 60 minutes = 3600 seconds

# ─────────────────────────────────────────────────────────────────
# STEP 6 ─ DAILY POSTING LIMIT (safety cap)
# ─────────────────────────────────────────────────────────────────
# Maximum number of posts per 24 hours across ALL groups combined.
# Keeps your activity looking human-level even if your group list is large.
MAX_POSTS_PER_DAY = 30