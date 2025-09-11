from telethon import TelegramClient, events
import httpx
import re
import asyncio

# ================== CONFIG ==================
API_ID = 25777114
API_HASH = "83d41274e41d8330fc83876fb499432b"

BOT_TOKEN = "8322952231:AAEN1_emKlD9BDajTcDodAapLgtNXe_8qUs"
API_URL = "https://rolexxbhaiyaa.great-site.net/index.php"
API_KEY = "CHUTPAGLU"

# ================== CLIENT ==================
bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 Number Normalizer
def normalize_number(raw):
    num = raw.replace(" ", "").strip()
    if num.startswith("+91"):
        num = num[3:]
    elif num.startswith("91") and len(num) == 12:
        num = num[2:]
    return num if len(num) == 10 and num.isdigit() else None

# 🔹 Fetch data from API (async httpx)
async def fetch_data(number):
    url = f"{API_URL}?key={API_KEY}&num={number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Termux)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                return f"⚠️ API Error: HTTP {r.status_code}"

            text = r.text.strip()

            # ❌ Remove unwanted lines (Owner line etc.)
            text = re.sub(r"Owner:.*", "", text, flags=re.IGNORECASE)

            return text.strip() if text else None
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ================== BOT HANDLERS ==================

# /start command
@bot.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    await event.reply(
        "👋 Welcome!\n\n"
        "🔍 Just send me a mobile number (with or without +91).\n"
        "Example: `9821932771`\n\n"
        "I will search details for you."
    )

# Handle numbers
@bot.on(events.NewMessage(pattern=r'^\+?\d[\d\s]{9,}$'))
async def number_handler(event):
    raw_num = event.text.strip()
    number = normalize_number(raw_num)

    if not number:
        await event.reply("❌ Invalid number format.")
        return

    await event.reply(f"🔍 Searching data for {number}... Please wait")

    # Fetch data from API
    reply_text = await fetch_data(number)

    if not reply_text:
        await event.reply("⚠️ No data found.")
        return

    # Final clean reply
    await event.reply(f"📱 Mobile Search Result for {number}\n\n{reply_text}")

# ================== START ==================
print("✅ Bot Started with Direct API (httpx + Termux friendly)")
bot.run_until_disconnected()
