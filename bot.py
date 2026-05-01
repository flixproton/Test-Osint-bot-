import requests
import json
import time

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8744112471:AAEfdBHyA9HxSee6nSln1TYuD3h3_C60Blg"   # <-- put your bot token here
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

EXTERNAL_API = "https://osint-api.alphamovies.workers.dev/api/numinfo?key=flix9080&num="  # <-- leave blank or put your API base URL

# Admin ID (put your Telegram numeric ID)
ADMIN_ID = 7189814021

# In-memory storage
user_states = {}
banned_users = set()

# =========================
# HELPER FUNCTIONS
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

    response = requests.get(url, params=params)
    return response.json()


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
