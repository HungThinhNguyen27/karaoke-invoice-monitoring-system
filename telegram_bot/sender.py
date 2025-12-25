import io


async def send_photo(bot, chat_id, img_bytes, caption):
    bio = io.BytesIO(img_bytes)
    bio.name = "image.png"
    await bot.send_photo(chat_id, bio, caption=caption, parse_mode="Markdown")


async def send_message(bot, chat_id, text):
    await bot.send_message(chat_id, text, parse_mode="Markdown")
