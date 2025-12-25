from pathlib import Path
from telegram import Bot

BOT_TOKEN = "7515004996:AAGgSqhtZmhwBmKg28tDxJR0GbxAMc7Rho4"
CHAT_ID = 724525798
# CHAT_ID = -5005964335 ##nhom chinh

PRN_FOLDER = Path("/Users/macos/Downloads/Coding Project/prn")
PNG_FOLDER = Path("/Users/macos/Downloads/Coding Project/prn/output_png")

PNG_FOLDER.mkdir(parents=True, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
