# 📢 Telegram Marketing Bot
### Automatically posts your message to Telegram groups — so you don't have to do it manually.

---

## 📁 Files in This Folder

| File | What it is |
|---|---|
| `main.py` | The bot — do not touch this |
| `config.py` | ✏️ **You edit this** — your API keys + group list |
| `templates.py` | ✏️ **You edit this** — your marketing messages |
| `requirements.txt` | Do not touch |
| `run.bat` | Double-click this to start the bot |

---

## ✅ BEFORE YOU START — Things You Need

- A Windows laptop/PC that stays ON
- Telegram account (already on your phone)
- Internet connection
- 15 minutes to set up (only once)

---

# STEP 1 — Install Python

1. Go to 👉 **https://python.org/downloads**
2. Click the big yellow **Download Python** button
3. Open the downloaded file
4. ⚠️ **VERY IMPORTANT** — Before clicking Install, tick the box that says **"Add Python to PATH"**

   ![Tick the checkbox at the bottom of the installer screen]

5. Click **Install Now**
6. Wait for it to finish → Click **Close**

**Check it worked:**
- Press `Windows key + R` on keyboard
- Type `cmd` → press **Enter** (a black window opens)
- Type `python --version` → press **Enter**
- You should see something like `Python 3.12.4` ✅
- If you see an error — reinstall Python and make sure to tick the PATH checkbox

---

# STEP 2 — Set Up the Project Folder

1. Create a new folder on your Desktop called `telegram_marketing`
2. Put all 5 downloaded files into that folder

Your folder should look like this:
```
telegram_marketing/
  ├── main.py
  ├── config.py
  ├── templates.py
  ├── requirements.txt
  └── run.bat
```

---

# STEP 3 — Install the Required Library

1. Press `Windows key + R` → type `cmd` → press **Enter**
2. Type this exactly and press **Enter**:
   ```
   cd Desktop\telegram_marketing
   ```
3. Then type this and press **Enter**:
   ```
   pip install -r requirements.txt
   ```
4. Wait for it to finish downloading
5. You'll see **"Successfully installed telethon"** when done ✅

---

# STEP 4 — Get Your Telegram API ID and Hash

> This is a free one-time process. Takes about 3 minutes.

**4a.** Open **Google Chrome** (not Brave, not Edge — use Chrome)

**4b.** Go to 👉 **https://my.telegram.org**

**4c.** Type your phone number with country code
- India example: `+919876543210`
- Click **Next**

**4d.** Open **Telegram on your phone**
- You'll receive a message from "Telegram" with a code
- Type that code on the website → Click **Sign In**

**4e.** Click **"API development tools"**

**4f.** Fill in the form:
- **App title:** type anything — example: `MyMarketingApp`
- **Short name:** type anything (5+ letters, no spaces) — example: `myapp1`
- **URL:** leave blank
- **Platform:** select **Desktop**
- **Description:** leave blank
- Click **Create Application**

**4g.** You will now see your credentials on screen:
```
App api_id:    12345678
App api_hash:  abc123def456...
```

📋 **Copy both of these — you will paste them in the next step**

> ⚠️ Keep these private. Anyone with your api_id and hash can access your account.

---

# STEP 5 — Edit config.py (Your Settings)

1. Go to your `telegram_marketing` folder
2. Right-click on **config.py** → Open with **Notepad**
3. Edit these lines at the top:

```python
API_ID   = 12345678          # Paste your api_id here (just the number, no quotes)
API_HASH = "abc123def456"    # Paste your api_hash here (keep the " " quotes)
PHONE    = "+919876543210"   # Your Telegram phone number with country code
```

**Now add your groups:**

Scroll down to the `GROUPS` section and add your group usernames:

```python
GROUPS = [
    "pune_marketplace",        # Group username without @
    "india_buy_sell",
    "maharashtra_business",
    # Add more below...
]
```

**How to find a group's username:**
- Open the group in Telegram
- Tap the group name at the top
- You'll see something like `t.me/pune_marketplace`
- The part after `t.me/` is the username → add that to the list

**If the group has no username (private group):**
- Forward any message from that group to the Telegram bot 👉 **@getidsbot**
- It will reply with a number like `-1001234567890`
- Add that number in quotes: `"-1001234567890"`

**Timing (already set, change only if needed):**
```python
MIN_DELAY = 30 * 60    # Wait at least 30 minutes between posts
MAX_DELAY = 60 * 60    # Wait at most 60 minutes between posts
MAX_POSTS_PER_DAY = 30 # Maximum posts in one day
```

4. Press **Ctrl + S** to save

---

# STEP 6 — Edit templates.py (Your Messages)

