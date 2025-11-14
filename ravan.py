#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Telegram account auto-poster using Telethon.
Posts a message to one or more groups every ~36 seconds (with small random jitter).
Also auto-forwards specific message (ID 4 from FreeAdultServiceApp) to new users in private chat, only once.
"""

import asyncio
import random
import signal
import sys
from telethon import TelegramClient, errors, events

# ---------- CONFIG (UPDATED CREDENTIALS) ----------
api_id = 33304437
api_hash = '235146410a3efc97bb2a711c43ce17d5'
phone_number = '+919895038308'  # <-- UPDATED PHONE NUMBER
# Two-step password: Shubh#@123 (You must enter this when prompted during first login)

# Provided group usernames:
TARGETS = [
    'friends_circle_1908',
    'worldwide_girl_chatting',
    'Friends_Chats_International',
    'bestfriend_Girls_Chatting_group',
    'openchatwithfriends', 
]
MESSAGE_TEXT = "Free servise applikation download kre profile se"
BASE_INTERVAL_SECONDS = 36  # Base 36s 
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


# --- Event Handler for Auto-Forward (Message ID 4 from FreeAdultServiceApp) ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_forward_handler(event):
    """Forwards specific message (ID 4 from FreeAdultServiceApp) to a new user only once."""
    global REPLIED_USERS
    sender = await event.get_sender()
    sender_id = sender.id

    # Check if this user has already received the reply
    if sender_id not in REPLIED_USERS:
        print(f"Received message from new user {sender_id}. Preparing auto-forward...")
        try:
            source_channel = 'FreeAdultServiceApp'
            message_id = 4
            
            # Fetch the message
            messages_to_forward = await client.get_messages(source_channel, ids=[message_id])
            
            # Get the single message 
            msg_4 = messages_to_forward[0] if messages_to_forward else None

            # Ensure the message is found and forward it
            if msg_4:
                # Forward it to the chat where the message came from
                await client.forward_messages(event.chat_id, msg_4)
                
                REPLIED_USERS.add(sender_id)
                print(f"Auto-forward complete. User {sender_id} added to replied list.")
            else:
                print(f"Error: Message ID {message_id} not found in {source_channel}.")


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
        