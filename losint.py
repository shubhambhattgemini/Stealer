from telethon import TelegramClient, events
import asyncio
import re

# ================== CONFIG ==================
API_ID = 25777114
API_HASH = "83d41274e41d8330fc83876fb499432b"

BOT_TOKEN = "8322952231:AAEN1_emKlD9BDajTcDodAapLgtNXe_8qUs"
SEARCH_BOT = "@h4ckerosint_bot"   # 👈 Using new bot

# ================== CLIENTS ==================
bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user = TelegramClient("user_session", API_ID, API_HASH)  # OTP login hoga

# 🔹 Ensure user login once
async def init_user():
    await user.start()  # pehli baar OTP puchega
    print("✅ User Account Logged In Successfully")

# 🔹 Number Normalizer
def normalize_number(raw):
    num = raw.replace(" ", "").strip()
    if num.startswith("+91"):
        num = num[3:]
    elif num.startswith("91") and len(num) == 12:
        num = num[2:]
    return num if len(num) == 10 and num.isdigit() else None

# 🔹 Ask other bot using USER account
async def ask_search_bot(query):
    async with user.conversation(SEARCH_BOT, timeout=30) as conv:
        await conv.send_message(query)
        # wait for bot animation delay
        await asyncio.sleep(6)
        resp = await conv.get_response()
        text = resp.text.strip()

        # ❌ Remove Status + Owner lines
        text = re.sub(r"⚡ STATUS:.*", "", text, flags=re.DOTALL)
        text = re.sub(r"Owner:.*", "", text, flags=re.DOTALL)
        return text.strip()

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

    # Step 1: Ask for /num
    reply_text = await ask_search_bot(f"/num {number}")

    if not reply_text:
        await event.reply("⚠️ No data found.")
        return

    # Final clean reply
    await event.reply(f"📱 Mobile Search Result for {number}\n\n{reply_text}")

# ================== START ==================
async def main():
    await init_user()  # OTP login yahin hoga
    print("✅ Bot + User Session Started")
    await bot.run_until_disconnected()

with bot:
    bot.loop.run_until_complete(main())
    
