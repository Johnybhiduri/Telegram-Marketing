"""
╔══════════════════════════════════════════════════════════════════╗
║     TELEGRAM MARKETING AUTOMATION — main.py                     ║
║     Uses Telethon (MTProto) — posts as your user account        ║
║     Python 3.11+  |  pip install telethon python-dotenv          ║
╚══════════════════════════════════════════════════════════════════╝
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

# ─────────────────────────────────────────────────────────────────
# LOGGER SETUP
# ─────────────────────────────────────────────────────────────────
def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("TGMarketing")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    fh = RotatingFileHandler(os.path.join("logs", "marketing.log"), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

log = setup_logger()

# ─────────────────────────────────────────────────────────────────
# MAIN MARKETER CLASS
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
        self.client.flood_sleep_threshold = 60
        self.group_cache: dict = {}
        self.skip_groups: set = set()
        
        # Cyclical group tracking
        self.current_group_idx = 0
        self.round_num = 0

        self.stats = {
            "sent": 0,
            "failed": 0,
            "flood_waits": 0,
            "posts_today": 0,
            "day_started": datetime.now().date(),
            "session_started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    async def connect(self):
        log.info("=" * 62)
        log.info("  TELEGRAM MARKETING BOT  —  Starting Up")
        log.info("=" * 62)
        await self.client.start(phone=config.PHONE)
        me = await self.client.get_me()
        log.info(f"✅ Logged in as   : {me.first_name} (ID: {me.id})")
        log.info(f"📱 Phone           : +{me.phone}")
        log.info(f"📋 Groups loaded   : {len(config.GROUPS)}")
        log.info(f"📝 Templates loaded: {len(config.TEMPLATES)}")
        log.info(f"⏱️  Delay range     : {config.MIN_DELAY // 60}m {config.MIN_DELAY % 60}s – {config.MAX_DELAY // 60}m {config.MAX_DELAY % 60}s")
        log.info(f"📅 Daily post cap  : {config.MAX_POSTS_PER_DAY}")
        log.info("=" * 62)

    async def cache_groups(self) -> list:
        log.info(f"🔄 Resolving {len(config.GROUPS)} groups — please wait...")
        log.info("-" * 62)
        valid = []

        for gid in config.GROUPS:
            try:
                entity = await self.client.get_entity(gid)
                name = getattr(entity, "title", str(gid))
                self.group_cache[gid] = entity
                valid.append(gid)
                log.info(f"  ✅  {name}")
            except errors.FloodWaitError as e:
                wait = e.seconds + random.randint(5, 20)
                log.warning(f"  ⚠️  FloodWait {e.seconds}s on resolve — sleeping {wait}s...")
                await asyncio.sleep(wait)
                try:
                    entity = await self.client.get_entity(gid)
                    self.group_cache[gid] = entity
                    valid.append(gid)
                    log.info(f"  ✅  {getattr(entity, 'title', gid)} (retry OK)")
                except Exception as ex:
                    log.error(f"  ❌  {gid}  →  {type(ex).__name__}: {ex}")
            except Exception as e:
                log.error(f"  ❌  {gid}  →  {type(e).__name__}: {e}")
            await asyncio.sleep(random.uniform(1.5, 3.5))

        log.info("-" * 62)
        log.info(f"✅ Successfully resolved {len(valid)}/{len(config.GROUPS)} groups")
        log.info("-" * 62)
        return valid

    def _check_daily_reset(self):
        today = datetime.now().date()
        if self.stats["day_started"] != today:
            log.info(f"📅 New day started — resetting daily counter (was {self.stats['posts_today']})")
            self.stats["posts_today"] = 0
            self.stats["day_started"] = today

    async def send(self, gid: str, template_data: dict) -> bool:
        entity = self.group_cache.get(gid)
        name = getattr(entity, "title", str(gid)) if entity else str(gid)
        text = template_data["text"]
        image = template_data["image"]

        try:
            if entity is None:
                entity = await self.client.get_entity(gid)
                self.group_cache[gid] = entity
                name = getattr(entity, "title", str(gid))

            # Send with image if provided and exists, otherwise text only
            if image and os.path.exists(image):
                await self.client.send_file(entity, file=image, caption=text, parse_mode="md")
            else:
                if image:
                    log.warning(f"  ⚠️ Image '{image}' not found. Sending text only.")
                await self.client.send_message(entity, text, parse_mode="md")

            self.stats["sent"] += 1
            self.stats["posts_today"] += 1
            log.info(f"✅ Sent → '{name}' | total: {self.stats['sent']} | today: {self.stats['posts_today']}")
            return True

        # ── FALLBACK: Group doesn't allow photos/media ──────────
        except errors.ChatSendPhotosForbiddenError:
            log.warning(f"⚠️ Photos/Media not allowed in '{name}'. Retrying with text only...")
            try:
                await self.client.send_message(entity, text, parse_mode="md")
                self.stats["sent"] += 1
                self.stats["posts_today"] += 1
                log.info(f"✅ Sent (text-only fallback) → '{name}'")
                return True
            except Exception as e2:
                log.error(f"❌ Text-only fallback also failed: {e2}")
                return False

        except errors.FloodWaitError as e:
            self.stats["flood_waits"] += 1
            total = e.seconds + random.randint(15, 60)
            log.warning(f"⚠️  FloodWait {e.seconds}s on '{name}' — sleeping {total}s")
            await asyncio.sleep(total)
            return False
        except errors.SlowModeWaitError as e:
            log.warning(f"⏳ SlowMode: must wait {e.seconds}s in '{name}' — skipping")
            return False
        except errors.ChatWriteForbiddenError:
            log.error(f"🚫 Write not permitted in '{name}' — removing from session")
            self.skip_groups.add(gid)
            return False
        except errors.UserBannedInChannelError:
            log.error(f"🚫 You are banned in '{name}' — removing from session")
            self.skip_groups.add(gid)
            return False
        except errors.ChatAdminRequiredError:
            log.error(f"🚫 Admin-only in '{name}' — removing from session")
            self.skip_groups.add(gid)
            return False
        except errors.PeerFloodError:
            log.critical("🚨 PeerFloodError — Pausing ALL posting for 2 hours to protect the account.")
            self.stats["flood_waits"] += 1
            await asyncio.sleep(2 * 3600)
            return False
        except Exception as e:
            self.stats["failed"] += 1
            log.error(f"❌ Unexpected error on '{name}': {type(e).__name__}: {e}")
            return False

    async def run(self):
        valid_groups = await self.cache_groups()
        if not valid_groups:
            log.error("❌ No valid groups found! Check groups.txt")
            return

        log.info("🚀 Bot is running! Starting marketing loop...")

        while True:
            self._check_daily_reset()

            if self.stats["posts_today"] >= config.MAX_POSTS_PER_DAY:
                now = datetime.now()
                midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
                wait_secs = int((midnight - now).total_seconds()) + random.randint(120, 600)
                log.info(f"📅 Daily cap reached. Sleeping until ~{(now + timedelta(seconds=wait_secs)).strftime('%H:%M')}...")
                await asyncio.sleep(wait_secs)
                continue

            active = [g for g in valid_groups if g not in self.skip_groups]
            if not active:
                log.error("❌ Every group has been removed due to errors. Check logs.")
                break

            # Cyclical order logic
            if self.current_group_idx == 0:
                self.round_num += 1
                log.info("-" * 62)
                log.info(f"🔄 Round {self.round_num} starting — {len(active)} groups in cyclical order")
                log.info("-" * 62)
                
                # Inter-round break (only if we have more than 1 group to form a "round")
                if self.round_num > 1 and len(active) > 1:
                    cooldown = random.randint(config.MIN_DELAY, config.MAX_DELAY)
                    wake_at = (datetime.now() + timedelta(seconds=cooldown)).strftime("%H:%M:%S")
                    log.info(f"☕ Inter-round break: {cooldown // 60}m {cooldown % 60}s (resuming at ~{wake_at})")
                    await asyncio.sleep(cooldown)
                    # ⚠️ BUG FIX: Removed the 'continue' statement that was here.
                    # If we 'continue', it loops back to the top, sees index is still 0, 
                    # and starts Round 3 immediately without posting!

            # Pick the next group in the cycle
            gid = active[self.current_group_idx]
            self.current_group_idx = (self.current_group_idx + 1) % len(active)

            # Pick a RANDOM template (as requested)
            template_data = random.choice(config.TEMPLATES)
            name = getattr(self.group_cache.get(gid), "title", str(gid))
            
            log.info(f"📤 Target  : {name}")
            log.info(f"📝 Preview : {template_data['text'][:70].strip().replace(chr(10), ' ')}...")

            await self.send(gid, template_data)

            log.info(f"📊 Stats — sent: {self.stats['sent']} | today: {self.stats['posts_today']} | failed: {self.stats['failed']} | flood_waits: {self.stats['flood_waits']}")

            # Standard delay between EVERY post
            delay = random.randint(config.MIN_DELAY, config.MAX_DELAY)
            wake = (datetime.now() + timedelta(seconds=delay)).strftime("%H:%M:%S")
            log.info(f"⏰ Next post in {delay // 60}m {delay % 60}s — at {wake}")
            await asyncio.sleep(delay)

    async def disconnect(self):
        await self.client.disconnect()
        log.info("👋 Disconnected from Telegram.")
        log.info(f"📊 Session stats: {self.stats}")

# ─────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────
async def main():
    marketer = TelegramMarketer()
    try:
        await marketer.connect()
        await marketer.run()
    except KeyboardInterrupt:
        log.info("🛑 Stopped by user (Ctrl+C)")
    except Exception as e:
        log.critical(f"💥 Fatal unhandled exception: {type(e).__name__}: {e}", exc_info=True)
    finally:
        await marketer.disconnect()

if __name__ == "__main__":
    asyncio.run(main())