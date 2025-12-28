import io
from telegram.error import TimedOut, NetworkError


async def send_photo(bot, chat_id, img_bytes, caption):
    try:
        bio = io.BytesIO(img_bytes)
        bio.name = "image.png"
        await bot.send_photo(chat_id, bio, caption=caption, parse_mode="Markdown")
    except (TimedOut, NetworkError) as e:
        print(f"⚠️ Telegram send_photo timeout: {e}")


async def send_message(bot, chat_id, text):
    try:
        await bot.send_message(chat_id, text, parse_mode="Markdown")
    except (TimedOut, NetworkError) as e:
        print(f"⚠️ Telegram send_photo timeout: {e}")
