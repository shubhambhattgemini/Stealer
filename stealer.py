from telethon import TelegramClient, events
import re, random

# ================== CONFIG ==================
API_ID = 25777114
API_HASH = "83d41274e41d8330fc83876fb499432b"
PHONE_NUMBER = "+919908262004"

# 👇 Ab 3 groups se steal hoga
SOURCE_GROUPS = [-1002710317388, -1002757008250, -1001739402223]
TARGET_GROUP = -1002882603089

OWNER_ID = 7835198116
BOT_NAME = "⏤͟͞𝗖𝘆𝗿𝗲𝗼𝗖𝗖𝗦𝘁𝗲𝗮𝗹𝗲𝗿⌁ 💸"

GATES = ["/ho", "/pain", "/le", "/lw"]
# =============================================

seen = set()
running = False

client = TelegramClient("cyreo_cc_stealer", API_ID, API_HASH)

# --- Extractor ---
def extract_combos(text):
    results = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        # Case 1: "Card: CC|MM|YY|CVV"
        card_pattern = r'Card:\s*(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})'
        matches1 = re.findall(card_pattern, line, re.IGNORECASE)

        # Case 2: "CC|MM|YY|CVV"
        simple_pattern = r'(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})'
        matches2 = re.findall(simple_pattern, line)

        for ccnum, month, year, cvv in matches1 + matches2:
            month = month.zfill(2)
            year = year[-2:]
            combo = f"{ccnum}|{month}|{year}|{cvv}"
            if combo not in seen:
                seen.add(combo)
                results.append(combo)

    return results

# --- Commands ---
@client.on(events.NewMessage(pattern=r'/start stealer'))
async def start_stealer(event):
    global running
    if event.sender_id != OWNER_ID:
        await event.reply("❌ You are not authorized.")
        return
    running = True
    await event.reply(f"✅ {BOT_NAME} started! Extracting 'Card:' combos now.")

@client.on(events.NewMessage(pattern=r'/stop stealer'))
async def stop_stealer(event):
    global running
    if event.sender_id != OWNER_ID:
        await event.reply("❌ You are not authorized.")
        return
    running = False
    await event.reply(f"🛑 {BOT_NAME} stopped! No more combos will be extracted.")

# --- Handler ---
@client.on(events.NewMessage(chats=SOURCE_GROUPS))
async def handler(event):
    global running
    if not running:
        return
    text = event.raw_text
    combos = extract_combos(text)

    for combo in combos:
        gate = random.choice(GATES)   # random gate assign
        msg = f"{BOT_NAME}\n{gate} {combo}"
        await client.send_message(TARGET_GROUP, msg)
        print(f"Forwarded with {gate}:", msg)

# --- Main ---
async def main():
    print(f"Starting {BOT_NAME}...")
    await client.start(PHONE_NUMBER)
    print("Bot ready. Use /start stealer to begin.")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
