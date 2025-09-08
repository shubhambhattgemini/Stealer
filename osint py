import logging
import re
import requests
import pytz
import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Config ---
BOT_TOKEN = '8322952231:AAEN1_emKlD9BDajTcDodAapLgtNXe_8qUs'
OWNER_ID = 7835198116

API_URL = "https://leakosintapi.com/"
api_token = "7990562228:dgSYJ2xK"   # default token

# --- Data Stores ---
user_credits = {}
referred_users = set()

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Normalize Query ---
def clean_input(text):
    text = text.strip().replace(" ", "").replace("-", "")
    match = re.match(r"^(?:\+91|91)?(\d{10})$", text)
    if match:
        return match.group(1)
    return text

# --- Keyboards ---
main_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔍 Search", callback_data="search"),
        InlineKeyboardButton("💰 Balance", callback_data="balance")
    ],
    [
        InlineKeyboardButton("💸 Add Funds", callback_data="add_funds"),
        InlineKeyboardButton("💎 Referral", callback_data="referral")
    ],
    [
        InlineKeyboardButton("🔐 Contact Admin", url="https://t.me/Cyreo")
    ]
])

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    args = context.args

    if uid not in user_credits:
        user_credits[uid] = 5

    if args and args[0].startswith("ref_"):
        ref_id = int(args[0][4:])
        if ref_id != uid and ref_id in user_credits and uid not in referred_users:
            user_credits[ref_id] += 5
            referred_users.add(uid)
            try:
                await context.bot.send_message(ref_id, f"✨ You got 5 coins from referral! New balance: {user_credits[ref_id]}")
            except:
                pass

    await update.message.reply_text(
        "🕵️ I can look for almost everything. Just send me your request.",
        reply_markup=main_keyboard
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if query.data == "search":
        await query.message.reply_text(
            "📨 Send phone number, email, username, IP, domain, or social profile to search.\n\n"
            "💸 Each search costs 5 coins."
        )

    elif query.data == "balance":
        coins = user_credits.get(uid, 0)
        await query.message.reply_text(f"💰 Your balance: {coins} coins")

    elif query.data == "add_funds":
        await query.message.reply_text(
            "💸 <b>Pricing List</b>\n"
            "━━━━━━━━━━━━━━\n"
            "🔍 1 Search = 5 Coins\n\n"
            "• 100 Coins — ₹100\n"
            "• 250 Coins — ₹250\n"
            "• 500 Coins — ₹500\n"
            "━━━━━━━━━━━━━━\n"
            "📩 Contact @Cyreo to top-up.",
            parse_mode='HTML'
        )

    elif query.data == "referral":
        bot_info = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start=ref_{uid}"
        await query.message.reply_text(
            f"💎 <b>Referral Program</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎁 Earn 5 coins per referral!\n"
            f"🔗 Your link:\n<code>{ref_link}</code>",
            parse_mode='HTML'
        )

# --- API Token Setter ---
async def set_api_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global api_token
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /api <new_token>")
        return

    api_token = context.args[0]
    await update.message.reply_text(f"✅ API token updated successfully:\n<code>{api_token}</code>", parse_mode="HTML")

# --- Handle Text Queries ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    query = update.message.text.strip()

    if uid not in user_credits:
        user_credits[uid] = 5

    coins = user_credits.get(uid, 0)
    if coins < 5:
        await update.message.reply_text(
            "💸 <b>INSUFFICIENT FUNDS!</b>\n"
            "Balance: 0 coins\n"
            "Required: 5 coins\n"
            "Use /start → Add Funds",
            parse_mode='HTML'
        )
        return

    searching_msg = await update.message.reply_text("🔍 Searching...")

    query = clean_input(query)

    try:
        payload = {
            "token": api_token,
            "request": query,
            "limit": 100,
            "lang": "ru"
        }
        r = requests.post(API_URL, json=payload, timeout=15)

        if r.status_code != 200 or not r.text.strip():
            await searching_msg.edit_text(
                "❌ <b>NO DATA FOUND</b>\nCredits not deducted.",
                parse_mode='HTML'
            )
            return

        response_text = r.text.strip()

        # Try JSON formatting
        try:
            data = r.json()
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                results = []
                for idx, item in enumerate(data["data"], start=1):
                    block = [f"📑 <b>Record {idx}</b>"]
                    if "email" in item:
                        block.append(f"📧 Email: <b>{item['email']}</b>")
                    if "password" in item:
                        block.append(f"🔑 Password: <code>{item['password']}</code>")
                    if "phone" in item:
                        block.append(f"📱 Phone: <b>{item['phone']}</b>")
                    if "username" in item:
                        block.append(f"👤 Username: <b>{item['username']}</b>")
                    results.append("\n".join(block))
                response_text = "\n\n".join(results)
            else:
                response_text = f"<code>{json.dumps(data, indent=2)}</code>"
        except:
            # Fallback plain text
            response_text = f"<code>{response_text}</code>"

        # Deduct coins only after success
        user_credits[uid] -= 5

        await searching_msg.edit_text(
            f"🎯 <b>RESULT FOUND</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"{response_text}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 Coins Left: <b>{user_credits[uid]}</b>",
            parse_mode='HTML'
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        await searching_msg.edit_text(
            "⚠️ <b>SEARCH FAILED</b>\nCredits not deducted.",
            parse_mode='HTML'
        )

# --- Add Coins (Admin) ---
async def addcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized")
        return

    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /addcoin <user_id> <amount>")
        return

    try:
        user_id = int(args[0])
        amount = int(args[1])
        user_credits[user_id] = user_credits.get(user_id, 0) + amount
        await update.message.reply_text(f"✅ Added {amount} coins to user {user_id}.")
        try:
            await context.bot.send_message(user_id, f"💰 You've received {amount} coins from admin. Balance: {user_credits[user_id]}")
        except:
            pass
    except:
        await update.message.reply_text("⚠️ Invalid input")

# --- Main ---
if __name__ == '__main__':
    print("✅ Bot is starting...")

    scheduler = AsyncIOScheduler(timezone=pytz.UTC)

    app = Application.builder().token(BOT_TOKEN).build()
    app.job_queue.scheduler = scheduler

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addcoin", addcoin))
    app.add_handler(CommandHandler("api", set_api_token))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    try:
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ Error: {e}")
