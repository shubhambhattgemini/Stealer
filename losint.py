from telethon import TelegramClient, events
import json
import asyncio

# ================== CONFIG ==================
API_ID = 25777114
API_HASH = "83d41274e41d8330fc83876fb499432b"

BOT_TOKEN = "8322952231:AAEN1_emKlD9BDajTcDodAapLgtNXe_8qUs"
SEARCH_BOT = "@RolexxOsint_bot"

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

# 🔹 Format JSON into text
def format_data(data):
    lines = []
    for d in data:
        mobile = d.get("mobile", "N/A")
        name = d.get("name", "N/A")
        fname = d.get("fname", "N/A")
        address = d.get("address", "N/A").replace("!", ", ")
        circle = d.get("circle", "N/A")
        lines.append(
            f"📱 {mobile} | {circle}\n"
            f"👤 {name} | 👨‍👦 {fname}\n"
            f"🏠 {address}\n"
        )
    return "\n──────────────\n".join(lines)

# 🔹 Ask other bot using USER account
async def ask_search_bot(query):
    async with user.conversation(SEARCH_BOT, timeout=20) as conv:
        await conv.send_message(query)
        resp = await conv.get_response()
        try:
            js = json.loads(resp.text)
            return js
        except:
            return None

# ================== BOT HANDLER ==================
@bot.on(events.NewMessage(pattern=r'^\+?\d[\d\s]{9,}$'))
async def handler(event):
    raw_num = event.text.strip()
    number = normalize_number(raw_num)

    if not number:
        await event.reply("❌ Invalid number format.")
        return

    await event.reply(f"🔍 Searching data for {number}... Please wait")

    # Step 1: Ask for /num
    js1 = await ask_search_bot(f"/num {number}")
    if not js1 or "data" not in js1:
        await event.reply("⚠️ No data found.")
        return

    num_data = js1["data"]
    aadhaar_id = None
    if num_data and "id" in num_data[0]:
        aadhaar_id = num_data[0]["id"]

    # Step 2: Aadhaar Linked Numbers
    aadhaar_data = []
    if aadhaar_id:
        js2 = await ask_search_bot(f"/aadhar {aadhaar_id}")
        if js2 and "data" in js2:
            aadhaar_data = js2["data"]

    # Step 3: Merge + Format
    reply_text = f"📱 Mobile Search Result for {number}\n\n"
    reply_text += format_data(num_data)

    if aadhaar_data:
        reply_text += "\n\n──────────────\n🪪 Aadhaar Linked Numbers:\n\n"
        reply_text += format_data(aadhaar_data)

    await event.reply(reply_text)

# ================== START ==================
async def main():
    await init_user()  # OTP login yahin hoga
    print("✅ Bot + User Session Started")
    await bot.run_until_disconnected()

with bot:
    bot.loop.run_until_complete(main())
    
