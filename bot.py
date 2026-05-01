import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8744112471:AAEfdBHyA9HxSee6nSln1TYuD3h3_C60Blg"   # डालो अपना token
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

EXTERNAL_API = "https://osint-api.alphamovies.workers.dev/api/numinfo?key=flix9080&num="  # optional

ADMIN_ID = 7189814021

user_states = {}
banned_users = set()

# =========================
# DUMMY SERVER (FOR RENDER)
# =========================
def run_server():
    port = int(os.environ.get("PORT", 10000))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot running")

        def do_HEAD(self):   # FIX for Render health check
            self.send_response(200)
            self.end_headers()

    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# =========================
# TELEGRAM FUNCTIONS
# =========================
def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{API_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    if parse_mode:
        payload["parse_mode"] = parse_mode

    requests.post(url, data=payload)


def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"

    params = {"timeout": 100}
    if offset:
        params["offset"] = offset

    res = requests.get(url, params=params)
    return res.json()


def phone_keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True
    }


def admin_keyboard():
    return {
        "keyboard": [
            [{"text": "📊 Status"}],
            [{"text": "🚫 Ban User"}]
        ],
        "resize_keyboard": True
    }


def is_valid_number(text):
    return text.isdigit() and len(text) == 10


def call_api(number):
    if EXTERNAL_API:
        url = f"{EXTERNAL_API}?num={number}&key={ADMIN_ID}"
    else:
        url = f"https://yash-code-with-ai.alphamovies.workers.dev/?num={number}&key={ADMIN_ID}"

    try:
        return requests.get(url).json()
    except:
        return {"error": "API failed"}


# =========================
# MAIN BOT
# =========================
def main():
    offset = None
    print("Bot started...")

    while True:
        try:
            data = get_updates(offset)

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                msg = update["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                if user_id in banned_users:
                    continue

                # START
                if text == "/start":
                    send_message(chat_id, "👋 Welcome!", phone_keyboard())

                # PHONE BUTTON
                elif text == "📱 Phone Lookup":
                    user_states[user_id] = "WAIT"
                    send_message(chat_id, "📞 Send 10 digit mobile number:")

                # NUMBER INPUT
                elif user_states.get(user_id) == "WAIT":
                    if is_valid_number(text):
                        send_message(chat_id, "🔍 Checking...")

                        result = call_api(text)
                        formatted = json.dumps(result, indent=4)

                        send_message(chat_id, f"<pre>{formatted}</pre>", parse_mode="HTML")
                        user_states[user_id] = None
                    else:
                        send_message(chat_id, "❌ Invalid number")

                # ADMIN
                elif user_id == ADMIN_ID and text == "/admin":
                    send_message(chat_id, "Admin Panel", admin_keyboard())

                elif user_id == ADMIN_ID and text == "📊 Status":
                    send_message(chat_id, f"Users: {len(user_states)}\nBanned: {len(banned_users)}")

                elif user_id == ADMIN_ID and text == "🚫 Ban User":
                    user_states[user_id] = "BAN"
                    send_message(chat_id, "Send user ID")

                elif user_id == ADMIN_ID and user_states.get(user_id) == "BAN":
                    if text.isdigit():
                        banned_users.add(int(text))
                        send_message(chat_id, "User banned")
                        user_states[user_id] = None
                    else:
                        send_message(chat_id, "Invalid ID")

        except Exception as e:
            print("Error:", e)

        time.sleep(1)


# =========================
# RUN BOTH
# =========================
if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    main()    return response.json()


def phone_keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True
    }


def admin_keyboard():
    return {
        "keyboard": [
            [{"text": "📊 Status"}],
            [{"text": "🚫 Ban User"}]
        ],
        "resize_keyboard": True
    }


def is_valid_number(text):
    return text.isdigit() and len(text) == 10


def call_external_api(number):
    # Works with or without key
    if EXTERNAL_API:
        url = f"{EXTERNAL_API}?num={number}&key={ADMIN_ID}"
    else:
        url = f"https://yash-code-with-ai.alphamovies.workers.dev/?num={number}&key={ADMIN_ID}"

    try:
        res = requests.get(url)
        return res.json()
    except:
        return {"error": "API request failed"}


# =========================
# MAIN BOT LOOP
# =========================
def main():
    offset = None

    print("Bot started...")

    while True:
        data = get_updates(offset)

        if "result" in data:
            for update in data["result"]:
                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]
                chat_id = message["chat"]["id"]
                user_id = message["from"]["id"]
                text = message.get("text", "")

                # Check banned
                if user_id in banned_users:
                    continue

                # =========================
                # START COMMAND
                # =========================
                if text == "/start":
                    send_message(
                        chat_id,
                        "👋 Welcome!\n\nUse the button below:",
                        reply_markup=phone_keyboard()
                    )

                # =========================
                # PHONE LOOKUP BUTTON
                # =========================
                elif text == "📱 Phone Lookup":
                    user_states[user_id] = "WAITING_NUMBER"
                    send_message(chat_id, "📞 Send 10 digit mobile number:")

                # =========================
                # HANDLE NUMBER INPUT
                # =========================
                elif user_states.get(user_id) == "WAITING_NUMBER":
                    if is_valid_number(text):
                        send_message(chat_id, "🔍 Fetching details...")

                        data = call_external_api(text)

                        formatted = json.dumps(data, indent=4)

                        send_message(
                            chat_id,
                            f"<pre>{formatted}</pre>",
                            parse_mode="HTML"
                        )

                        user_states[user_id] = None
                    else:
                        send_message(chat_id, "❌ Invalid number! Send 10 digit mobile number.")

                # =========================
                # ADMIN PANEL
                # =========================
                elif user_id == ADMIN_ID and text == "/admin":
                    send_message(
                        chat_id,
                        "🔐 Admin Panel",
                        reply_markup=admin_keyboard()
                    )

                elif user_id == ADMIN_ID and text == "📊 Status":
                    send_message(
                        chat_id,
                        f"📊 Bot Status\n\n👥 Users: {len(user_states)}\n🚫 Banned: {len(banned_users)}"
                    )

                elif user_id == ADMIN_ID and text == "🚫 Ban User":
                    user_states[user_id] = "BAN_MODE"
                    send_message(chat_id, "Send User ID to ban:")

                elif user_id == ADMIN_ID and user_states.get(user_id) == "BAN_MODE":
                    if text.isdigit():
                        banned_users.add(int(text))
                        send_message(chat_id, f"🚫 User {text} banned successfully.")
                        user_states[user_id] = None
                    else:
                        send_message(chat_id, "❌ Invalid User ID")

        time.sleep(1)


if __name__ == "__main__":
    main()
