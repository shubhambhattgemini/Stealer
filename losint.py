from telethon import TelegramClient, events
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
    await user.start()  # pehli baar OTP maangega
    print("✅ User Account Logged In Successfully")

# 🔹 Proper Flow Function
async def query_crazy_bot(number):
    async with user.conversation(SEARCH_BOT, timeout=40) as conv:
        # Step 1 → 🔎 Search {number}
        await conv.send_message(f"🔎 Search {number}")
        first = await conv.get_response()

        # Step 2 → click second button (Number Info Search)
        if first.buttons:
            try:
                await first.click(1)  # 0 = Aadhaar, 1 = Number Info
            except:
                return "❌ Button click failed"

        # Step 3 → wait for "Send Number" prompt
        second = await conv.get_response()
        if "Send Number" not in second.text:
            return f"⚠️ Unexpected response: {second.text}"

        # Step 4 → send number (without +91)
        await conv.send_message(number)
        final = await conv.get_response()

        return final.text if final else "⚠️ No data found"

# ================== HANDLER ==================
@bot.on(events.NewMessage(pattern=r'^\d{10}$'))
async def handler(event):
    number = event.text.strip()
    await event.reply(f"🔍 Searching data for {number}... Please wait")

    try:
        data = await query_crazy_bot(number)
        await event.reply(f"📊 Result for {number}:\n\n{data}")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# ================== START ==================
async def main():
    await init_user()
    print("✅ Bot + User Session Started")
    await bot.run_until_disconnected()

with bot:
    bot.loop.run_until_complete(main())
    
