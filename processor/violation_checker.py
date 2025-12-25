from utils.text_utils import safe_int_from_currency
from state import TEMP_STORAGE, state_lock
from telegram_bot.sender import send_message
from config import bot, CHAT_ID


async def check_vi_pham(so_hd):
    with state_lock:
        hd = TEMP_STORAGE.get(so_hd)

    if not hd or "tam_tinh" not in hd or "thanh_toan" not in hd:
        return

    t1 = safe_int_from_currency(hd["tam_tinh"]["data"]["tien"])
    t2 = safe_int_from_currency(hd["thanh_toan"]["data"]["tien"])

    if t1 and t2 and t1 > t2:
        await send_message(
            bot,
            CHAT_ID,
            f"⚠️ *PHÁT HIỆN VI PHẠM*\nHĐ `{so_hd}`\nChênh lệch: *{t1 - t2:,} VNĐ*",
        )
