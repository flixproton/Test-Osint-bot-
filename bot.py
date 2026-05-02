import requests
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8744112471:AAEfdBHyA9HxSee6nSln1TYuD3h3_C60Blg"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
# The External API for lookups
EXTERNAL_API = "https://osint-api.alphamovies.workers.dev/api/numinfo"
ADMIN_ID = 7189814021

user_states = {}
banned_users = set()

# =========================
# DUMMY SERVER (FOR RENDER/HEROKU)
# =========================
def run_server():
    port = int(os.environ.get("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive!")
        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

# =========================
# TELEGRAM HELPER FUNCTIONS
# =========================
def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    try:
        res = requests.get(url, params=params)
        return res.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return {"result": []}

def phone_keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True
    }

def admin_keyboard():
    return {
        "keyboard": [[{"text": "📊 Status"}], [{"text": "🚫 Ban User"}]],
        "resize_keyboard": True
    }

def call_api(number):
    # Constructing the API URL
    url = f"{EXTERNAL_API}?key=flix9080&num={number}"
    try:
        res = requests.get(url, timeout=15)
        return res.json()
    except Exception as e:
        return {"error": "API failed or timed out", "details": str(e)}

# =========================
# MAIN BOT LOGIC
# =========================
def main():
    offset = None
    print("Bot loop started...")

    while True:
        updates = get_updates(offset)
        
        for update in updates.get("result", []):
            offset = update["update_id"] + 1
            if "message" not in update:
                continue

            msg = update["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            text = msg.get("text", "")

            # Security Check: Banned Users
            if user_id in banned_users:
                continue

            # --- COMMANDS ---
            if text == "/start":
                user_states[user_id] = None
                send_message(chat_id, "👋 Welcome! Click the button below to start searching.", phone_keyboard())

            elif text == "📱 Phone Lookup":
                user_states[user_id] = "WAIT_NUMBER"
                send_message(chat_id, "📞 Please send the **10-digit** mobile number:")

            # --- ADMIN COMMANDS ---
            elif user_id == ADMIN_ID and text == "/admin":
                send_message(chat_id, "🔐 Admin Panel Opened", admin_keyboard())

            elif user_id == ADMIN_ID and text == "📊 Status":
                send_message(chat_id, f"📊 **Bot Status**\nActive Users: {len(user_states)}\nBanned: {len(banned_users)}", parse_mode="Markdown")

            elif user_id == ADMIN_ID and text == "🚫 Ban User":
                user_states[user_id] = "BAN_INPUT"
                send_message(chat_id, "Enter the User ID you want to ban:")

            # --- STATE HANDLING (Inputs) ---
            elif user_states.get(user_id) == "WAIT_NUMBER":
                if text.isdigit() and len(text) >= 10:
                    send_message(chat_id, "🔍 Searching... please wait.")
                    
                    api_res = call_api(text)
                    # Formatting JSON response for Telegram
                    formatted_json = json.dumps(api_res, indent=2)
                    
                    send_message(chat_id, f"✅ **Results for {text}:**\n<pre>{formatted_json}</pre>", parse_mode="HTML")
                    user_states[user_id] = None # Reset state
                else:
                    send_message(chat_id, "❌ Invalid number. Please send a valid 10-digit number.")

            elif user_id == ADMIN_ID and user_states.get(user_id) == "BAN_INPUT":
                if text.isdigit():
                    banned_users.add(int(text))
                    send_message(chat_id, f"✅ User {text} has been banned.")
                else:
                    send_message(chat_id, "❌ Invalid ID.")
                user_states[user_id] = None

        time.sleep(1)

# =========================
# EXECUTION
# =========================
if __name__ == "__main__":
    # Start the dummy server in a separate thread
    threading.Thread(target=run_server, daemon=True).start()
    # Start the bot
    main()