1. Right-click on **templates.py** → Open with **Notepad**
2. You will see several message templates
3. Replace the placeholder text with your actual business messages

**Example of a filled-in template:**
```python
"""🚀 *Raj Mobile Shop — Pune*

Looking for mobile accessories at best price?

✅ All brands available
✅ Same day delivery in Pune
✅ Bulk orders welcome

📲 WhatsApp: +919876543210
🌐 www.rajmobile.com""",
```

**Tips:**
- Add at least **6 different messages** — more variety is better
- Each message should sound different from the others
- Include your contact info in every message
- `*bold text*` makes text bold in Telegram
- `_italic text_` makes text italic
- Emojis work — just paste them in directly

4. Press **Ctrl + S** to save

---

# STEP 7 — First Time Login (One Time Only)

1. Open Command Prompt (`Windows + R` → `cmd` → Enter)
2. Type:
   ```
   cd Desktop\telegram_marketing
   ```
3. Type:
   ```
   python main.py
   ```

**The bot will ask for your phone number:**
```
Please enter your phone: 
```
Type your number with country code → press **Enter**
Example: `+919876543210`

**Then it asks for a code:**
```
Please enter the code you received:
```
- Open **Telegram on your phone**
- You got a message from "Telegram" with a 5-digit code
- Type that code → press **Enter**

**If you have 2-Step Verification on:**
```
Please enter your password:
```
Type your Telegram 2FA password → press **Enter**

✅ **Done! The bot is now running.**

You will see it posting to your groups one by one. It shows you exactly which group it posted to and when the next post will happen.

> 📝 A file called `marketing_session.session` is created in your folder. This saves your login. **Never delete this file** or you'll have to log in again.

---

# STEP 8 — Running 24/7 (Every Day)

## First: Stop Windows from Sleeping

1. Click **Start** → **Settings**
2. Go to **System → Power & Sleep**
3. Under **Sleep**, change both dropdowns to **Never**
4. Keep your laptop **plugged into power**

## Then: Start the Bot

Every time you want to run the bot, just:

1. Go to your `telegram_marketing` folder
2. **Double-click `run.bat`**

A black window opens and the bot runs forever.

- ✅ If the bot crashes → it **automatically restarts** in 60 seconds
- ✅ If internet goes out → it **automatically reconnects**
- ✅ If Telegram asks you to slow down → it **automatically waits** and continues
- ⛔ To stop → just **close the window**

---

# 📊 Understanding What You See

The bot shows you live updates:

| What you see | What it means |
|---|---|
| `✅ Sent → 'Group Name'` | Message posted successfully |
| `⏰ Next post in 42m 17s` | Bot is waiting before next post |
| `🔄 Round 2 starting` | Finished all groups, starting again from top |
| `⚠️ FloodWait 30s` | Telegram asked to slow down — bot waited, will continue |
| `🚫 Write not permitted` | That group doesn't allow posting — bot skipped it |
| `📅 Daily cap reached` | Posted 30 times today — sleeping till midnight |

All activity is also saved in the `logs` folder as `marketing.log`

---

# ❗ Common Problems & Fixes

**"python is not recognized"**
→ Reinstall Python. On the first screen, tick **"Add Python to PATH"**

**"No module named telethon"**
→ Open CMD, go to your folder, run: `pip install -r requirements.txt`

**"Cannot find entity for group_name"**
→ The group username is wrong, or you are not a member of that group. Join the group first in Telegram, then try again.

**Bot stops after a few hours**
→ Your laptop went to sleep. Fix: Set Sleep to **Never** in Power Settings (Step 8 above)

**"ERROR" on my.telegram.org**
→ Use Google Chrome (not Brave). Clear cookies. Try again in incognito mode.

**"Incorrect app name" error**
→ Your Short name is less than 5 characters. Make it longer — at least 5 letters.

---

# 🔄 How to Update Later

**Add a new group:**
Open `config.py` in Notepad → add group username to the GROUPS list → save

**Add a new message template:**
Open `templates.py` in Notepad → copy an existing template block → paste below → edit text → save

**Change posting speed:**
Open `config.py` → change `MIN_DELAY` and `MAX_DELAY` (values are in seconds)

---

# 📞 Quick Help Checklist

Before running, make sure:
- [ ] Python installed with PATH ticked
- [ ] `pip install -r requirements.txt` done
- [ ] `config.py` has your real API_ID, API_HASH, PHONE
- [ ] `config.py` has your groups listed
- [ ] `templates.py` has your real marketing messages
- [ ] You are a member of every group in your list
- [ ] Laptop sleep is set to Never
- [ ] Laptop is plugged in to power

**To start every day:** Double-click `run.bat` ✅