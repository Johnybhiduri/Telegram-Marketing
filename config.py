"""
╔══════════════════════════════════════════════════════════════════╗
║        TELEGRAM MARKETING BOT — config.py                       ║
║  Edit .env, groups.txt, and templates.txt instead of this file  ║
╚══════════════════════════════════════════════════════════════════╝
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────────────────────────
# STEP 1 ─ API CREDENTIALS & SETTINGS (From .env)
# ─────────────────────────────────────────────────────────────────
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
PHONE = os.getenv("PHONE", "")
SESSION_NAME = os.getenv("SESSION_NAME", "marketing_session")

MIN_DELAY = int(os.getenv("MIN_DELAY", 1800))      # in seconds
MAX_DELAY = int(os.getenv("MAX_DELAY", 3600))      # in seconds
MAX_POSTS_PER_DAY = int(os.getenv("MAX_POSTS_PER_DAY", 300))

# ─────────────────────────────────────────────────────────────────
# STEP 2 ─ DEVICE INFO (Makes Telethon look like a real phone)
# ─────────────────────────────────────────────────────────────────
DEVICE_MODEL = "Samsung Galaxy S23"
SYSTEM_VERSION = "Android 14"
APP_VERSION = "10.9.1"

# ─────────────────────────────────────────────────────────────────
# STEP 3 ─ LOAD GROUPS FROM groups.txt
# ─────────────────────────────────────────────────────────────────
def load_groups_from_txt():
    groups = []
    if not os.path.exists("groups.txt"):
        print("⚠️ groups.txt not found. Please create it.")
        return groups
    
    with open("groups.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignore empty lines and comments
            if line and not line.startswith("#"):
                groups.append(line)
    return groups

GROUPS = load_groups_from_txt()

# ─────────────────────────────────────────────────────────────────
# STEP 4 ─ LOAD TEMPLATES FROM templates.txt
# ─────────────────────────────────────────────────────────────────
def load_templates_from_txt():
    templates_list = []
    if not os.path.exists("templates.txt"):
        print("⚠️ templates.txt not found. Please create it.")
        return templates_list
    
    with open("templates.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by the === separator
    blocks = content.split("===")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        image_path = None
        # Check if the block starts with an image tag
        if block.startswith("[IMAGE:"):
            end_idx = block.find("]")
            if end_idx != -1:
                image_path = block[7:end_idx].strip()
                block = block[end_idx+1:].strip() # Remove the tag from the text
        
        templates_list.append({
            "text": block,
            "image": image_path if image_path else None
        })
    
    return templates_list

TEMPLATES = load_templates_from_txt()