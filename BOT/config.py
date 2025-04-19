from dotenv import load_dotenv
import os
import json

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TELEGRAM_IDS = []

# Load admin IDs from config and external file
try:
    with open("admin_log.json", "r", encoding="utf-8") as f:
        saved_admins = json.load(f)
        ADMIN_TELEGRAM_IDS = saved_admins.get("admins", [])
except Exception:
    ADMIN_TELEGRAM_IDS = []
