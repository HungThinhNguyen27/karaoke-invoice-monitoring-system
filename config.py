from pathlib import Path
from telegram import Bot
from telegram.request import HTTPXRequest

request = HTTPXRequest(
    connect_timeout=20,
    read_timeout=30,
    write_timeout=30,
    pool_timeout=20,
)

BOT_TOKEN = "7515004996:AAGgSqhtZmhwBmKg28tDxJR0GbxAMc7Rho4"
CHAT_ID = 724525798
# CHAT_ID = -5005964335 ##nhom chinh

BASE = Path("/Users/macos/Downloads/Coding Project/karaoke_bot/data_example")

PRN_FOLDER_TAMTINH = BASE / "prn_tamtinh"
PRN_FOLDER_THANHTOAN = BASE / "prn_thanhtoan"

PNG_FOLDER_TAMTINH = BASE / "png_tamtinh"
PNG_FOLDER_THANHTOAN = BASE / "png_thanhtoan"

for p in [
    PRN_FOLDER_TAMTINH,
    PRN_FOLDER_THANHTOAN,
    PNG_FOLDER_TAMTINH,
    PNG_FOLDER_THANHTOAN,
]:
    p.mkdir(parents=True, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
