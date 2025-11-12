#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Telegram account auto-poster using Telethon.
Posts a message to one or more groups every ~36 seconds (with small random jitter).
Also auto-forwards specific messages (ID 8 & 9 from FreeServiceApk) to new users in private chat, only once.

USAGE:
1) Replace phone_number with your number (including +country code).
2) Replace targets in TARGETS with group username (like 'mygroup') or numeric id (int).
3) Run: python auto_poster_account.py
4) First run will ask OTP in terminal.

SECURITY:
- Do NOT publish your session file or api_hash.
- If credentials leaked, rotate/revoke them at https://my.telegram.org
"""

import asyncio
import random
import signal
import sys
from telethon import TelegramClient, errors, events

# ---------- CONFIG (UPDATED TARGETS AND INTERVAL) ----------
api_id = 19612077
api_hash = '5b66d8462d913e8427339fbbe1bbd3a7'
phone_number = '+919821932773'  # <-- replace with your phone number (include +)
# Provided group usernames:
TARGETS = [
    'friends_circle_1908',
    'worldwide_girl_chatting',
    'Friends_Chats_International',
    'bestfriend_Girls_Chatting_group',
    'openchatwithfriends', 
]
MESSAGE_TEXT = "Free servise applikation download kre profile se"
BASE_INTERVAL_SECONDS = 36  # Base 36s (New speed as requested)
JITTER_SECONDS = 5         # random +/- jitter (0..5 seconds)
SESSION_NAME = 'me_session'  # session file: me_session.session
# ---------------------------------------------------------

client = TelegramClient(SESSION_NAME, api_id, api_hash)
stop_signal = False
REPLIED_USERS = set() # Stores IDs of users who have received the auto-forward

def handle_stop(sig, frame):
    global stop_signal
    print("\nReceived stop signal, shutting down...")
    stop_signal = True

signal.signal(signal.SIGINT, handle_stop)
signal.signal(signal.SIGTERM, handle_stop)


# --- New Event Handler for Auto-Forward ---
@client.on(events.NewMessage(incoming=True, private=True))
async def auto_forward_handler(event):
    """Forwards specific messages to a new user only once."""
    global REPLIED_USERS
    sender = await event.get_sender()
    sender_id = sender.id

    # Check if this user has already received the reply
    if sender_id not in REPLIED_USERS:
        print(f"Received message from new user {sender_id}. Preparing auto-forward...")
        try:
            source_channel = 'FreeServiceApk'
            message_ids = [8, 9]

            # Fetch the messages
            messages_to_forward = await client.get_messages(source_channel, ids=message_ids)
            
            # Forward them sequentially to the chat where the message came from
            msg_8 = next((m for m in messages_to_forward if m and m.id == 8), None)
            msg_9 = next((m for m in messages_to_forward if m and m.id == 9), None)

            # Ensure both messages are found and forward them
            if msg_8:
                await client.forward_messages(event.chat_id, msg_8)
            if msg_9:
                await client.forward_messages(event.chat_id, msg_9)
                
            REPLIED_USERS.add(sender_id)
            print(f"Auto-forward complete. User {sender_id} added to replied list.")

        except Exception as e:
            print(f"Error during auto-forward to {sender_id}: {e}. Will retry on next message.")


# --- Periodic Posting Task ---
async def post_messages_periodically(resolved_targets):
    """The main loop for periodic posting to groups."""
    global stop_signal
    
    while not stop_signal:
        for ent in resolved_targets:
            try:
                await client.send_message(ent, MESSAGE_TEXT)
                print(f"[{ent.id}] Message sent.")
            except errors.FloodWaitError as fw:
                print(f"Flood wait: sleeping {fw.seconds} seconds.")
                await asyncio.sleep(fw.seconds + 1)
            except Exception as e:
                print(f"Error sending to {ent}: {e}")
            # small pause between targets to avoid bursts
            await asyncio.sleep(1)

        # compute next interval with jitter
        jitter = random.uniform(-JITTER_SECONDS, JITTER_SECONDS)
        next_sleep = max(1, BASE_INTERVAL_SECONDS + jitter)
        print(f"Sleeping ~{next_sleep:.1f}s before next round...")
        await asyncio.sleep(next_sleep)


# --- Main Execution Setup ---
async def send_to_targets():
    """Sets up the client, resolves targets, and runs both posting and listener tasks."""
    await client.start(phone=phone_number)
    me = await client.get_me()
    print(f"Logged in as: {me.username or me.first_name} (id: {me.id})")

    # Resolve entities
    resolved = []
    for t in TARGETS:
        try:
            ent = await client.get_entity(t)
            resolved.append(ent)
            print(f"Resolved target: {getattr(ent, 'title', getattr(ent, 'username', ent.id))}")
        except Exception as e:
            print(f"⚠️ Could not resolve target '{t}': {e}")

    if not resolved:
        print("No valid targets resolved. Bot will run listeners only.")
    else:
        # Start the periodic posting as a background task
        asyncio.create_task(post_messages_periodically(resolved))

    # This keeps the client running, listening for events, and allows the background task to run
    await client.run_until_disconnected()
    print("Disconnected. Exiting.")


if __name__ == "__main__":
    try:
        asyncio.run(send_to_targets())
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting.")
        sys.exit(0)
        