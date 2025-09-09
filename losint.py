from telethon import TelegramClient, events, Button
import json
import asyncio

# ================== CONFIG ==================
API_ID = 25777114
API_HASH = "83d41274e41d8330fc83876fb499432b"
BOT_TOKEN = "8322952231:AAEN1_emKlD9BDajTcDodAapLgtNXe_8qUs"

SEARCH_BOT = "@crazy_num_info_bot"

# ================== CLIENTS ==================
bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user = TelegramClient("user_session", API_ID, API_HASH)

async def init_user():
    await user.start()  # Pehli baar OTP maangega
    print("✅ User Account Logged In Successfully")

# 🔹 Ask crazy_num_info_bot
async def query_crazy_bot(number):
    async with user.conversation(SEARCH_BOT, timeout=40) as conv:
        # Step 1 → Send search command
        await conv.send_message(f"🔎 Search {number}")
        first = await conv.get_response()

        # Step 2 → Click "Number Info Search" button
        if first.buttons:
            try:
                await first.click(1)  # 0 = Aadhaar Info, 1 = Number Info
            except:
                return "❌ Could not click button"

        # Step 3 → Wait for "Send Number" prompt
        second = await conv.get_response()
        if "Send Number" not in second.text:
            return "❌ Unexpected response from bot"

        # Step 4 → Send the number without +91
        await conv.send_message(number)
        final = await conv.get_response()

        return final.text if final else "⚠️ No data found"

# ================== HANDLER ==================
@bot.on(events.NewMessage(pattern=r'^\d{10}$'))
async def handler(event):
    number = event.text.strip()
    await event.reply(f"🔍 Searching data for {number}... Please wait")

    data = await query_crazy_bot(number)
    await event.reply(f"📊 Result for {number}:\n\n{data}")

# ================== START ==================
async def main():
    await init_user()
    print("✅ Bot + User Session Started")
    await bot.run_until_disconnected()

with bot:
    bot.loop.run_until_complete(main())
    
