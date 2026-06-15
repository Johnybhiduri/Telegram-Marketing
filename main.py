"""
╔══════════════════════════════════════════════════════════════════╗
║     TELEGRAM MARKETING AUTOMATION — main.py                     ║
║     Uses Telethon (MTProto) — posts as your user account        ║
║     Python 3.11+  |  pip install telethon                       ║
╚══════════════════════════════════════════════════════════════════╝

HOW IT WORKS:
  1. Logs in as your Telegram account (one-time phone verification)
  2. Pre-loads all your group entities from config.py
  3. Starts a loop:
       - Shuffles the group list randomly
       - Picks one group at a time
       - Picks a random message template
       - Posts it
       - Waits a random time (MIN_DELAY to MAX_DELAY from config)
       - Moves to the next group
       - When all groups have been posted to, starts a new round
  4. Handles all Telegram errors gracefully (FloodWait, slow mode, etc.)
  5. Saves a rotating log file in the logs/ folder
"""

import asyncio
import random
import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from telethon import TelegramClient, errors

import config
import templates


# ─────────────────────────────────────────────────────────────────
#  LOGGER SETUP
#  Logs appear in the terminal AND saved to logs/marketing.log
#  Rotates automatically at 5 MB, keeps 5 old files
# ─────────────────────────────────────────────────────────────────
def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("TGMarketing")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    fh = RotatingFileHandler(
        os.path.join("logs", "marketing.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

log = setup_logger()


# ─────────────────────────────────────────────────────────────────
#  MAIN MARKETER CLASS
# ─────────────────────────────────────────────────────────────────
class TelegramMarketer:

    def __init__(self):
        self.client = TelegramClient(
            config.SESSION_NAME,
            config.API_ID,
            config.API_HASH,
            device_model=config.DEVICE_MODEL,
            system_version=config.SYSTEM_VERSION,
            app_version=config.APP_VERSION,
        )
        # Telethon will automatically sleep on FloodWait errors
        # up to this many seconds (longer ones are raised as exceptions)
        self.client.flood_sleep_threshold = 60

        # Cache of group_identifier → Telegram entity object
        # (avoids repeated API calls to look up the same group)
        self.group_cache: dict = {}

        # Groups that failed permanently this session (no permission, banned, etc.)
        # These are automatically removed so we don't keep retrying them
        self.skip_groups: set = set()

        # Running statistics
        self.stats = {
            "sent"           : 0,
            "failed"         : 0,
            "flood_waits"    : 0,
            "posts_today"    : 0,
            "day_started"    : datetime.now().date(),
            "session_started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # ──────────────────────────────────────────────────────────────
    #  CONNECT & LOGIN
    # ──────────────────────────────────────────────────────────────
    async def connect(self):
        log.info("=" * 62)
        log.info("  TELEGRAM MARKETING BOT  —  Starting Up")
        log.info("=" * 62)

        # start() handles login automatically:
        # - First time: asks for phone → OTP → logs in → saves session file
        # - After that: loads session file silently (no prompt needed)
        await self.client.start(phone=config.PHONE)

        me = await self.client.get_me()
        log.info(f"✅ Logged in as   : {me.first_name} (ID: {me.id})")
        log.info(f"📱 Phone           : +{me.phone}")
        log.info(f"📋 Groups in config: {len(config.GROUPS)}")
        log.info(f"📝 Templates loaded: {len(templates.TEMPLATES)}")
        log.info(f"⏱️  Delay range     : {config.MIN_DELAY // 60}–{config.MAX_DELAY // 60} minutes")
        log.info(f"📅 Daily post cap  : {config.MAX_POSTS_PER_DAY}")
        log.info("=" * 62)

    # ──────────────────────────────────────────────────────────────
    #  PRE-CACHE ALL GROUP ENTITIES
    #
    #  Calling get_entity() for every message would burn through
    #  your API quota fast. We call it ONCE per group at startup
    #  and cache the result. Much safer.
    # ──────────────────────────────────────────────────────────────
    async def cache_groups(self) -> list:
        log.info(f"🔄 Resolving {len(config.GROUPS)} groups — please wait ...")
        log.info("─" * 62)
        valid = []

        for gid in config.GROUPS:
            try:
                entity = await self.client.get_entity(gid)
                name   = getattr(entity, "title", str(gid))
                self.group_cache[gid] = entity
                valid.append(gid)
                log.info(f"  ✅  {name}")

            except errors.FloodWaitError as e:
                # Telegram told us to wait — respect it fully
                wait = e.seconds + random.randint(5, 20)
                log.warning(f"  ⚠️  FloodWait {e.seconds}s on resolve — sleeping {wait}s ...")
                await asyncio.sleep(wait)
                # Retry once after sleeping
                try:
                    entity = await self.client.get_entity(gid)
                    self.group_cache[gid] = entity
                    valid.append(gid)
                    log.info(f"  ✅  {getattr(entity, 'title', gid)}  (retry OK)")
                except Exception as ex:
                    log.error(f"  ❌  {gid}  →  {type(ex).__name__}: {ex}")

            except Exception as e:
                log.error(f"  ❌  {gid}  →  {type(e).__name__}: {e}")

            # Small pause between lookups — polite to the API
            await asyncio.sleep(random.uniform(1.5, 3.5))

        log.info("─" * 62)
        log.info(f"✅ Successfully resolved {len(valid)}/{len(config.GROUPS)} groups")
        log.info("─" * 62)
        return valid

    # ──────────────────────────────────────────────────────────────
    #  DAILY COUNTER RESET
    #  Called at the top of every loop iteration
    # ──────────────────────────────────────────────────────────────
    def _check_daily_reset(self):
        today = datetime.now().date()
        if self.stats["day_started"] != today:
            log.info(
                f"📅 New day started — "
                f"resetting daily counter (was {self.stats['posts_today']})"
            )
            self.stats["posts_today"] = 0
            self.stats["day_started"] = today

    # ──────────────────────────────────────────────────────────────
    #  SEND ONE MESSAGE TO ONE GROUP
    #  Returns True if sent successfully, False otherwise.
    #  All Telegram errors are handled here — the loop never crashes.
    # ──────────────────────────────────────────────────────────────
    async def send(self, gid: str, message: str) -> bool:
        entity = self.group_cache.get(gid)
        name   = getattr(entity, "title", str(gid)) if entity else str(gid)

        try:
            if entity is None:
                entity = await self.client.get_entity(gid)
                self.group_cache[gid] = entity
                name = getattr(entity, "title", str(gid))

            await self.client.send_message(entity, message, parse_mode="md")

            self.stats["sent"] += 1
            self.stats["posts_today"] += 1
            log.info(
                f"✅ Sent → '{name}'  |  "
                f"total: {self.stats['sent']}  |  "
                f"today: {self.stats['posts_today']}"
            )
            return True

        # ── RECOVERABLE: Too many requests ────────────────────────
        except errors.FloodWaitError as e:
            self.stats["flood_waits"] += 1
            extra = random.randint(15, 60)
            total  = e.seconds + extra
            log.warning(
                f"⚠️  FloodWait {e.seconds}s on '{name}' — "
                f"sleeping {total}s (base + {extra}s safety buffer)"
            )
            await asyncio.sleep(total)
            return False

        # ── RECOVERABLE: Group has slow-mode active ────────────────
        except errors.SlowModeWaitError as e:
            log.warning(
                f"⏳ SlowMode: must wait {e.seconds}s before "
                f"next message in '{name}' — skipping this turn"
            )
            return False

        # ── PERMANENT: No write permission ────────────────────────
        except errors.ChatWriteForbiddenError:
            log.error(f"🚫 Write not permitted in '{name}' — removing from session list")
            self.skip_groups.add(gid)
            return False

        # ── PERMANENT: You were banned from this group ────────────
        except errors.UserBannedInChannelError:
            log.error(f"🚫 You are banned in '{name}' — removing from session list")
            self.skip_groups.add(gid)
            return False

        # ── PERMANENT: Only admins can post ───────────────────────
        except errors.ChatAdminRequiredError:
            log.error(f"🚫 Admin-only in '{name}' — removing from session list")
            self.skip_groups.add(gid)
            return False

        # ── DANGER: Account-level spam flag ───────────────────────
        #    This means Telegram noticed unusual activity on your account.
        #    We stop everything for 2 hours to let it cool down.
        except errors.PeerFloodError:
            log.critical(
                "🚨 PeerFloodError — Telegram flagged this account for heavy activity!\n"
                "   Pausing ALL posting for 2 hours to protect the account.\n"
                "   This is normal if you just started or recently sent many messages.\n"
                "   The bot will resume automatically after the pause."
            )
            self.stats["flood_waits"] += 1
            await asyncio.sleep(2 * 3600)  # 2 hours
            return False

        # ── CATCH-ALL: Any other unexpected error ─────────────────
        except Exception as e:
            self.stats["failed"] += 1
            log.error(f"❌ Unexpected error on '{name}': {type(e).__name__}: {e}")
            return False

    # ──────────────────────────────────────────────────────────────
    #  MAIN MARKETING LOOP
    #  This runs forever until you press Ctrl+C
    # ──────────────────────────────────────────────────────────────
    async def run(self):
        valid_groups = await self.cache_groups()

        if not valid_groups:
            log.error(
                "❌ No valid groups found!\n"
                "   Open config.py and check your GROUPS list.\n"
                "   Make sure you are a member of every group listed."
            )
            return

        log.info(f"🚀 Bot is running! Starting marketing loop ...")

        queue: list = []
        round_num   = 0

        while True:
            # ── 1. Reset daily counter if it's a new day ──────────
            self._check_daily_reset()

            # ── 2. Check daily cap ────────────────────────────────
            if self.stats["posts_today"] >= config.MAX_POSTS_PER_DAY:
                now      = datetime.now()
                midnight = datetime.combine(
                    now.date() + timedelta(days=1),
                    datetime.min.time()
                )
                wait_secs = int((midnight - now).total_seconds()) + random.randint(120, 600)
                wake_at   = (now + timedelta(seconds=wait_secs)).strftime("%H:%M")
                log.info(
                    f"📅 Daily cap ({config.MAX_POSTS_PER_DAY} posts) reached. "
                    f"Sleeping until ~{wake_at} ..."
                )
                await asyncio.sleep(wait_secs)
                continue

            # ── 3. Remove groups that permanently failed ──────────
            active = [g for g in valid_groups if g not in self.skip_groups]

            if not active:
                log.error(
                    "❌ Every group in your list has been removed due to errors.\n"
                    "   Check the logs and update config.py with working groups."
                )
                break

            # ── 4. Refill queue when empty (start new round) ──────
            if not queue:
                round_num += 1
                queue = active.copy()
                random.shuffle(queue)   # ← randomises the posting order

                log.info("─" * 62)
                log.info(
                    f"🔄 Round {round_num} starting — "
                    f"{len(queue)} groups | "
                    f"in random order"
                )
                log.info("─" * 62)

                # Between rounds: wait one full delay period
                # so consecutive rounds don't look like rapid-fire posting
                if round_num > 1:
                    cooldown = random.randint(config.MIN_DELAY, config.MAX_DELAY)
                    wake_at  = (datetime.now() + timedelta(seconds=cooldown)).strftime("%H:%M:%S")
                    log.info(
                        f"☕ Inter-round break: "
                        f"{cooldown // 60}m {cooldown % 60}s "
                        f"(resuming at ~{wake_at})"
                    )
                    await asyncio.sleep(cooldown)
                    continue   # recheck daily cap after cooldown

            # ── 5. Pick next group from the shuffled queue ────────
            gid = queue.pop(0)
            if gid in self.skip_groups:
                continue    # silently skip failed groups

            # ── 6. Pick a random message template ─────────────────
            msg = random.choice(templates.TEMPLATES)

            name = getattr(self.group_cache.get(gid), "title", str(gid))
            log.info(f"📤 Target  : {name}")
            log.info(
                f"📝 Preview : "
                f"{msg[:70].strip().replace(chr(10), ' ')} ..."
            )

            # ── 7. Send it ────────────────────────────────────────
            await self.send(gid, msg)

            log.info(
                f"📊 Stats — "
                f"sent: {self.stats['sent']} | "
                f"today: {self.stats['posts_today']} | "
                f"failed: {self.stats['failed']} | "
                f"flood_waits: {self.stats['flood_waits']} | "
                f"skipped_groups: {len(self.skip_groups)}"
            )

            # ── 8. Wait random time before next post ──────────────
            if queue:
                delay  = random.randint(config.MIN_DELAY, config.MAX_DELAY)
                wake   = (datetime.now() + timedelta(seconds=delay)).strftime("%H:%M:%S")
                log.info(
                    f"⏰ Next post in {delay // 60}m {delay % 60}s "
                    f"— at {wake}  |  {len(queue)} left in round"
                )
                await asyncio.sleep(delay)

    # ──────────────────────────────────────────────────────────────
    async def disconnect(self):
        await self.client.disconnect()
        log.info("👋 Disconnected from Telegram.")
        log.info(f"📊 Session stats: {self.stats}")


# ─────────────────────────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────────────────────────
async def main():
    marketer = TelegramMarketer()
    try:
        await marketer.connect()
        await marketer.run()
    except KeyboardInterrupt:
        log.info("🛑 Stopped by user (Ctrl+C)")
    except Exception as e:
        log.critical(
            f"💥 Fatal unhandled exception: {type(e).__name__}: {e}",
            exc_info=True
        )
    finally:
        await marketer.disconnect()


if __name__ == "__main__":
    asyncio.run(main())