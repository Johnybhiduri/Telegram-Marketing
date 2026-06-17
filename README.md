📢 Telegram Marketing Bot
Automatically posts your message (with optional images) to Telegram groups — so you don't have to do it manually.

📁 Files in This Folder
| File | What it is |
| --- | --- |
| `main.py` | The bot engine — do not touch this |
| `config.py` | Reads settings automatically — do not touch |
| `.env` | ✏️ **You edit this** — your API keys & settings |
| `groups.txt` | ✏️ **You edit this** — list of groups to post in |
| `templates.txt` | ✏️ **You edit this** — your marketing messages & images |
| `requirements.txt` | Do not touch |
| `run.bat` | Double-click this to start the bot |

✅ BEFORE YOU START — Things You Need
- A Windows laptop/PC that stays ON
- Telegram account (already on your phone)
- Internet connection
- 15 minutes to set up (only once)

STEP 1 — Install Python
1. Go to 👉 https://python.org/downloads
2. Click the big yellow Download Python button
3. Open the downloaded file
4. ⚠️ **VERY IMPORTANT** — Before clicking Install, tick the box that says **"Add Python to PATH"**
5. Click Install Now → Wait → Click Close
6. Check it worked: Press `Windows key + R`, type `cmd`, press Enter. Type `python --version`. You should see `Python 3.x.x` ✅

STEP 2 — Set Up the Project Folder
1. Create a new folder on your Desktop called `telegram_marketing`
2. Put all downloaded files into that folder.
3. Create three new text files in this folder: `.env`, `groups.txt`, and `templates.txt`.

STEP 3 — Install the Required Libraries
1. Press `Windows key + R` → type `cmd` → press Enter
2. Type: `cd Desktop\telegram_marketing` and press Enter
3. Type: `pip install -r requirements.txt` and press Enter
*(Make sure `python-dotenv` and `telethon` are in your requirements.txt)*

STEP 4 — Get Your Telegram API ID and Hash
1. Open Google Chrome → Go to 👉 https://my.telegram.org
2. Type your phone number with country code (e.g., `+919876543210`) → Click Next
3. Open Telegram on your phone, get the code, and type it on the website → Click Sign In
4. Click **"API development tools"**
5. Fill in the form:
   - App title: `MyMarketingApp`
   - Short name: `myapp1` (5+ letters, no spaces)
   - Platform: `Desktop`
   - Leave URL and Description blank.
6. Click **Create Application**. Copy your `api_id` and `api_hash`.

STEP 5 — Edit `.env` (Your Settings)
1. Right-click on `.env` → Open with Notepad
2. Paste your credentials and settings like this:
```env
API_ID=12345678
API_HASH=abc123def456
PHONE=+919876543210
SESSION_NAME=marketing_session
MIN_DELAY=1800
MAX_DELAY=3600
MAX_POSTS_PER_DAY=300